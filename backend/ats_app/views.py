import logging
import threading

import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ats_app.agents.orchestrator import OrchestratorAgent
from ats_app.models import Job, ProcessRun, StageResult
from ats_app.serializers import (
    JobCreateSerializer,
    JobSerializer,
    ManualLatexSubmissionSerializer,
    ProcessRunCreateSerializer,
    ProcessRunSerializer,
    StageResultSerializer,
)

logger = logging.getLogger(__name__)


def _run_orchestrator_async(process_run_id, user_id=None):
    from django import db
    from django.contrib.auth.models import User
    db.connections.close_all()
    try:
        process_run = ProcessRun.objects.get(id=process_run_id)
        user = User.objects.get(id=user_id) if user_id else None
        orchestrator = OrchestratorAgent(user=user)
        orchestrator.start_process(process_run)
    except Exception as e:
        logger.error(f"Orchestrator failed for process {process_run_id}: {e}", exc_info=True)
        ProcessRun.objects.filter(id=process_run_id).update(status='failed')
    finally:
        db.connections.close_all()


def _resume_orchestrator_async(process_run_id):
    from django import db
    db.connections.close_all()
    try:
        process_run = ProcessRun.objects.get(id=process_run_id)
        orchestrator = OrchestratorAgent()
        orchestrator.resume_after_manual_input(process_run)
    except Exception as e:
        logger.error(f"Resume orchestrator failed for process {process_run_id}: {e}", exc_info=True)
        ProcessRun.objects.filter(id=process_run_id).update(status='failed')
    finally:
        db.connections.close_all()


def _restart_orchestrator_async(process_run_id):
    from django import db
    db.connections.close_all()
    try:
        process_run = ProcessRun.objects.get(id=process_run_id)
        orchestrator = OrchestratorAgent()
        orchestrator.restart_from_failure(process_run)
    except Exception as e:
        logger.error(f"Restart orchestrator failed for process {process_run_id}: {e}", exc_info=True)
        ProcessRun.objects.filter(id=process_run_id).update(status='failed')
    finally:
        db.connections.close_all()


class JobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        # Filter jobs by current user
        return Job.objects.prefetch_related('process_runs__stage_results').filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return JobCreateSerializer
        return JobSerializer

    @action(detail=True, methods=['post'])
    def run_process(self, request, pk=None):
        job = self.get_object()
        process_run = ProcessRun.objects.create(job=job, user=request.user)
        # Pass user ID to orchestrator thread
        user_id = request.user.id
        thread = threading.Thread(
            target=_run_orchestrator_async,
            args=(str(process_run.id), user_id),
            daemon=True,
        )
        thread.start()
        serializer = ProcessRunSerializer(process_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProcessRunViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProcessRunSerializer

    def get_queryset(self):
        # Filter process runs by current user
        return ProcessRun.objects.prefetch_related('stage_results').select_related('job').filter(user=self.request.user)

    @action(detail=True, methods=['get'])
    def get_prompt(self, request, pk=None):
        """
        Get the generated prompt from Agent 3 for manual LLM input.
        """
        process_run = self.get_object()
        
        try:
            # Get cv_update stage result safely
            try:
                cv_update_result = process_run.stage_results.get(stage='cv_update')
            except StageResult.DoesNotExist:
                cv_update_result = process_run.stage_results.filter(stage='cv_update').first()
            
            if not cv_update_result or not cv_update_result.result:
                return Response(
                    {'error': 'No prompt generated yet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            prompt = cv_update_result.result.get('prompt', '')
            if not prompt:
                return Response(
                    {'error': 'Prompt not found in result'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                'prompt': prompt,
                'iteration_number': cv_update_result.iteration_number,
                'max_iterations': process_run.max_iterations
            })
        
        except Exception as e:
            logger.error(f"Failed to get prompt for process {pk}: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def submit_manual_latex(self, request, pk=None):
        """
        Submit manually updated LaTeX from external LLM and continue process.
        """
        process_run = self.get_object()
        
        # Validate process is in the correct state
        if process_run.status != 'awaiting_manual_input':
            return Response(
                {'error': f'Process is not awaiting manual input. Current status: {process_run.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the input
        serializer = ManualLatexSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        latex_content = serializer.validated_data['latex_content']
        
        try:
            # Validate LaTeX structure
            from ats_app.agents.cv_updater import CVUpdaterAgent
            cv_updater = CVUpdaterAgent()
            validation_result = cv_updater.validate_manual_latex(latex_content)
            
            if not validation_result['valid']:
                return Response(
                    {'error': validation_result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save manual input
            process_run.manual_latex_input = latex_content
            process_run.save()
            
            # Resume's orchestrator in a background thread
            thread = threading.Thread(
                target=_resume_orchestrator_async,
                args=(str(process_run.id),),
                daemon=True,
            )
            thread.start()
            
            logger.info(f"Manual LaTeX submitted for process {pk}, resuming orchestrator")
            
            return Response({
                'message': 'LaTeX submitted successfully. Process is resuming...',
                'iteration': process_run.iteration_count
            })
        
        except Exception as e:
            logger.error(f"Failed to submit manual LaTeX for process {pk}: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def continue_iterating(self, request, pk=None):
        """
        Trigger a new manual iteration after process completion.
        """
        process_run = self.get_object()
        
        # Validate process is in completed state
        if process_run.status != 'completed':
            return Response(
                {'error': f'Process is not completed. Current status: {process_run.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if we can continue iterating
        if process_run.iteration_count >= process_run.max_iterations:
            return Response(
                {'error': f'Max iterations ({process_run.max_iterations}) reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from ats_app.agents.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            success = orchestrator.trigger_manual_iteration(process_run)
            
            if not success:
                return Response(
                    {'error': 'Failed to trigger manual iteration'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Refresh process run data
            process_run.refresh_from_db()
            
            serializer = ProcessRunSerializer(process_run)
            return Response({
                'message': 'New iteration triggered successfully',
                'process': serializer.data
            })
        
        except Exception as e:
            logger.error(f"Failed to continue iterating for process {pk}: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def restart(self, request, pk=None):
        """
        Restart a failed process from the point of failure.
        Preserves all completed stage results.
        """
        process_run = self.get_object()
        
        # Validate process is in failed state
        if process_run.status != 'failed':
            return Response(
                {'error': f'Process is not failed. Current status: {process_run.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Start orchestrator restart in a background thread
            thread = threading.Thread(
                target=_restart_orchestrator_async,
                args=(str(process_run.id),),
                daemon=True,
            )
            thread.start()
            
            logger.info(f"Restart triggered for failed process {pk}")
            
            return Response({
                'message': 'Process restarted successfully from failure point'
            })
        
        except Exception as e:
            logger.error(f"Failed to restart process {pk}: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def force_complete(self, request, pk=None):
        """
        Force complete a process without running any agents.
        Saves manual LaTeX input to job if available.
        """
        process_run = self.get_object()
        
        try:
            # If manual LaTeX input exists, save it to job
            if process_run.manual_latex_input:
                process_run.job.latex_cv = process_run.manual_latex_input
                process_run.job.save(update_fields=['latex_cv'])
            
            # Update status to completed
            process_run.status = 'completed'
            process_run.save(update_fields=['status'])
            
            logger.info(f"Process {pk} force-completed by user (agent execution bypassed)")
            
            serializer = ProcessRunSerializer(process_run)
            return Response({
                'message': 'Process force-completed successfully',
                'process': serializer.data
            })
        
        except Exception as e:
            logger.error(f"Failed to force complete process {pk}: {e}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StageResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StageResult.objects.select_related('process_run__job').all()
    serializer_class = StageResultSerializer
