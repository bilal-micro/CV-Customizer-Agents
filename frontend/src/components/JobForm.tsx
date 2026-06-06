import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { createJob, runProcess } from '../api';

export default function JobForm() {
  const navigate = useNavigate();
  const { isAuthenticated, loading: authLoading } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, authLoading, navigate]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [latexCv, setLatexCv] = useState('');
  const [additionalSkills, setAdditionalSkills] = useState('');
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (ev) => setLatexCv(ev.target?.result as string);
    reader.readAsText(file);
  }, []);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file && (file.name.endsWith('.tex') || file.name.endsWith('.txt') || file.name.endsWith('.latex'))) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (ev) => setLatexCv(ev.target?.result as string);
      reader.readAsText(file);
    } else {
      setError('Please upload a .tex, .txt, or .latex file');
    }
  }, []);

  const handleRemoveFile = useCallback(() => {
    setLatexCv('');
    setFileName('');
  }, []);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!title || !description || !latexCv) {
        setError('All fields are required');
        return;
      }
      setLoading(true);
      setError('');
      try {
        console.log('Creating job...');
        const job = await createJob({ title, description, latex_cv: latexCv, additional_skills: additionalSkills });
        console.log('Job created:', job);
        
        if (!job?.id) {
          throw new Error('Invalid job response - no job ID returned');
        }
        
        console.log('Starting process for job:', job.id);
        const processRun = await runProcess(job.id);
        console.log('Process run started:', processRun);
        
        if (!processRun?.id) {
          throw new Error('Invalid process run response - no process ID returned');
        }
        
        navigate(`/process/${processRun.id}`);
      } catch (err: any) {
        const errorMessage = err?.response?.data?.error || err?.response?.data?.detail || err?.message || 'Failed to start process';
        setError(`${errorMessage}. Make sure the backend is running and check console for details.`);
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    },
    [title, description, latexCv, navigate],
  );

  const getCharCounterClass = (current: number, max: number) => {
    const percentage = (current / max) * 100;
    if (percentage >= 90) return 'error';
    if (percentage >= 75) return 'warning';
    return '';
  };

  return (
    <div className="job-form animate-fade-in">
      <h2>🎯 Submit Job Application</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">
            Job Title
            <span className="label-hint">(Required)</span>
          </label>
          <input 
            id="title" 
            type="text" 
            value={title} 
            onChange={(e) => setTitle(e.target.value)} 
            placeholder="e.g. Senior Python Developer"
            maxLength={100}
          />
          <div className={`char-counter ${getCharCounterClass(title.length, 100)}`}>
            {title.length} / 100
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="description">
            Job Description / Requirements
            <span className="label-hint">(Paste the full job description)</span>
          </label>
          <textarea 
            id="description" 
            value={description} 
            onChange={(e) => setDescription(e.target.value)} 
            rows={12} 
            placeholder="Paste the full job description here including requirements, qualifications, and responsibilities..."
            maxLength={10000}
          />
          <div className={`char-counter ${getCharCounterClass(description.length, 10000)}`}>
            {description.length.toLocaleString()} / 10,000
          </div>
        </div>

        <div className="form-group">
          <label>
            Upload LaTeX CV
            <span className="label-hint">(.tex, .txt, or .latex)</span>
          </label>
          
          {!latexCv && (
            <div
              className={`drop-zone ${dragActive ? 'dragover' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="drop-zone-icon">📄</div>
              <div className="drop-zone-text">Drag & drop your LaTeX CV here</div>
              <div className="drop-zone-subtext">or click to browse files</div>
              <input
                id="latex"
                type="file"
                accept=".tex,.txt,.latex"
                onChange={handleFileUpload}
              />
            </div>
          )}

          {latexCv && (
            <div className="file-preview file-preview-success">
              <div className="file-name">
                {fileName || 'Pasted LaTeX content'}
                <span style={{ marginLeft: '8px', opacity: 0.7 }}>
                  ({latexCv.length.toLocaleString()} characters)
                </span>
              </div>
              <span className="file-remove" onClick={handleRemoveFile}>✕</span>
            </div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="latex-manual">
            Or paste LaTeX CV
            <span className="label-hint">(Alternative to upload)</span>
          </label>
          <textarea 
            id="latex-manual" 
            value={latexCv} 
            onChange={(e) => {
              setLatexCv(e.target.value);
              setFileName('');
            }} 
            rows={8} 
            placeholder="\documentclass{article}
\begin{document}
Your CV content here...
\end{document}"
          />
        </div>

        <div className="form-group">
          <label htmlFor="additional-skills">
            Additional Skills & Experience
            <span className="label-hint">(Optional — helps generate a stronger CV)</span>
          </label>
          <textarea
            id="additional-skills"
            value={additionalSkills}
            onChange={(e) => setAdditionalSkills(e.target.value)}
            rows={6}
            placeholder="List your tools, technologies, frameworks, programming languages, platforms, and skills you have experience with. For example: Docker, Kubernetes, PostgreSQL, Redis, Celery, Git, CI/CD, REST APIs, GraphQL, AWS, Linux, Agile/Scrum..."
          />
          <div className="field-hint" style={{ fontSize: '0.85em', color: 'var(--text-secondary)', marginTop: '4px' }}>
            💡 This information helps the AI agent create a more personalized and stronger CV by incorporating your actual skills into the optimization process.
          </div>
        </div>

        <button type="submit" disabled={loading || !title || !description || !latexCv} className="btn-primary">
          {loading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>
              🚀 Start ATS Analysis
            </>
          )}
        </button>
      </form>
    </div>
  );
}
