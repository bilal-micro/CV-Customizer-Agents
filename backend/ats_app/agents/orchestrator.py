import json
import logging

from ats_app.agents.keyword_extractor import KeywordExtractorAgent
from ats_app.agents.cv_matcher import CVMatcherAgent
from ats_app.agents.cv_updater import CVUpdaterAgent
from ats_app.agents.ats_rater import ATSRaterAgent
from ats_app.models import Job, ProcessRun, StageResult, UserProfile
from ats_app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ProcessCancelledException(Exception):
    """Raised when a process has been cancelled by the user."""
    pass

STAGE_ORDER = [
    'keyword_extraction',
    'cv_matching',
    'cv_update',
    'ats_rating',
]


class OrchestratorAgent:
    """
    Simplified orchestrator for CV optimization workflow.
    
    Flow:
    1. Extract keywords (one-time)
    2. Initial CV matching (one-time)
    3. Iteration loop (max 3):
       a. Generate prompt for external LLM
       b. Wait for manual input
       c. Re-match CV with new LaTeX
       d. Rate CV with ATS analysis
       e. Evaluate and continue or finish
    """
    
    def __init__(self, user=None):
        self.user = user
        
        # Validate user profile and get configuration
        api_key = None
        model = None
        
        if user:
            try:
                profile = user.profile
                api_key = profile.openrouter_api_key
                model = profile.preferred_model
                
                # Validate that required fields are present
                if not api_key or not api_key.strip():
                    raise ValueError(
                        "OpenRouter API key is required. Please update your profile with your API key. "
                        "Get your API key from https://openrouter.ai/keys"
                    )
                if not model or not model.strip():
                    raise ValueError(
                        "OpenRouter model is required. Please update your profile with your preferred model. "
                        "Available models at https://openrouter.ai/models"
                    )
                
                logger.info(f"OrchestratorAgent: Using user-specific configuration for {user.username}")
            except UserProfile.DoesNotExist:
                raise ValueError(
                    f"User profile not found for {user.username}. Please complete your registration or "
                    "contact support."
                )
            except Exception as e:
                logger.error(f"OrchestratorAgent: Error loading user profile: {e}")
                raise ValueError(
                    f"Error loading user profile: {str(e)}. Please update your profile."
                )
        else:
            raise ValueError(
                "User is required to initialize OrchestratorAgent. Please provide a valid user."
            )
        
        # Initialize LLM service with user configuration
        self.llm_service = LLMService(api_key=api_key, model=model)
        
        # Initialize agents with user-specific LLM service
        self.keyword_extractor = KeywordExtractorAgent(llm_service=self.llm_service)
        self.cv_matcher = CVMatcherAgent(include_advanced_analysis=True, llm_service=self.llm_service)
        self.cv_updater = CVUpdaterAgent()
        self.ats_rater = ATSRaterAgent(llm_service=self.llm_service)
        
        logger.info("OrchestratorAgent initialized")
    
    def start_process(self, process_run: ProcessRun) -> None:
        """
        Start a new CV optimization process.
        
        This is the main entry point that handles the entire workflow.
        """
        logger.info(f"OrchestratorAgent: Starting process {process_run.id}")
        
        try:
            # Set status to running
            process_run.status = 'running'
            process_run.save()
            
            # Get job data
            job = process_run.job
            latex_cv = job.latex_cv
            
            # Save original latex for comparison
            if not process_run.original_latex:
                process_run.original_latex = job.latex_cv
                process_run.save()
            
            # ============================================================================
            # ONE-TIME SETUP: Keyword Extraction and Initial Matching
            # ============================================================================
            logger.info("OrchestratorAgent: ===== PHASE 1: INITIAL ANALYSIS =====")
            
            # Stage 1: Extract keywords
            self._check_if_cancelled(process_run)
            keywords = self._execute_keyword_extraction(process_run, job)
            if not keywords:
                self._fail_process(process_run, "Keyword extraction failed")
                return
            
            # Stage 2: Initial CV matching
            self._check_if_cancelled(process_run)
            match_result = self._execute_cv_matching(process_run, job, keywords, latex_cv)
            if not match_result:
                self._fail_process(process_run, "Initial CV matching failed")
                return
            
            # ============================================================================
            # ITERATION LOOP: CV Optimization
            # ============================================================================
            self._check_if_cancelled(process_run)
            logger.info("OrchestratorAgent: ===== PHASE 2: ITERATIVE OPTIMIZATION =====")
            
            # Start iteration loop
            self._run_iteration_loop(process_run, job, keywords, latex_cv)
            
        except ProcessCancelledException:
            logger.info(f"OrchestratorAgent: Process {process_run.id} cancelled during start_process")
            # Don't change status - it's already 'cancelled'
        except Exception as e:
            logger.error(f"OrchestratorAgent: Process failed: {e}", exc_info=True)
            self._fail_process(process_run, str(e))
    
    def _run_iteration_loop(self, process_run: ProcessRun, job: Job, 
                           keywords: dict, current_latex: str) -> None:
        """
        Run the iteration loop for CV optimization.
        
        Args:
            process_run: The process run
            job: The job object
            keywords: Extracted keywords
            current_latex: Current LaTeX CV
        """
        max_iterations = process_run.max_iterations
        
        for iteration in range(1, max_iterations + 1):
            logger.info(f"OrchestratorAgent: ----- Iteration {iteration}/{max_iterations} -----")
            
            # Increment iteration count
            process_run.iteration_count = iteration
            process_run.save()
            
            # ========================================================================
            # Step 1: Generate prompt for external LLM
            # ========================================================================
            logger.info(f"OrchestratorAgent: [{iteration}] Generating prompt for external LLM")
            prompt = self._execute_cv_update_stage(
                process_run, job, keywords, current_latex
            )
            
            if not prompt:
                logger.error(f"OrchestratorAgent: [{iteration}] Failed to generate prompt")
                self._fail_process(process_run, "Prompt generation failed")
                return
            
            # ========================================================================
            # Step 2: Pause and wait for manual input
            # ========================================================================
            logger.info(f"OrchestratorAgent: [{iteration}] Pausing for manual input")
            process_run.status = 'awaiting_manual_input'
            process_run.save()
            
            # Exit here - process will resume when user submits manual input
            logger.info(f"OrchestratorAgent: Process {process_run.id} paused, awaiting input")
            return
    
    def resume_after_manual_input(self, process_run: ProcessRun) -> None:
        """
        Resume process after user has submitted manual LaTeX input.
        
        This is called when the user provides updated LaTeX from external LLM.
        """
        logger.info(f"OrchestratorAgent: Resuming process {process_run.id} after manual input")
        
        try:
            # Set status back to running
            process_run.status = 'running'
            process_run.save()
            
            # Get data
            job = process_run.job
            new_latex = process_run.manual_latex_input
            keyword_stage = self._get_stage_result_safely(process_run, 'keyword_extraction')
            if not keyword_stage:
                self._fail_process(process_run, "Keyword extraction stage not found")
                return
            
            # Ensure keywords is a dict (sometimes LLM returns list)
            keywords = keyword_stage.result
            if isinstance(keywords, list):
                logger.warning(f"OrchestratorAgent: Keywords returned as list, converting to dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            elif not isinstance(keywords, dict):
                logger.error(f"OrchestratorAgent: Keywords is {type(keywords)}, expected dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            current_iteration = process_run.iteration_count
            
            # ========================================================================
            # Step 1: Re-run CV matching with updated LaTeX
            # ========================================================================
            self._check_if_cancelled(process_run)
            logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Re-matching CV")
            match_result = self._execute_cv_matching(
                process_run, job, keywords, new_latex
            )
            
            if not match_result:
                self._fail_process(process_run, "CV matching failed")
                return
            
            # ========================================================================
            # Step 2: Run ATS rating on new LaTeX
            # ========================================================================
            self._check_if_cancelled(process_run)
            logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Rating CV with ATS")
            rating_result = self._execute_ats_rating(
                process_run, job, new_latex, match_result
            )
            
            if not rating_result:
                self._fail_process(process_run, "ATS rating failed")
                return
            
            # ========================================================================
            # Step 3: Evaluate results and decide next action
            # ========================================================================
            logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Evaluating results")
            evaluation = self._evaluate_results(match_result, rating_result)
            
            # Update job with the new LaTeX
            job.latex_cv = new_latex
            job.save(update_fields=['latex_cv'])
            
            # ========================================================================
            # Step 4: Decide - continue or finish?
            # ========================================================================
            if evaluation['meets_criteria']:
                # Success criteria met - finish
                logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Criteria met, completing")
                self._complete_process(process_run, "CV meets criteria")
                return
            
            elif current_iteration >= process_run.max_iterations:
                # Max iterations reached - finish
                logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Max iterations reached, completing")
                self._complete_process(process_run, "Max iterations reached")
                return
            
            else:
                # Need improvement - continue to next iteration
                logger.info(f"OrchestratorAgent: [Resume {current_iteration}] Need improvement, continuing")
                
                # Prepare feedback for next iteration
                feedback = self._prepare_feedback_for_next_iteration(
                    process_run, rating_result, match_result, evaluation
                )
                
                # Continue to next iteration
                self._continue_to_next_iteration(
                    process_run, job, keywords, new_latex, feedback
                )
        
        except ProcessCancelledException:
            logger.info(f"OrchestratorAgent: Process {process_run.id} cancelled during resume")
            # Don't change status - it's already 'cancelled'
        except Exception as e:
            logger.error(f"OrchestratorAgent: Resume failed: {e}", exc_info=True)
            self._fail_process(process_run, str(e))
    
    def _continue_to_next_iteration(self, process_run: ProcessRun, job: Job,
                                  keywords: dict, latex_cv: str, feedback: dict) -> None:
        """
        Continue to the next iteration with feedback.
        
        Args:
            process_run: The process run
            job: The job object
            keywords: Extracted keywords
            latex_cv: Current LaTeX CV
            feedback: Feedback for next iteration
        """
        try:
            # Increment iteration count
            next_iteration = process_run.iteration_count + 1
            process_run.iteration_count = next_iteration
            process_run.save()
            
            logger.info(f"OrchestratorAgent: Preparing iteration {next_iteration}/{process_run.max_iterations}")
            
            # Generate prompt with feedback
            prompt = self._execute_cv_update_stage(
                process_run, job, keywords, latex_cv, next_iteration, feedback
            )
            
            if not prompt:
                self._fail_process(process_run, "Prompt generation failed")
                return
            
            # Set status to awaiting manual input
            process_run.status = 'awaiting_manual_input'
            process_run.save()
            
            logger.info(f"OrchestratorAgent: Iteration {next_iteration} ready, awaiting input")
            
        except Exception as e:
            logger.error(f"OrchestratorAgent: Continue iteration failed: {e}", exc_info=True)
            self._fail_process(process_run, str(e))
    
    # ==========================================================================
    # STAGE EXECUTION METHODS
    # ==========================================================================
    
    def _execute_keyword_extraction(self, process_run: ProcessRun, job: Job) -> dict:
        """Execute keyword extraction stage."""
        return self._execute_stage(
            process_run, 'keyword_extraction',
            lambda: self.keyword_extractor.run(job.title, job.description)
        )
    
    def _execute_cv_matching(self, process_run: ProcessRun, job: Job,
                           keywords: dict, latex_cv: str) -> dict:
        """Execute CV matching stage."""
        return self._execute_stage(
            process_run, 'cv_matching',
            lambda: self.cv_matcher.run(job.title, keywords, latex_cv)
        )
    
    def _execute_cv_update_stage(self, process_run: ProcessRun, job: Job,
                                keywords: dict, latex_cv: str,
                                iteration: int = 1, feedback: dict = None) -> str:
        """
        Execute CV update stage (generate prompt).
        
        Returns:
            Generated prompt string or None if failed
        """
        stage_result = self._get_or_create_stage(process_run, 'cv_update')
        stage_result.status = 'running'
        stage_result.iteration_number = iteration
        stage_result.save()
        
        try:
            # Get cv_matching stage result safely
            cv_matching_stage = self._get_stage_result_safely(process_run, 'cv_matching')
            if not cv_matching_stage:
                logger.error(f"CV matching stage not found for process {process_run.id}")
                raise Exception("CV matching stage not found")
            
            # Generate prompt
            prompt = self.cv_updater.generate_prompt(
                job_title=job.title,
                keywords=keywords,
                matching_analysis=cv_matching_stage.result,
                latex_cv=latex_cv,
                iteration_number=iteration,
                feedback=feedback
            )
            
            # Save result
            result = {
                'prompt': prompt,
                'iteration_number': iteration,
                'update_notes': f'Prompt generated for iteration {iteration}'
            }
            
            stage_result.result = result
            stage_result.rating = 100.0
            stage_result.notes = result['update_notes']
            stage_result.status = 'completed'
            stage_result.save()
            
            logger.info(f"OrchestratorAgent: CV update stage completed - iteration {iteration}")
            return prompt
            
        except Exception as e:
            logger.error(f"OrchestratorAgent: CV update stage failed: {e}", exc_info=True)
            stage_result.result = {"error": str(e)}
            stage_result.status = 'failed'
            stage_result.save()
            return None
    
    def _execute_ats_rating(self, process_run: ProcessRun, job: Job,
                           latex_cv: str, match_result: dict) -> dict:
        """Execute ATS rating stage."""
        return self._execute_stage(
            process_run, 'ats_rating',
            lambda: self.ats_rater.run(
                job.title, job.description, latex_cv, 
                match_result.get('match_rate', 0.0)
            )
        )
    
    def _execute_stage(self, process_run: ProcessRun, stage_name: str,
                     stage_func) -> dict:
        """
        Execute a single stage with retry logic.
        
        Args:
            process_run: The process run
            stage_name: Name of the stage
            stage_func: Function to execute that returns a dict
            
        Returns:
            Stage result or None if failed
        """
        stage_result = self._get_or_create_stage(process_run, stage_name)
        stage_result.status = 'running'
        stage_result.save()
        
        retry_count = 0
        max_retries = process_run.max_retries
        
        while retry_count <= max_retries:
            try:
                # Execute stage
                result = stage_func()
                
                # Calculate rating
                rating = self._rate_stage_result(stage_name, result)
                needs_retry = self._should_retry_stage(stage_name, result)
                
                # Save result
                stage_result.result = result
                stage_result.rating = rating
                stage_result.notes = self._get_stage_notes(stage_name, result)
                
                if needs_retry and retry_count < max_retries:
                    retry_count += 1
                    process_run.retry_count = max(process_run.retry_count, retry_count)
                    process_run.save()
                    logger.info(f"OrchestratorAgent: Retrying stage {stage_name}, attempt {retry_count}")
                    continue
                
                stage_result.status = 'completed' if not result.get("error") else 'failed'
                stage_result.save()
                return result
                
            except Exception as e:
                logger.error(f"OrchestratorAgent: Stage {stage_name} attempt {retry_count} failed: {e}")
                result = {"error": str(e)}
                
                retry_count += 1
                if retry_count > max_retries:
                    stage_result.result = result
                    stage_result.status = 'failed'
                    stage_result.save()
                    return None
        
        return None
    
    # ==========================================================================
    # EVALUATION METHODS
    # ==========================================================================
    
    def _evaluate_results(self, match_result: dict, rating_result: dict) -> dict:
        """
        Evaluate if results meet completion criteria.
        
        Criteria: ATS score >= 80 AND match rate >= 75
        """
        ats_score = rating_result.get('ats_score', 0.0)
        match_rate = match_result.get('match_rate', 0.0)
        
        meets_criteria = ats_score >= 80.0 and match_rate >= 75.0
        
        logger.info(f"OrchestratorAgent: Evaluation - ATS: {ats_score}, Match: {match_rate}, "
                   f"Meets criteria: {meets_criteria}")
        
        return {
            'ats_score': ats_score,
            'match_rate': match_rate,
            'meets_criteria': meets_criteria,
            'reason': (f"Meets criteria: ATS >= 80 and Match >= 75" 
                      if meets_criteria else 
                      f"Needs improvement: ATS < 80 or Match < 75")
        }
    
    def _prepare_feedback_for_next_iteration(self, process_run: ProcessRun, rating_result: dict,
                                         match_result: dict, 
                                         evaluation: dict) -> dict:
        """
        Prepare feedback for the next iteration.
        """
        ats_breakdown = rating_result.get('ats_breakdown', {})
        
        feedback = {
            'ats_score': rating_result.get('ats_score', 0.0),
            'match_rate': match_result.get('match_rate', 0.0),
            'recruiter_appeal': rating_result.get('recruiter_appeal', 0.0),
            'weak_points': rating_result.get('weak_points', []),
            'strong_points': rating_result.get('strong_points', []),
            'improvement_suggestions': rating_result.get('improvement_suggestions', []),
            'overall_assessment': rating_result.get('overall_assessment', ''),
            'ats_breakdown': ats_breakdown,
            'notes': evaluation.get('reason', '')
        }
        
        # Save feedback to cv_update stage
        cv_update_stage = self._get_stage_result_safely(process_run, 'cv_update')
        if cv_update_stage:
            cv_update_stage.manual_feedback = json.dumps(feedback, indent=2)
            cv_update_stage.save()
        
        logger.info(f"OrchestratorAgent: Prepared feedback for next iteration")
        return feedback
    
    # ==========================================================================
    # CANCELLATION CHECK
    # ==========================================================================
    
    def _check_if_cancelled(self, process_run: ProcessRun) -> None:
        """
        Check if the process has been cancelled by the user.
        Raises ProcessCancelledException if cancelled, allowing the orchestrator
        to gracefully stop execution.
        """
        # Refresh from DB to get the latest status
        fresh_status = ProcessRun.objects.filter(id=process_run.id).values_list('status', flat=True).first()
        if fresh_status == 'cancelled':
            logger.info(f"OrchestratorAgent: Process {process_run.id} has been cancelled, stopping execution")
            raise ProcessCancelledException(f"Process {process_run.id} was cancelled by user")
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def _get_stage_result_safely(self, process_run: ProcessRun, stage_name: str):
        """
        Get stage result safely, handling different QuerySet states.
        
        Args:
            process_run: The process run
            stage_name: Name of the stage to retrieve
            
        Returns:
            StageResult object or None if not found
        """
        try:
            # Try standard Django get (works with unique_together)
            return process_run.stage_results.get(stage=stage_name)
        except StageResult.DoesNotExist:
            logger.warning(f"Stage {stage_name} not found for process {process_run.id}")
            return None
        except AttributeError as e:
            # Fallback if stage_results is list-like or not a proper manager
            logger.warning(f"Using fallback for {stage_name}: {e}")
            try:
                # Try filter approach
                return process_run.stage_results.filter(stage=stage_name).first()
            except Exception as e2:
                logger.error(f"Fallback also failed for {stage_name}: {e2}")
                return None
    
    def _get_or_create_stage(self, process_run: ProcessRun, stage_name: str) -> StageResult:
        """Get or create stage result."""
        stage_result, _ = StageResult.objects.get_or_create(
            process_run=process_run,
            stage=stage_name,
        )
        return stage_result
    
    def _should_retry_stage(self, stage: str, result: dict) -> bool:
        """Determine if stage should be retried."""
        if result.get("parse_error"):
            return True
        if stage == "keyword_extraction":
            return not result.get("hard_skills") and not result.get("keywords")
        if stage == "cv_matching":
            return result.get("match_rate") is None
        if stage == "cv_update":
            return not result.get("prompt")
        if stage == "ats_rating":
            return result.get("ats_score") is None
        return False
    
    def _rate_stage_result(self, stage: str, result: dict) -> float:
        """Calculate rating for stage result."""
        if result.get("parse_error"):
            return 0.0
        if stage == "keyword_extraction":
            return min(len(result.get("hard_skills", [])) + len(result.get("keywords", [])), 20) / 20 * 100
        if stage == "cv_matching":
            return result.get("match_rate", 0.0)
        if stage == "cv_update":
            return 100.0 if result.get("prompt") else 30.0
        if stage == "ats_rating":
            return result.get("ats_score", 0.0)
        return 50.0
    
    def _get_stage_notes(self, stage: str, result: dict) -> str:
        """Get notes for stage result."""
        if stage == "keyword_extraction":
            return result.get("job_notes", "")
        if stage == "cv_matching":
            return result.get("matching_notes", "")
        if stage == "cv_update":
            return result.get("update_notes", "")
        if stage == "ats_rating":
            return result.get("overall_assessment", "")
        return ""
    
    def _complete_process(self, process_run: ProcessRun, reason: str) -> None:
        """Mark process as completed."""
        process_run.status = 'completed'
        process_run.save()
        logger.info(f"OrchestratorAgent: Process {process_run.id} completed - {reason}")
    
    def trigger_manual_iteration(self, process_run: ProcessRun) -> bool:
        """
        Trigger a manual iteration after process completion.
        Used when user wants to continue iterating after max iterations.
        """
        try:
            # Reset status to continue iterating
            process_run.status = 'running'
            process_run.save()
            
            # Get job and keywords
            job = process_run.job
            keyword_stage = self._get_stage_result_safely(process_run, 'keyword_extraction')
            if not keyword_stage:
                self._fail_process(process_run, "Keyword extraction stage not found")
                return False
            
            # Ensure keywords is a dict (sometimes LLM returns list)
            keywords = keyword_stage.result
            if isinstance(keywords, list):
                logger.warning(f"OrchestratorAgent: Keywords returned as list in manual iteration, converting to dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            elif not isinstance(keywords, dict):
                logger.error(f"OrchestratorAgent: Keywords is {type(keywords)} in manual iteration, expected dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            
            current_latex = process_run.manual_latex_input or job.latex_cv
            
            # Increase max iterations by 1
            process_run.max_iterations += 1
            process_run.save()
            
            # Continue iteration loop
            self._continue_to_next_iteration(
                process_run, job, keywords, current_latex, 
                feedback={'reason': 'User requested additional iteration'}
            )
            
            logger.info(f"OrchestratorAgent: Manual iteration triggered for process {process_run.id}")
            return True
            
        except Exception as e:
            logger.error(f"OrchestratorAgent: Failed to trigger manual iteration: {e}", exc_info=True)
            process_run.status = 'failed'
            process_run.save()
            return False
    
    def _fail_process(self, process_run: ProcessRun, reason: str) -> None:
        """Mark process as failed."""
        process_run.status = 'failed'
        process_run.save()
        logger.error(f"OrchestratorAgent: Process {process_run.id} failed - {reason}")
    
    def restart_from_failure(self, process_run: ProcessRun) -> None:
        """
        Restart process from the failed stage, preserving completed results.
        
        This method identifies which stage failed and restarts execution from that point,
        keeping all previously completed stage results intact.
        """
        logger.info(f"OrchestratorAgent: Restarting failed process {process_run.id}")
        
        try:
            # Find the failed stage
            failed_stage = None
            stage_order = ['keyword_extraction', 'cv_matching', 'cv_update', 'ats_rating']
            
            for stage in stage_order:
                stage_result = self._get_stage_result_safely(process_run, stage)
                if stage_result and stage_result.status == 'failed':
                    failed_stage = stage
                    break
            
            # If all stages are completed, just mark process as completed
            if not failed_stage:
                all_completed = all(
                    self._get_stage_result_safely(process_run, stage) and 
                    self._get_stage_result_safely(process_run, stage).status == 'completed'
                    for stage in stage_order
                )
                
                if all_completed:
                    logger.info(f"OrchestratorAgent: All stages completed, marking process {process_run.id} as completed")
                    self._complete_process(process_run, "All stages completed successfully")
                else:
                    self._fail_process(process_run, "No failed stage found and not all stages completed")
                return
            
            logger.info(f"OrchestratorAgent: Failed stage identified: {failed_stage}")
            
            # Validate previous stages are completed
            for stage in stage_order:
                if stage == failed_stage:
                    break
                stage_result = self._get_stage_result_safely(process_run, stage)
                if not stage_result or stage_result.status != 'completed':
                    self._fail_process(process_run, f"Previous stage {stage} not completed")
                    return
            
            # Reset failed and subsequent stages to pending
            reset_started = False
            for stage in stage_order:
                if stage == failed_stage:
                    reset_started = True
                if reset_started:
                    stage_result = self._get_stage_result_safely(process_run, stage)
                    if stage_result:
                        stage_result.status = 'pending'
                        stage_result.save()
                        logger.info(f"OrchestratorAgent: Reset stage {stage} to pending")
            
            # Set status to running
            process_run.status = 'running'
            process_run.save()
            
            # Get job data
            job = process_run.job
            keyword_stage = self._get_stage_result_safely(process_run, 'keyword_extraction')
            
            # Ensure keywords is a dict (sometimes LLM returns list)
            keywords = keyword_stage.result if keyword_stage else {}
            if isinstance(keywords, list):
                logger.warning(f"OrchestratorAgent: Keywords returned as list in restart, converting to dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            elif not isinstance(keywords, dict):
                logger.error(f"OrchestratorAgent: Keywords is {type(keywords)} in restart, expected dict")
                keywords = {'hard_skills': [], 'soft_skills': [], 'keywords': []}
            
            current_latex = process_run.manual_latex_input or job.latex_cv
            
            # Execute based on which stage failed
            if failed_stage == 'keyword_extraction':
                # Restart from beginning
                logger.info("OrchestratorAgent: Restarting from keyword_extraction")
                self.start_process(process_run)
            elif failed_stage == 'cv_matching':
                # Restart CV matching with existing keywords
                logger.info("OrchestratorAgent: Restarting from cv_matching")
                match_result = self._execute_cv_matching(process_run, job, keywords, job.latex_cv)
                if not match_result:
                    self._fail_process(process_run, "CV matching failed on restart")
                    return
                # Continue to iteration loop
                self._run_iteration_loop(process_run, job, keywords, job.latex_cv)
            elif failed_stage == 'cv_update':
                # Restart prompt generation
                logger.info("OrchestratorAgent: Restarting from cv_update")
                self._run_iteration_loop(process_run, job, keywords, current_latex)
            elif failed_stage == 'ats_rating':
                # Resume after manual input (re-run ATS rating)
                logger.info("OrchestratorAgent: Restarting from ats_rating")
                self.resume_after_manual_input(process_run)
            
            logger.info(f"OrchestratorAgent: Process {process_run.id} restarted successfully")
            
        except Exception as e:
            logger.error(f"OrchestratorAgent: Restart failed for process {process_run.id}: {e}", exc_info=True)
            self._fail_process(process_run, str(e))
