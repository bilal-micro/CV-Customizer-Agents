import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getJobs } from '../api';
import { useAuth } from '../context/AuthContext';
import type { Job } from '../types';

export default function ProcessList() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, authLoading, navigate]);

  const fetchJobs = useCallback(async () => {
    try {
      const data = await getJobs();
      setJobs(data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  if (loading) {
    return (
      <div className="loading-container animate-fade-in">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading your job history...</div>
      </div>
    );
  }

  return (
    <div className="process-list animate-fade-in">
      <h2>📋 Process History</h2>
      {jobs.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <div className="empty-state-text">No processes yet</div>
          <div className="empty-state-subtext">
            Submit your first job to start analyzing applications with AI
          </div>
          <Link to="/" className="btn-primary" style={{ marginTop: '24px', textDecoration: 'none' }}>
            🚀 Start New Analysis
          </Link>
        </div>
      ) : (
        <div className="job-list">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <h3>{job.title}</h3>
              <p className="job-meta">Created {new Date(job.created_at).toLocaleDateString()}</p>
              <div className="process-runs">
                {job.process_runs.map((run) => (
                  <Link 
                    key={run.id} 
                    to={`/process/${run.id}`} 
                    className={`run-link badge-${run.status}`}
                  >
                    {run.status === 'completed' && '✅'}
                    {run.status === 'running' && '🔄'}
                    {run.status === 'failed' && '❌'}
                    {run.status === 'pending' && '⏳'}
                    {run.status} ({run.retry_count} {run.retry_count === 1 ? 'retry' : 'retries'})
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
