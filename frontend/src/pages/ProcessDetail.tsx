import { useCallback, useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getProcessRun, getJob, getPrompt, submitManualLatex, continueIterating, restartProcess, forceComplete } from '../api';
import ProcessTracker from '../components/ProcessTracker';
import type { ProcessRun, Job } from '../types';

export default function ProcessDetail() {
  const { id } = useParams<{ id: string }>();
  const [processRun, setProcessRun] = useState<ProcessRun | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [prompt, setPrompt] = useState<string>('');
  const [manualLatex, setManualLatex] = useState<string>('');
  const [promptLoading, setPromptLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [continuing, setContinuing] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [forceCompleting, setForceCompleting] = useState(false);
  const [error, setError] = useState<string>('');

  const fetchData = useCallback(async () => {
    if (!id) return;
    try {
      const run = await getProcessRun(id);
      setProcessRun(run);
      const jobData = await getJob(run.job);
      setJob(jobData);
      
      // Clear error state if process is completed or running
      if (run.status === 'completed' || run.status === 'running' || run.status === 'awaiting_manual_input') {
        setError('');
      }
    } catch (error) {
      console.error('Failed to fetch process:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  const isActive = processRun?.status === 'running' || processRun?.status === 'pending';
  const isAwaitingInput = processRun?.status === 'awaiting_manual_input';

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!isActive && !isAwaitingInput) return;
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [isActive, isAwaitingInput, fetchData]);

  // Fetch prompt when awaiting manual input
  useEffect(() => {
    if (isAwaitingInput && id && !prompt) {
      fetchPrompt();
    }
  }, [isAwaitingInput, id, prompt]);

  const fetchPrompt = async () => {
    if (!id) return;
    setPromptLoading(true);
    setError('');
    try {
      const data = await getPrompt(id);
      setPrompt(data.prompt);
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to fetch prompt');
      console.error('Failed to fetch prompt:', error);
    } finally {
      setPromptLoading(false);
    }
  };

  const handleCopy = useCallback(async () => {
    if (prompt) {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [prompt]);

  const handleSubmitLatex = async () => {
    if (!id || !manualLatex.trim()) {
      setError('Please enter the updated LaTeX code');
      return;
    }

    setSubmitting(true);
    setError('');
    try {
      await submitManualLatex(id, manualLatex);
      setManualLatex('');
      setPrompt('');
      await fetchData();
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to submit LaTeX');
      console.error('Failed to submit LaTeX:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleContinueIterating = async () => {
    if (!id) return;

    setContinuing(true);
    setError('');
    try {
      await continueIterating(id);
      await fetchData();
      setPrompt('');
      // The process will now be in 'awaiting_manual_input' state
      // So fetch the prompt
      await fetchPrompt();
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to continue iterating');
      console.error('Failed to continue iterating:', error);
    } finally {
      setContinuing(false);
    }
  };

  const handleRestart = async () => {
    if (!id) return;

    setRestarting(true);
    setError('');
    try {
      await restartProcess(id);
      await fetchData();
      setPrompt('');
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to restart process');
      console.error('Failed to restart process:', error);
    } finally {
      setRestarting(false);
    }
  };

  const handleForceComplete = async () => {
    if (!id) return;

    const confirmed = window.confirm(
      `Are you sure you want to force complete this process?\n\n` +
      `This will:\n` +
      `- Mark the process as completed\n` +
      `- Save your manual LaTeX input (if available)\n` +
      `- Bypass all remaining agent executions\n` +
      `- You will not be able to resume or continue iterating\n\n` +
      `This action cannot be undone.\n\n` +
      `Proceed with force completion?`
    );

    if (!confirmed) return;

    setForceCompleting(true);
    setError('');
    try {
      await forceComplete(id);
      await fetchData();
    } catch (error: any) {
      setError(error.response?.data?.error || 'Failed to force complete process');
      console.error('Failed to force complete process:', error);
    } finally {
      setForceCompleting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'running': return '🔄';
      case 'awaiting_manual_input': return '⏸️';
      case 'failed': return '❌';
      case 'pending': return '⏳';
      default: return '📊';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'var(--success)';
      case 'running': return 'var(--primary)';
      case 'awaiting_manual_input': return '#f59e0b';
      case 'failed': return 'var(--error)';
      case 'pending': return 'var(--text-light)';
      default: return 'var(--text)';
    }
  };

  if (loading) {
    return (
      <div className="loading-container animate-fade-in">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading process details...</div>
      </div>
    );
  }

  if (!processRun) {
    return (
      <div className="empty-state animate-fade-in">
        <div className="empty-state-icon">🔍</div>
        <div className="empty-state-text">Process not found</div>
        <div className="empty-state-subtext">
          The process you're looking for doesn't exist or has been deleted
        </div>
        <Link to="/history" className="btn-primary" style={{ marginTop: '24px', textDecoration: 'none' }}>
          View All Processes
        </Link>
      </div>
    );
  }

  // Get feedback from previous iteration
  const cvUpdateResult = processRun.stage_results.find(sr => sr.stage === 'cv_update');
  const feedback = cvUpdateResult?.manual_feedback ? JSON.parse(cvUpdateResult.manual_feedback) : null;

  // Get ATS rating results (both original and new)
  const atsRatingResult = processRun.stage_results.find(sr => sr.stage === 'ats_rating');
  const dualRatings = atsRatingResult?.result as any;

  return (
    <div className="process-detail animate-fade-in">
      <div className="breadcrumbs">
        <Link to="/history" className="breadcrumb-item">History</Link>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-item active">Process Details</span>
      </div>

      <div className="process-header">
        <h2>
          {getStatusIcon(processRun.status)} Analysis Status: {processRun.status.toUpperCase()}
        </h2>
        {job && (
          <p className="job-title" style={{ fontSize: '18px', marginTop: '12px', fontWeight: 500 }}>
            📌 {job.title}
          </p>
        )}
        {processRun.iteration_count > 0 && (
          <p className="retry-info">
            🔄 Iteration: {processRun.iteration_count} / {processRun.max_iterations}
          </p>
        )}
        {processRun.retry_count > 0 && (
          <p className="retry-info">
            ⚠️ Retries: {processRun.retry_count} / {processRun.max_retries}
          </p>
        )}
        <div style={{ marginTop: '16px', color: 'var(--text-light)', fontSize: '14px' }}>
          Started: {new Date(processRun.created_at).toLocaleString()}
        </div>
      </div>

      <ProcessTracker stages={processRun.stage_results} />

      {/* Restart Button for Failed Processes */}
      {processRun.status === 'failed' && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <div style={{ marginBottom: '16px', padding: '16px', 
            backgroundColor: 'var(--error-bg)', borderRadius: '8px',
            border: '2px solid var(--error)' }}>
            <p style={{ marginBottom: '8px', fontSize: '14px', color: 'var(--text)' }}>
              The process encountered an error. You can restart it from the point of failure.
              All completed stages will be preserved.
            </p>
            <button
              className="btn-primary"
              onClick={handleRestart}
              disabled={restarting}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                opacity: restarting ? 0.5 : 1
              }}
            >
              {restarting ? '🔄 Retrying...' : '🔄 Retry Process'}
            </button>
          </div>
          
          {error && (
            <div style={{
              marginBottom: '16px',
              padding: '12px',
              backgroundColor: 'var(--error-bg)',
              color: 'var(--error)',
              borderRadius: '8px'
            }}>
              {error}
            </div>
          )}

          {/* Force Complete Button for Failed Processes */}
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <button
              className="btn-primary"
              onClick={handleForceComplete}
              disabled={forceCompleting}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                backgroundColor: 'var(--warning)',
                opacity: forceCompleting ? 0.5 : 1
              }}
            >
              {forceCompleting ? '⚡ Completing...' : '⚡ Force Complete'}
            </button>
          </div>
        </div>
      )}

      {/* Show feedback from previous iteration */}
      {feedback && !feedback.meets_criteria && isAwaitingInput && (
        <div className="feedback-display animate-fade-in" style={{
          marginTop: '24px',
          padding: '20px',
          backgroundColor: 'var(--surface)',
          borderRadius: '8px',
          border: '2px solid var(--warning)'
        }}>
          <h3 style={{ color: 'var(--warning)', marginBottom: '12px' }}>💡 Previous Iteration Feedback</h3>
          <div style={{ marginBottom: '12px' }}>
            <strong>ATS Score:</strong> {feedback.ats_score.toFixed(1)} / 100<br />
            <strong>Match Rate:</strong> {feedback.match_rate.toFixed(1)} / 100
          </div>
          <p style={{ color: 'var(--text)', marginBottom: '12px' }}>{feedback.reason}</p>
          {feedback.improvement_suggestions && feedback.improvement_suggestions.length > 0 && (
            <div>
              <strong>Improvement Suggestions:</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {feedback.improvement_suggestions.map((suggestion: string, idx: number) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Force Complete Button for Other States */}
      {(processRun.status === 'running' || processRun.status === 'awaiting_manual_input' || processRun.status === 'pending') && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <div style={{ marginBottom: '16px', padding: '16px', 
            backgroundColor: 'var(--warning-bg)', borderRadius: '8px',
            border: '2px solid var(--warning)' }}>
            <p style={{ marginBottom: '8px', fontSize: '14px', color: 'var(--text)' }}>
              The process is currently active. You can force complete it if desired.
              This will bypass all remaining agent executions.
            </p>
            <button
              className="btn-primary"
              onClick={handleForceComplete}
              disabled={forceCompleting}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                backgroundColor: 'var(--warning)',
                opacity: forceCompleting ? 0.5 : 1
              }}
            >
              {forceCompleting ? '⚡ Completing...' : '⚡ Force Complete'}
            </button>
          </div>
        </div>
      )}

      {/* Manual Input Section */}
      {isAwaitingInput && (
        <div className="manual-input-section animate-fade-in" style={{ marginTop: '24px' }}>
          <h3 style={{ marginBottom: '16px' }}>🤖 Manual CV Optimization</h3>
          
          <p style={{ marginBottom: '16px', color: 'var(--text-light)' }}>
            Copy the prompt below, paste it into an external LLM, then paste the result back here.
          </p>

          {/* Prompt Display */}
          {promptLoading ? (
            <div className="loading-spinner" style={{ margin: '20px auto' }}></div>
          ) : error ? (
            <div style={{ 
              padding: '16px', 
              backgroundColor: 'var(--error-bg)', 
              color: 'var(--error)',
              borderRadius: '8px',
              marginBottom: '16px'
            }}>
              {error}
            </div>
          ) : (
            <div className="prompt-display" style={{ marginBottom: '24px' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '12px'
              }}>
                <strong>Generated Prompt:</strong>
                <button 
                  className="btn-primary" 
                  onClick={handleCopy}
                  style={{ padding: '8px 16px', fontSize: '14px' }}
                >
                  {copied ? '✅ Copied!' : '📋 Copy Prompt'}
                </button>
              </div>
              <textarea
                value={prompt}
                readOnly
                style={{
                  width: '100%',
                  minHeight: '300px',
                  padding: '16px',
                  fontFamily: 'monospace',
                  fontSize: '13px',
                  border: '2px solid var(--border)',
                  borderRadius: '8px',
                  backgroundColor: 'var(--surface)',
                  color: 'var(--text)',
                  resize: 'vertical'
                }}
              />
            </div>
          )}

          {/* Manual Input */}
          <div className="manual-latex-input">
            <div style={{ marginBottom: '12px' }}>
              <strong>Paste Updated LaTeX from External LLM:</strong>
            </div>
            <textarea
              value={manualLatex}
              onChange={(e) => setManualLatex(e.target.value)}
              placeholder="Paste the updated LaTeX code here..."
              style={{
                width: '100%',
                minHeight: '300px',
                padding: '16px',
                fontFamily: 'monospace',
                fontSize: '13px',
                border: manualLatex ? '2px solid var(--primary)' : '2px solid var(--border)',
                borderRadius: '8px',
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                resize: 'vertical'
              }}
            />
            
            <button
              className="btn-primary"
              onClick={handleSubmitLatex}
              disabled={submitting || !manualLatex.trim()}
              style={{
                marginTop: '16px',
                padding: '12px 24px',
                fontSize: '16px',
                opacity: submitting || !manualLatex.trim() ? 0.5 : 1
              }}
            >
              {submitting ? '🔄 Submitting...' : '✅ Submit to Agent 4'}
            </button>
            
            {error && (
              <div style={{
                marginTop: '12px',
                padding: '12px',
                backgroundColor: 'var(--error-bg)',
                color: 'var(--error)',
                borderRadius: '8px'
              }}>
                {error}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Final LaTeX Output */}
      {processRun.manual_latex_input && processRun.status === 'completed' && !isAwaitingInput && (
        <div className="latex-output animate-fade-in">
          <h3>📝 Final LaTeX CV (from external LLM)</h3>
          <pre className="latex-code">{processRun.manual_latex_input}</pre>
          <button className="btn-primary" onClick={async () => {
            await navigator.clipboard.writeText(processRun.manual_latex_input);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
          }}>
            {copied ? '✅ Copied!' : '📋 Copy LaTeX'}
          </button>
        </div>
      )}

      {/* Dual Ratings Comparison */}
      {processRun.status === 'completed' && dualRatings?.original_latex && dualRatings?.new_latex && (
        <div className="dual-ratings animate-fade-in" style={{ 
          marginTop: '24px',
          padding: '20px',
          backgroundColor: 'var(--surface)',
          borderRadius: '8px',
          border: '2px solid var(--primary)'
        }}>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>📊 Rating Comparison</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            {/* Original LaTeX Rating */}
            <div style={{ padding: '16px', backgroundColor: 'var(--surface)', borderRadius: '8px', border: '1px solid var(--border)' }}>
              <h4 style={{ marginBottom: '12px', color: 'var(--text-light)' }}>📄 Original LaTeX</h4>
              <div style={{ marginBottom: '8px' }}>
                <strong>ATS Score:</strong> {dualRatings.original_latex.ats_score?.toFixed(1) || 0} / 100
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Match Rate:</strong> {dualRatings.original_latex.match_rate?.toFixed(1) || 0} / 100
              </div>
              <p style={{ fontSize: '14px', color: 'var(--text-light)', marginTop: '12px' }}>
                {dualRatings.original_latex.overall_assessment || 'No assessment available'}
              </p>
            </div>
            
            {/* New LaTeX Rating */}
            <div style={{ padding: '16px', backgroundColor: 'var(--success-bg)', borderRadius: '8px', border: '1px solid var(--success)' }}>
              <h4 style={{ marginBottom: '12px', color: 'var(--success)' }}>✨ New LaTeX (from external LLM)</h4>
              <div style={{ marginBottom: '8px' }}>
                <strong>ATS Score:</strong> {dualRatings.new_latex.ats_score?.toFixed(1) || 0} / 100
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>Match Rate:</strong> {dualRatings.new_latex.match_rate?.toFixed(1) || 0} / 100
              </div>
              <p style={{ fontSize: '14px', color: 'var(--text)', marginTop: '12px' }}>
                {dualRatings.new_latex.overall_assessment || 'No assessment available'}
              </p>
            </div>
          </div>
          
          {/* Improvement Summary */}
          {dualRatings.improvement && (
            <div style={{ padding: '16px', backgroundColor: 'var(--primary-bg)', borderRadius: '8px', border: '1px solid var(--primary)' }}>
              <h4 style={{ marginBottom: '8px', color: 'var(--primary)' }}>📈 Improvement Summary</h4>
              <div style={{ marginBottom: '4px' }}>
                ATS Score Change: {dualRatings.improvement.ats_score_change > 0 ? '+' : ''}
                {dualRatings.improvement.ats_score_change.toFixed(1)}
                {dualRatings.improvement.ats_score_change > 0 ? ' 📈' : dualRatings.improvement.ats_score_change < 0 ? ' 📉' : ''}
              </div>
              <div>
                Match Rate Change: {dualRatings.improvement.match_rate_change > 0 ? '+' : ''}
                {dualRatings.improvement.match_rate_change.toFixed(1)}
                {dualRatings.improvement.match_rate_change > 0 ? ' 📈' : dualRatings.improvement.match_rate_change < 0 ? ' 📉' : ''}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ATS Results */}
      {processRun.status === 'completed' && feedback && (
        <div className="ats-results animate-fade-in" style={{ 
          marginTop: '24px',
          padding: '20px',
          backgroundColor: 'var(--surface)',
          borderRadius: '8px',
          border: '2px solid var(--success)'
        }}>
          <h3 style={{ color: 'var(--success)', marginBottom: '12px' }}>🎯 Final Results (New LaTeX)</h3>
          <div style={{ marginBottom: '12px' }}>
            <strong>ATS Score:</strong> {feedback.ats_score.toFixed(1)} / 100<br />
            <strong>Match Rate:</strong> {feedback.match_rate.toFixed(1)} / 100
          </div>
          <p style={{ color: 'var(--text)', marginBottom: '12px' }}>{feedback.reason}</p>
          
          {feedback.strong_points && feedback.strong_points.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <strong>✅ Strong Points:</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {feedback.strong_points.map((point: string, idx: number) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          
          {feedback.weak_points && feedback.weak_points.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <strong>⚠️ Weak Points:</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {feedback.weak_points.map((point: string, idx: number) => (
                  <li key={idx}>{point}</li>
                ))}
              </ul>
            </div>
          )}
          
          {feedback.improvement_suggestions && feedback.improvement_suggestions.length > 0 && (
            <div>
              <strong>💡 Improvement Suggestions:</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                {feedback.improvement_suggestions.map((suggestion: string, idx: number) => (
                  <li key={idx}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Continue Iterating Button */}
      {processRun.status === 'completed' && !isAwaitingInput && 
       processRun.iteration_count < processRun.max_iterations && (
        <div style={{ marginTop: '32px', textAlign: 'center' }}>
          <div style={{ marginBottom: '16px', padding: '16px', 
            backgroundColor: 'var(--surface)', borderRadius: '8px',
            border: '2px solid var(--primary)' }}>
            <p style={{ marginBottom: '8px', fontSize: '14px', color: 'var(--text-light)' }}>
              You can continue improving your CV. {processRun.max_iterations - processRun.iteration_count} more iteration(s) available.
            </p>
            <button
              className="btn-primary"
              onClick={handleContinueIterating}
              disabled={continuing}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                opacity: continuing ? 0.5 : 1
              }}
            >
              {continuing ? '🔄 Starting...' : '🔄 Continue Iterating'}
            </button>
          </div>
          
          {error && (
            <div style={{
              marginBottom: '16px',
              padding: '12px',
              backgroundColor: 'var(--error-bg)',
              color: 'var(--error)',
              borderRadius: '8px'
            }}>
              {error}
            </div>
          )}
        </div>
      )}

      {processRun.status === 'completed' && !isAwaitingInput && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <Link to="/" className="btn-primary" style={{ textDecoration: 'none', marginRight: '12px' }}>
            🚀 New Analysis
          </Link>
          <Link to="/history" className="btn-primary" style={{ 
            textDecoration: 'none', 
            background: 'var(--surface)',
            color: 'var(--primary)',
            border: '2px solid var(--primary)'
          }}>
            📋 View History
          </Link>
        </div>
      )}
    </div>
  );
}