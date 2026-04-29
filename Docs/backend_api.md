# Backend API Endpoints

**Purpose**: REST API for ATS-Agentic system  
**Location**: `backend/ats_app/views.py`  
**Lines**: 1-300  
**Framework**: Django REST Framework

---

## API Overview

Base URL: `http://localhost:8000`

### Authentication
Currently using public API (no authentication required)

### Response Format
All responses return JSON with appropriate HTTP status codes

---

## Endpoints

### 1. Health Check

**Endpoint**: `GET /health/`  
**Purpose**: Check system health and Ollama connectivity

**Response** (200 OK):
```json
{
  "status": "healthy",
  "ollama_status": "connected",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3.1"
}
```

**Response** (500 Internal Server Error):
```json
{
  "status": "unhealthy",
  "error": "Error message"
}
```

---

### 2. Jobs

#### List All Jobs
**Endpoint**: `GET /api/jobs/`  
**Purpose**: Retrieve all jobs with their process runs

**Response** (200 OK):
```json
{
  "id": "uuid",
  "title": "Senior Backend Developer",
  "description": "Full job description...",
  "latex_cv": "\\documentclass{resume}...",
  "created_at": "2026-04-19T20:00:00Z",
  "process_runs": [
    {
      "id": "uuid",
      "status": "completed",
      "iteration_count": 2,
      "created_at": "2026-04-19T20:01:00Z"
    }
  ]
}
```

#### Create New Job
**Endpoint**: `POST /api/jobs/`  
**Purpose**: Create a new job with CV

**Request Body**:
```json
{
  "title": "Senior Backend Developer",
  "description": "Full job description here...",
  "latex_cv": "\\documentclass{resume}\n\\begin{document}\n..."
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "Senior Backend Developer",
  "description": "Full job description...",
  "latex_cv": "\\documentclass{resume}...",
  "created_at": "2026-04-19T20:00:00Z",
  "process_runs": []
}
```

**Validation Errors** (400 Bad Request):
```json
{
  "title": ["This field is required."],
  "description": ["This field is required."],
  "latex_cv": ["This field is required."]
}
```

#### Get Job Details
**Endpoint**: `GET /api/jobs/{id}/`  
**Purpose**: Retrieve specific job details

**Response** (200 OK): Same as List All Jobs format

**Not Found** (404):
```json
{
  "detail": "Not found."
}
```

#### Run Process
**Endpoint**: `POST /api/jobs/{id}/run_process/`  
**Purpose**: Start CV optimization process for a job

**Response** (201 Created):
```json
{
  "id": "uuid",
  "job": "uuid",
  "status": "running",
  "iteration_count": 0,
  "max_iterations": 3,
  "created_at": "2026-04-19T20:01:00Z",
  "stage_results": []
}
```

**Behavior**:
- Creates new ProcessRun
- Starts orchestrator in background thread
- Returns immediately (async processing)

---

### 3. Process Runs

#### List All Process Runs
**Endpoint**: `GET /api/process-runs/`  
**Purpose**: Retrieve all process runs with stage results

**Response** (200 OK):
```json
{
  "id": "uuid",
  "job": {
    "id": "uuid",
    "title": "Senior Backend Developer"
  },
  "status": "running",
  "iteration_count": 1,
  "max_iterations": 3,
  "created_at": "2026-04-19T20:01:00Z",
  "stage_results": [
    {
      "id": "uuid",
      "stage": "keyword_extraction",
      "status": "completed",
      "result": {...},
      "rating": 95.0,
      "iteration_number": 0
    }
  ]
}
```

#### Get Process Run Details
**Endpoint**: `GET /api/process-runs/{id}/`  
**Purpose**: Retrieve specific process run details

**Response** (200 OK): Same as List All Process Runs format

#### Get Generated Prompt
**Endpoint**: `GET /api/process-runs/{id}/get_prompt/`  
**Purpose**: Retrieve generated prompt from Agent 3 for external LLM

**Response** (200 OK):
```json
{
  "prompt": "You are an expert CV writer. Please optimize this LaTeX CV...",
  "iteration_number": 1,
  "max_iterations": 3
}
```

**Not Ready** (400 Bad Request):
```json
{
  "error": "No prompt generated yet"
}
```

**Not Found** (404):
```json
{
  "error": "Prompt not found in result"
}
```

#### Submit Manual LaTeX
**Endpoint**: `POST /api/process-runs/{id}/submit_manual_latex/`  
**Purpose**: Submit manually updated LaTeX from external LLM

**Request Body**:
```json
{
  "latex_content": "\\documentclass{resume}\n\\begin{document}\n..."
}
```

**Response** (200 OK):
```json
{
  "message": "LaTeX submitted successfully. Process is resuming...",
  "iteration": 1
}
```

**Validation Errors** (400 Bad Request):
```json
{
  "error": "Process is not awaiting manual input. Current status: running"
}
```

```json
{
  "latex_content": ["This field is required."]
}
```

**Invalid LaTeX** (400 Bad Request):
```json
{
  "error": "Missing \\documentclass"
}
```

#### Continue Iterating
**Endpoint**: `POST /api/process-runs/{id}/continue_iterating/`  
**Purpose**: Trigger a new manual iteration after process completion

**Response** (200 OK):
```json
{
  "message": "New iteration triggered successfully",
  "process": {
    "id": "uuid",
    "status": "awaiting_manual_input",
    "iteration_count": 2,
    "max_iterations": 4
  }
}
```

**Wrong Status** (400 Bad Request):
```json
{
  "error": "Process is not completed. Current status: running"
}
```

**Max Iterations** (400 Bad Request):
```json
{
  "error": "Max iterations (3) reached"
}
```

**Behavior**:
- Increments max_iterations by 1
- Generates new prompt with feedback
- Sets status to 'awaiting_manual_input'

#### Restart Failed Process
**Endpoint**: `POST /api/process-runs/{id}/restart/`  
**Purpose**: Restart a failed process from point of failure

**Response** (200 OK):
```json
{
  "message": "Process restarted successfully from failure point"
}
```

**Wrong Status** (400 Bad Request):
```json
{
  "error": "Process is not failed. Current status: running"
}
```

**Behavior**:
- Identifies failed stage
- Resets failed and subsequent stages to 'pending'
- Preserves all completed stage results
- Resumes from failed stage

---

### 4. Stage Results

#### List All Stage Results
**Endpoint**: `GET /api/stage-results/`  
**Purpose**: Retrieve all stage results

**Response** (200 OK):
```json
{
  "id": "uuid",
  "process_run": {
    "id": "uuid",
    "job": {
      "id": "uuid",
      "title": "Senior Backend Developer"
    }
  },
  "stage": "keyword_extraction",
  "status": "completed",
  "result": {
    "hard_skills": [...],
    "soft_skills": [...]
  },
  "rating": 95.0,
  "notes": "Extracted 15 keywords",
  "iteration_number": 0,
  "created_at": "2026-04-19T20:01:00Z"
}
```

#### Get Stage Result Details
**Endpoint**: `GET /api/stage-results/{id}/`  
**Purpose**: Retrieve specific stage result details

**Response** (200 OK): Same as List All Stage Results format

---

## Status Codes

| Code | Meaning | Description |
|------|----------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or validation error |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

---

## ProcessRun Status Values

| Status | Description | User Action |
|--------|-------------|-------------|
| `pending` | Not started | Run process |
| `running` | Actively processing | Wait for completion |
| `awaiting_manual_input` | Waiting for user input | Submit LaTeX |
| `completed` | Successfully finished | View results or continue iterating |
| `failed` | Error occurred | Restart process |

---

## Stage Names

| Stage | Description | Occurs In |
|-------|-------------|-------------|
| `keyword_extraction` | Extract keywords from job | Phase 1 (once) |
| `cv_matching` | Match CV against keywords | Phase 1, Phase 2 (per iteration) |
| `cv_update` | Generate prompt for external LLM | Phase 2 (per iteration) |
| `ats_rating` | Rate CV against ATS standards | Phase 2 (per iteration) |

---

## Error Handling

All endpoints return consistent error format:

```json
{
  "error": "Human-readable error message"
}
```

Common errors:
- **Validation errors**: Missing required fields, invalid format
- **Status errors**: Wrong process status for action
- **Not found errors**: Resource doesn't exist
- **Internal errors**: Server-side failures

---

## Async Processing

- `run_process`, `submit_manual_latex`, and `restart` endpoints run orchestrator in background threads
- These endpoints return immediately (async processing)
- Client should poll `process-runs/{id}/` to check status updates

---

## Rate Limiting

Currently no rate limiting implemented (development mode)

---

**End of Backend API Documentation**