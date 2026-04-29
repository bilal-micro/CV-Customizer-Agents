# Backend Data Models

**Purpose**: Database models for the ATS-Agentic system  
**Location**: `backend/ats_app/models.py`  
**Lines**: 1-81

---

## Models Overview

### 1. Job Model

**Purpose**: Represents a job posting with associated CV  
**Table**: `ats_app_job`

**Fields**:
- `id` (UUIDField, Primary Key) - Unique identifier
- `title` (CharField, max 500) - Job title
- `description` (TextField) - Full job description
- `latex_cv` (TextField) - LaTeX CV content
- `created_at` (DateTimeField, auto_now_add) - Creation timestamp

**Meta**:
- Ordering: `['-created_at']` (newest first)

**Methods**:
- `__str__`: Returns job title

**Relationships**:
- Has many ProcessRuns (related_name='process_runs')

---

### 2. ProcessRun Model

**Purpose**: Represents a CV optimization process run for a job  
**Table**: `ats_app_processrun`

**Status Choices**:
- `pending` - Initial state, not started
- `running` - Actively processing
- `awaiting_manual_input` - Waiting for user input
- `completed` - Successfully finished
- `failed` - Error occurred

**Fields**:
- `id` (UUIDField, Primary Key) - Unique identifier
- `job` (ForeignKey to Job) - Associated job
- `status` (CharField, choices=STATUS_CHOICES) - Current status (default: 'pending')
- `retry_count` (PositiveIntegerField, default=0) - Number of retries attempted
- `max_retries` (PositiveIntegerField, default=3) - Maximum allowed retries
- `iteration_count` (PositiveIntegerField, default=0) - Current iteration number
- `max_iterations` (PositiveIntegerField, default=5) - Maximum iterations allowed
- `manual_latex_input` (TextField, blank=True) - User-submitted LaTeX
- `original_latex` (TextField, blank=True) - Original LaTeX for comparison
- `created_at` (DateTimeField, auto_now_add) - Creation timestamp
- `updated_at` (DateTimeField, auto_now=True) - Last update timestamp

**Meta**:
- Ordering: `['-created_at']` (newest first)

**Methods**:
- `__str__`: Returns "ProcessRun {id} - {status}"

**Relationships**:
- Belongs to Job (related_name='process_runs')
- Has many StageResults (related_name='stage_results')

---

### 3. StageResult Model

**Purpose**: Represents results from individual processing stages  
**Table**: `ats_app_stageresult`

**Stage Choices**:
- `keyword_extraction` - Extract keywords from job description
- `cv_matching` - Match CV against keywords
- `cv_update` - Generate prompt for external LLM
- `ats_rating` - Rate CV against ATS standards

**Status Choices**:
- `pending` - Not started
- `running` - Currently executing
- `completed` - Successfully finished
- `failed` - Error occurred

**Fields**:
- `id` (UUIDField, Primary Key) - Unique identifier
- `process_run` (ForeignKey to ProcessRun) - Associated process
- `stage` (CharField, choices=STAGE_CHOICES) - Stage name
- `status` (CharField, choices=STATUS_CHOICES, default='pending') - Stage status
- `result` (JSONField, default=dict, blank=True) - Stage output data
- `rating` (FloatField, null=True, blank=True) - Stage quality rating (0-100)
- `notes` (TextField, blank=True) - Human-readable notes
- `iteration_notes` (TextField, blank=True) - Notes specific to iteration
- `manual_feedback` (TextField, blank=True) - Feedback from manual iteration
- `iteration_number` (IntegerField, default=0) - Iteration number for this result
- `created_at` (DateTimeField, auto_now_add) - Creation timestamp
- `updated_at` (DateTimeField, auto_now=True) - Last update timestamp

**Meta**:
- Ordering: `['created_at']` (oldest first)
- unique_together: `['process_run', 'stage']` - One result per stage per process

**Methods**:
- `__str__`: Returns "{stage} - {status}"

**Relationships**:
- Belongs to ProcessRun (related_name='stage_results')

---

## Data Flow

```
Job (1) ──────┐
                │
                │ has many
                ▼
        ProcessRun (N)
                │
                │ has many
                ▼
        StageResult (N)
```

**Unique Constraint**: One StageResult per stage per ProcessRun (e.g., only one 'cv_matching' result per process)

---

## State Machine (ProcessRun)

**Transitions**:
1. `pending` → `running` (User starts process)
2. `running` → `awaiting_manual_input` (Prompt generated)
3. `awaiting_manual_input` → `running` (User submits LaTeX)
4. `running` → `completed` (Criteria met or max iterations)
5. `running` → `failed` (Error occurs)
6. `completed` → `running` (User continues iterating)
7. `awaiting_manual_input` → `failed` (Error occurs)

---

## Stage Order

Stages execute in this order:
1. `keyword_extraction` (once, Phase 1)
2. `cv_matching` (once in Phase 1, then per iteration)
3. `cv_update` (per iteration, generates prompt)
4. `ats_rating` (per iteration, after cv_matching)

---

## Result Data Structure

### Keyword Extraction Result
```json
{
  "hard_skills": [...],
  "soft_skills": [...],
  "keywords": [...],
  "job_notes": "..."
}
```

### CV Matching Result
```json
{
  "match_rate": 75.5,
  "matched_keywords": [...],
  "missing_keywords": [...],
  "strengths": [...],
  "weaknesses": [...],
  "matching_notes": "..."
}
```

### CV Update Result
```json
{
  "prompt": "You are an expert CV writer...",
  "iteration_number": 1,
  "update_notes": "Prompt generated for iteration 1"
}
```

### ATS Rating Result
```json
{
  "ats_score": 85.0,
  "ats_breakdown": {
    "keyword_density": 0.75,
    "formatting": 0.85,
    "readability": 0.80,
    "completeness": 0.70
  },
  "recruiter_appeal": 82.0,
  "strong_points": [...],
  "weak_points": [...],
  "improvement_suggestions": [...],
  "overall_assessment": "CV is well-optimized..."
}
```

---

**End of Backend Models Documentation**