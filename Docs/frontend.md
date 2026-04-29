# Frontend Architecture

**Purpose**: React TypeScript frontend for ATS-Agentic system  
**Location**: `frontend/src/`  
**Framework**: React + TypeScript + Vite

---

## Overview

The frontend is a single-page application (SPA) built with React and TypeScript. It provides a user interface for creating jobs, monitoring CV optimization processes, and viewing results.

---

## API Client

**File**: `frontend/src/api/index.ts`  
**Lines**: 1-58

### Configuration

```typescript
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000, // 30 second timeout
});
```

### API Functions

#### `createJob(data)`
- **Input**: `{ title: string; description: string; latex_cv: string }`
- **Output**: Promise<Job>
- **Endpoint**: `POST /api/jobs/`
- **Purpose**: Create a new job with CV

#### `getJobs()`
- **Input**: None
- **Output**: Promise<Job[]>
- **Endpoint**: `GET /api/jobs/`
- **Purpose**: Retrieve all jobs

#### `getJob(id)`
- **Input**: `id: string`
- **Output**: Promise<Job>
- **Endpoint**: `GET /api/jobs/{id}/`
- **Purpose**: Retrieve specific job

#### `runProcess(jobId, maxRetries)`
- **Input**: `jobId: string`, `maxRetries: number = 3`
- **Output**: Promise<ProcessRun>
- **Endpoint**: `POST /api/jobs/{id}/run_process/`
- **Purpose**: Start CV optimization process

#### `getProcessRuns()`
- **Input**: None
- **Output**: Promise<ProcessRun[]>
- **Endpoint**: `GET /api/process-runs/`
- **Purpose**: Retrieve all process runs

#### `getProcessRun(id)`
- **Input**: `id: string`
- **Output**: Promise<ProcessRun>
- **Endpoint**: `GET /api/process-runs/{id}/`
- **Purpose**: Retrieve specific process run

#### `getPrompt(id)`
- **Input**: `id: string`
- **Output**: Promise<{ prompt: string; iteration_number: number; max_iterations: number }>
- **Endpoint**: `GET /api/process-runs/{id}/get_prompt/`
- **Purpose**: Get generated prompt for external LLM

#### `submitManualLatex(id, latexContent)`
- **Input**: `id: string`, `latexContent: string`
- **Output**: Promise<{ message: string; iteration: number }>
- **Endpoint**: `POST /api/process-runs/{id}/submit_manual_latex/`
- **Purpose**: Submit manually updated LaTeX

#### `continueIterating(id)`
- **Input**: `id: string`
- **Output**: Promise<{ message: string; process: ProcessRun }>
- **Endpoint**: `POST /api/process-runs/{id}/continue_iterating/`
- **Purpose**: Trigger new iteration after completion

#### `restartProcess(id)`
- **Input**: `id: string`
- **Output**: Promise<{ message: string }>
- **Endpoint**: `POST /api/process-runs/{id}/restart/`
- **Purpose**: Restart failed process

#### `healthCheck()`
- **Input**: None
- **Output**: Promise<{ status: string; ollama_status: string; ollama_url: string; ollama_model: string }>
- **Endpoint**: `GET /health/`
- **Purpose**: Check system health

---

## Components

### 1. JobForm

**File**: `frontend/src/components/JobForm.tsx`

**Purpose**: Form for creating new jobs

**Props**: None

**State**:
- `title` (string): Job title
- `description` (string): Job description
- `latex_cv` (string): LaTeX CV content

**Methods**:
- `handleSubmit()`: Submits form to create job
- `handleRunProcess()`: Starts optimization process for created job

**UI Elements**:
- Title input field
- Description textarea
- LaTeX CV textarea
- Create Job button
- Run Process button (after job creation)

---

### 2. ProcessTracker

**File**: `frontend/src/components/ProcessTracker.tsx`  
**Lines**: 1-483

**Purpose**: Display and track optimization process progress

**Props**:
- `stages`: `StageResult[]` - Array of stage results

**Features**:
- Progress percentage calculation
- Stage timeline visualization
- Status indicators (pending, running, completed, failed)
- Stage quality rating bars
- Detailed stage result display

**Stage Displays**:

#### Keyword Extraction Stage
- Hard skills with priority ratings
- Soft skills with priority ratings
- Qualifications (degrees, certifications)
- Must-have keywords
- Nice-to-have keywords
- Job notes summary

#### CV Matching Stage
- Section analysis grid (education, experience, skills, projects, summary)
- Relevance scores per section
- Keyword density per section
- Top keywords per section
- Matched keywords (with context)
- Missing keywords (with importance)
- Strengths list
- Weaknesses list
- Analysis notes (formatted by category)

#### CV Update Stage
- Changes made list
- Unchangeable gaps list
- Update notes

#### ATS Rating Stage
- ATS score (0-100)
- Recruiter appeal (0-100)
- ATS breakdown (keyword_density, formatting, readability, completeness)
- Strong points list
- Weak points list
- Improvement suggestions list
- Expected interview questions
- Overall assessment

**Visual Components**:
- `RatingBar`: Progress bar with color coding
- `KeywordList`: Tag-based keyword display
- `KeywordDetails`: Detailed keyword information

---

### 3. KeywordDetails

**File**: `frontend/src/components/KeywordDetails.tsx`

**Purpose**: Display detailed matched and missing keyword information

**Props**:
- `matchedKeywords`: `MatchedKeyword[]`
- `missingKeywords`: `MissingKeyword[]`

**Display**:
- Matched keywords with context
- Missing keywords with importance ratings

---

### 4. KeywordExtractionDisplay

**File**: `frontend/src/components/KeywordExtractionDisplay.tsx`

**Purpose**: Display extracted keywords with formatting

**Props**:
- `items`: `ExtractedKeyword[]`
- `label`: string
- `category`: string

**Display**:
- Tag-based keyword display
- Category-specific styling
- Priority indicators

---

### 5. ProcessList

**File**: `frontend/src/components/ProcessList.tsx`

**Purpose**: List all jobs and their process runs

**Props**: None

**Features**:
- Job list with titles and creation dates
- Process run status indicators
- Navigation to process details
- Action buttons (run process, view details)

---

## Pages

### ProcessDetail Page

**File**: `frontend/src/pages/ProcessDetail.tsx`

**Purpose**: Detailed view of a single process run

**Features**:
- Process run status display
- Stage results with ProcessTracker
- Action buttons (submit LaTeX, continue iterating, restart)
- Real-time status updates (polling)

**Actions**:
- Get prompt from CV Update stage
- Submit manual LaTeX input
- Continue iterating after completion
- Restart failed process

---

## Types

**File**: `frontend/src/types/index.ts`

### Core Types

```typescript
interface Job {
  id: string;
  title: string;
  description: string;
  latex_cv: string;
  created_at: string;
  process_runs: ProcessRun[];
}

interface ProcessRun {
  id: string;
  job: Job;
  status: 'pending' | 'running' | 'awaiting_manual_input' | 'completed' | 'failed';
  iteration_count: number;
  max_iterations: number;
  retry_count: number;
  max_retries: number;
  manual_latex_input: string;
  original_latex: string;
  created_at: string;
  updated_at: string;
  stage_results: StageResult[];
}

interface StageResult {
  id: string;
  process_run: ProcessRun;
  stage: 'keyword_extraction' | 'cv_matching' | 'cv_update' | 'ats_rating';
  status: 'pending' | 'running' | 'completed' | 'failed';
  result: any; // Varies by stage
  rating: number | null;
  notes: string;
  iteration_notes: string;
  manual_feedback: string;
  iteration_number: number;
  created_at: string;
  updated_at: string;
}

interface ExtractedKeyword {
  skill?: string;
  keyword?: string;
  priority: number;
  category: string;
  placement_hints: string[];
  confidence: number;
}

interface MatchedKeyword {
  keyword: string;
  found_in: string;
  context: string;
  relevance: number;
}

interface MissingKeyword {
  keyword: string;
  importance: number;
  priority: 'must_have' | 'nice_to_have';
}
```

---

## Styling

### CSS Variables (Dark Mode Theme)

```css
:root {
  --primary: #3b82f6;
  --primary-bg: #dbeafe;
  --success: #22c55e;
  --success-bg: #dcfce7;
  --warning: #eab308;
  --warning-bg: #fef3c7;
  --error: #ef4444;
  --error-bg: #fee2e2;
  
  --bg: #1e293b;
  --surface: #334155;
  --border: #475569;
  
  --text: #e2e8f0;
  --text-h: #f1f5f9;
  --text-light: #94a3b8;
}
```

### Component Classes

- `.process-tracker`: Main container
- `.stages-timeline`: Stage list
- `.stage-card`: Individual stage container
- `.stage-header`: Stage title and status
- `.stage-status`: Status badge
- `.rating-bar`: Progress indicator
- `.keyword-section`: Keyword group
- `.keyword-tags`: Tag container
- `.tag`: Individual keyword tag
- `.notes-section`: Notes container
- `.badge-{status}`: Status-specific styling

---

## State Management

The frontend uses React hooks for local state management:

- `useState`: Component-level state
- `useEffect`: Side effects (API calls, polling)
- `useCallback`: Memoized callbacks
- `useMemo`: Computed values

No global state management library (Redux, Context) is currently used.

---

## Polling

Real-time updates achieved through polling:

```typescript
useEffect(() => {
  const interval = setInterval(() => {
    getProcessRun(id).then(setProcessRun);
  }, 2000); // Poll every 2 seconds
  
  return () => clearInterval(interval);
}, [id]);
```

Used for:
- Process run status updates
- Stage completion tracking

---

## Error Handling

### API Errors

Handled by axios response interceptor:

```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

### Display Errors

Components display error messages:
- Validation errors: Form field feedback
- Network errors: Alert banners
- Server errors: Error cards

---

## Responsive Design

Mobile-first approach with breakpoints:
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

Grid and flexbox used for responsive layouts.

---

## Performance Optimizations

- Memoized components with `React.memo`
- Lazy loading for large components
- Debounced form inputs
- Optimized re-renders with `useCallback` and `useMemo`

---

## Build Configuration

**File**: `frontend/vite.config.ts`

- Development server: `http://localhost:5173`
- API proxy: `/api` → `http://localhost:8000/api`
- Build output: `dist/`

**Scripts**:
- `npm run dev`: Start dev server
- `npm run build`: Production build
- `npm run preview`: Preview production build

---

**End of Frontend Documentation**