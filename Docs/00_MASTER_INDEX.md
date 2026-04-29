# ATS-Agentic Master Index

**Purpose**: Central navigation map for all project documentation  
**Last Updated**: April 19, 2026  
**Version**: 1.0

---

## 📋 Quick Start

**New to the project?** Start here:
1. Read `README.md` - Project overview
2. Read this document (`Docs/00_MASTER_INDEX.md`) - Navigation map
3. Use `docs/` for architecture and workflow understanding
4. Use `Scopes/` for task-specific scoping
5. Use `Plans/` for execution plans

---

## 📂 Documentation Structure

```
ATS-Agentic/
├── Docs/                      # Master documentation (this directory)
│   ├── 00_MASTER_INDEX.md     # This file - central navigation
│   ├── backend_models.md       # Database models documentation
│   ├── backend_agents.md       # AI agents documentation
│   ├── backend_api.md         # REST API endpoints
│   └── frontend.md            # Frontend architecture
├── Scopes/                    # Task-specific scoping documents
│   └── scope_*.md            # Bounded task definitions
├── Plans/                     # Execution plans and summaries
│   ├── *_TODO_PLAN.md         # Detailed task plans
│   └── *_EXECUTION_SUMMARY.md # Completed task summaries
├── docs/                      # Existing project docs
│   ├── README.md              # Documentation index
│   ├── ARCHITECTURE.md       # System architecture
│   ├── WORKFLOW.md           # Workflow documentation
│   ├── AGENTS.md             # Agent documentation
│   ├── API.md                # API documentation
│   ├── DATA_MODELS.md        # Data model documentation
│   ├── DEVELOPER_GUIDE.md    # Developer guide
│   └── USER_GUIDE.md         # User guide
├── backend/                   # Django backend
│   ├── ats_app/
│   │   ├── models.py         # Django models
│   │   ├── views.py          # API views
│   │   ├── serializers.py    # DRF serializers
│   │   ├── agents/           # AI agents
│   │   └── services/         # Business logic
│   └── ats_project/
│       ├── settings.py        # Django settings
│       └── urls.py           # URL routing
└── frontend/                  # React frontend
    └── src/
        ├── api/              # API client
        ├── components/       # React components
        ├── pages/            # Page components
        └── types/           # TypeScript types
```

---

## 🗺️ Domain Map

### Core Domains

#### 1. Database & Data Models
**Purpose**: Data persistence and structure  
**Key Files**:
- `backend/ats_app/models.py` (81 lines)
- `Docs/backend_models.md` - Comprehensive documentation

**Models**:
- `Job` - Job posting with CV
- `ProcessRun` - Optimization process instance
- `StageResult` - Individual stage results

**Relationships**:
```
Job (1) ──────┐
                │ has many
                ▼
        ProcessRun (N)
                │ has many
                ▼
        StageResult (N)
```

---

#### 2. AI Agents System
**Purpose**: Intelligent CV optimization workflow  
**Key Files**:
- `backend/ats_app/agents/orchestrator.py` (715 lines) - Main controller
- `backend/ats_app/agents/keyword_extractor.py`
- `backend/ats_app/agents/cv_matcher.py`
- `backend/ats_app/agents/cv_updater.py`
- `backend/ats_app/agents/ats_rater.py`
- `Docs/backend_agents.md` - Comprehensive documentation

**Agent Pipeline**:
```
OrchestratorAgent (Controller)
    │
    ├─► KeywordExtractorAgent (Phase 1)
    │
    ├─► CVMatcherAgent (Phase 1, Phase 2)
    │       ├─► EnhancedKeywordMatcher
    │       ├─► SectionAnalyzer
    │       ├─► MatchEvaluator
    │       └─► AnalysisSynthesizer
    │
    ├─► CVUpdaterAgent (Phase 2)
    │
    └─► ATSRaterAgent (Phase 2)
```

**Workflow Phases**:
- **Phase 1**: Initial Analysis (keyword extraction + initial matching)
- **Phase 2**: Iterative Optimization (up to 3 iterations)

---

#### 3. REST API
**Purpose**: External interface for frontend and clients  
**Key Files**:
- `backend/ats_app/views.py` (300 lines)
- `backend/ats_app/serializers.py`
- `backend/ats_project/urls.py`
- `Docs/backend_api.md` - Comprehensive documentation

**Endpoints**:
```
Health Check
  GET /health/

Jobs
  GET    /api/jobs/
  POST   /api/jobs/
  GET    /api/jobs/{id}/
  POST   /api/jobs/{id}/run_process/

Process Runs
  GET    /api/process-runs/
  GET    /api/process-runs/{id}/
  GET    /api/process-runs/{id}/get_prompt/
  POST   /api/process-runs/{id}/submit_manual_latex/
  POST   /api/process-runs/{id}/continue_iterating/
  POST   /api/process-runs/{id}/restart/

Stage Results
  GET    /api/stage-results/
  GET    /api/stage-results/{id}/
```

---

#### 4. Frontend Application
**Purpose**: User interface for CV optimization  
**Key Files**:
- `frontend/src/api/index.ts` (58 lines) - API client
- `frontend/src/components/ProcessTracker.tsx` (483 lines)
- `frontend/src/components/JobForm.tsx`
- `frontend/src/components/KeywordDetails.tsx`
- `frontend/src/components/KeywordExtractionDisplay.tsx`
- `frontend/src/components/ProcessList.tsx`
- `frontend/src/pages/ProcessDetail.tsx`
- `Docs/frontend.md` - Comprehensive documentation

**Components**:
- `JobForm` - Create new jobs
- `ProcessTracker` - Display process progress
- `KeywordDetails` - Detailed keyword information
- `KeywordExtractionDisplay` - Extracted keywords display
- `ProcessList` - List all processes
- `ProcessDetail` - Detailed process view

**State Management**:
- React hooks (useState, useEffect, useCallback, useMemo)
- No global state library (development mode)

---

## 📊 Component Reference

### Backend Components

#### Models
| Model | Table | Purpose | Fields |
|-------|-------|---------|--------|
| Job | ats_app_job | Job posting | id, title, description, latex_cv, created_at |
| ProcessRun | ats_app_processrun | Process instance | id, job, status, iteration_count, max_iterations, manual_latex_input, etc. |
| StageResult | ats_app_stageresult | Stage output | id, process_run, stage, status, result, rating, notes, etc. |

#### Agents
| Agent | File | Phase | Output |
|-------|------|-------|--------|
| KeywordExtractorAgent | keyword_extractor.py | 1 | Keywords with priorities |
| CVMatcherAgent | cv_matcher.py | 1, 2 | Match rate, analysis |
| CVUpdaterAgent | cv_updater.py | 2 | Prompt for external LLM |
| ATSRaterAgent | ats_rater.py | 2 | ATS score, breakdown |

#### API Views
| ViewSet | Actions | Purpose |
|---------|---------|---------|
| JobViewSet | list, create, retrieve, run_process | Job management |
| ProcessRunViewSet | list, retrieve, get_prompt, submit_manual_latex, continue_iterating, restart | Process management |
| StageResultViewSet | list, retrieve | Stage results |

### Frontend Components

| Component | File | Props | Purpose |
|-----------|-------|-------|---------|
| JobForm | JobForm.tsx | None | Create jobs |
| ProcessTracker | ProcessTracker.tsx | stages: StageResult[] | Track progress |
| KeywordDetails | KeywordDetails.tsx | matchedKeywords, missingKeywords | Show keyword details |
| KeywordExtractionDisplay | KeywordExtractionDisplay.tsx | items, label, category | Display extracted keywords |
| ProcessList | ProcessList.tsx | None | List all processes |
| ProcessDetail | ProcessDetail.tsx | None | Show process details |

---

## 🔄 Workflow Reference

### Complete CV Optimization Flow

```
1. User creates Job (JobForm)
   ↓
2. User starts Process (run_process)
   ↓
3. OrchestratorAgent.start_process()
   ↓
4. Phase 1: Initial Analysis
   ├─ KeywordExtractorAgent
   └─ CVMatcherAgent
   ↓
5. Phase 2: Iterative Loop
   ├─ CVUpdaterAgent.generate_prompt()
   ├─ [Pause for Manual Input]
   ├─ User submits LaTeX (submit_manual_latex)
   ├─ OrchestratorAgent.resume_after_manual_input()
   ├─ CVMatcherAgent (re-match)
   ├─ ATSRaterAgent
   └─ Evaluation (continue or complete)
   ↓
6. User views results (ProcessTracker)
   ↓
7. Optional: Continue iterating (continue_iterating)
   ↓
8. Complete
```

### State Transitions

**ProcessRun States**:
```
pending → running → awaiting_manual_input → running → completed
                    ↓
                   failed → (restart) → running
```

**StageResult States**:
```
pending → running → completed
              ↓
             failed → (restart) → pending → running → completed
```

---

## 🔍 Finding Information

### By Domain

| Domain | Documentation | Code |
|--------|---------------|------|
| Database | `Docs/backend_models.md` | `backend/ats_app/models.py` |
| AI Agents | `Docs/backend_agents.md` | `backend/ats_app/agents/` |
| API | `Docs/backend_api.md` | `backend/ats_app/views.py` |
| Frontend | `Docs/frontend.md` | `frontend/src/` |

### By Task

| Task | Where to Look |
|------|---------------|
| Create new job | `frontend/src/components/JobForm.tsx` + `POST /api/jobs/` |
| Start optimization | `POST /api/jobs/{id}/run_process/` + `OrchestratorAgent.start_process()` |
| Get prompt for LLM | `GET /api/process-runs/{id}/get_prompt/` |
| Submit updated CV | `POST /api/process-runs/{id}/submit_manual_latex/` |
| View process progress | `frontend/src/components/ProcessTracker.tsx` |
| Continue iterating | `POST /api/process-runs/{id}/continue_iterating/` |
| Restart failed process | `POST /api/process-runs/{id}/restart/` |

### By Component

| Component | Documentation | Location |
|-----------|---------------|----------|
| Job Model | `Docs/backend_models.md` | `backend/ats_app/models.py:6-18` |
| ProcessRun Model | `Docs/backend_models.md` | `backend/ats_app/models.py:20-46` |
| OrchestratorAgent | `Docs/backend_agents.md` | `backend/ats_app/agents/orchestrator.py` |
| KeywordExtractorAgent | `Docs/backend_agents.md` | `backend/ats_app/agents/keyword_extractor.py` |
| CVMatcherAgent | `Docs/backend_agents.md` | `backend/ats_app/agents/cv_matcher.py` |
| CVUpdaterAgent | `Docs/backend_agents.md` | `backend/ats_app/agents/cv_updater.py` |
| ATSRaterAgent | `Docs/backend_agents.md` | `backend/ats_app/agents/ats_rater.py` |
| ProcessTracker | `Docs/frontend.md` | `frontend/src/components/ProcessTracker.tsx` |
| API Client | `Docs/frontend.md` | `frontend/src/api/index.ts` |

---

## 📝 Documentation Index

### New Documentation (Docs/)

| File | Purpose | Lines |
|------|---------|-------|
| `00_MASTER_INDEX.md` | This file - central navigation | ~400 |
| `backend_models.md` | Database models documentation | ~200 |
| `backend_agents.md` | AI agents documentation | ~300 |
| `backend_api.md` | REST API documentation | ~350 |
| `frontend.md` | Frontend architecture documentation | ~400 |

### Existing Documentation (docs/)

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Documentation index | Active |
| `ARCHITECTURE.md` | System architecture | Active |
| `WORKFLOW.md` | Workflow documentation | Active |
| `AGENTS.md` | Agent documentation | Active |
| `API.md` | API documentation | Active |
| `DATA_MODELS.md` | Data model documentation | Active |
| `DEVELOPER_GUIDE.md` | Developer guide | Active |
| `USER_GUIDE.md` | User guide | Active |

---

## 🎯 Quick Reference

### Success Criteria

The optimization completes when:
- **ATS Score** ≥ 80%
- **Match Rate** ≥ 75%
- **Recruiter Appeal** ≥ 75%

OR
- **Max Iterations** reached (default: 3)

### Stage Order

1. `keyword_extraction` (Phase 1, once)
2. `cv_matching` (Phase 1, then Phase 2 per iteration)
3. `cv_update` (Phase 2, per iteration)
4. `ats_rating` (Phase 2, per iteration)

### Configuration Files

| File | Purpose |
|------|---------|
| `backend/.env` | Environment variables (DEBUG, SECRET_KEY, OLLAMA_HOST, OLLAMA_MODEL) |
| `backend/requirements.txt` | Python dependencies |
| `backend/ats_project/settings.py` | Django settings |
| `frontend/package.json` | Node.js dependencies |
| `frontend/vite.config.ts` | Vite configuration |

---

## 🔗 External Services

### Ollama (LLM)
- **URL**: `http://localhost:11434`
- **Model**: `llama3.1`
- **Purpose**: AI-powered analysis and generation
- **Health Check**: `curl http://localhost:11434/api/tags`

---

## 🚀 Development Commands

### Backend

```bash
cd backend
python manage.py runserver      # Start dev server
python manage.py check          # Check system
python manage.py showmigrations # Show migrations
python manage.py makemigrations # Create migrations
python manage.py migrate        # Apply migrations
```

### Frontend

```bash
cd frontend
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Production build
npm run preview  # Preview production build
```

### Ollama

```bash
ollama serve              # Start Ollama service
ollama list               # List available models
ollama pull llama3.1     # Pull model
curl http://localhost:11434/api/tags  # Check service
```

---

## 📚 Additional Resources

- **Project README**: `README.md`
- **Setup Status**: `SETUP_STATUS.md`
- **Start Script**: `start.sh`
- **Excalidraw Diagrams**: 
  - `state_transitions.excalidraw.json`
  - `workflow_detailed.excalidraw.json`
  - `workflow_simple.excalidraw.json`

---

## 🔄 Maintaining This Index

**When adding new features**:
1. Update the Domain Map section
2. Add to Component Reference tables
3. Update Workflow Reference if applicable
4. Add to Finding Information sections
5. Update this document's version and date

**When modifying existing features**:
1. Update relevant component tables
2. Update file locations and line numbers
3. Update documentation references
4. Update this document's version and date

---

## 📊 Statistics

- **Total Documentation Files**: 13 (5 new + 8 existing)
- **Backend Lines of Code**: ~2,000+
- **Frontend Lines of Code**: ~1,500+
- **Total Components**: 11 (5 backend agents + 6 frontend components)
- **API Endpoints**: 13
- **Database Models**: 3
- **Status**: Production Ready

---

**End of Master Index**

*This index is the single source of truth for project navigation. Always check here first when looking for information.*