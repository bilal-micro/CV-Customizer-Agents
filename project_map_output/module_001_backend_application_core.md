# 🗺️ Module: Backend Application Core

**Description:** Contains the main application logic, models, views, and authentication.
**Goal:** Implements core ATS business logic and data management.
**Directories:** `backend/ats_app`
**Files:** 6 | **Functions:** 27

[⬅️ Back to Index](./index.md)

---

## 📄 File: `backend/ats_app/admin.py`
- **Language:** PYTHON
- **Lines:** 36
- **Classes:** `StageResultInline` (line 6), `ProcessRunInline` (line 12), `JobAdmin` (line 19), `ProcessRunAdmin` (line 26), `StageResultAdmin` (line 33)
- **Functions:** 0

## 📄 File: `backend/ats_app/apps.py`
- **Language:** PYTHON
- **Lines:** 6
- **Classes:** `AtsAppConfig` (line 4)
- **Functions:** 0

## 📄 File: `backend/ats_app/authentication.py`
- **Language:** PYTHON
- **Lines:** 141
- **Functions:** 5

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `register_view` | `def register_view(request) -> Any` | 23 | Register a new user and return JWT tokens for automatic login |
| `login_view` | `def login_view(request) -> Any` | 47 | Login user and return JWT tokens |
| `logout_view` | `def logout_view(request) -> Any` | 79 | Logout user - blacklist the refresh token to invalidate it |
| `profile_view` | `def profile_view(request) -> Any` | 101 | Get or update user profile |
| `change_password_view` | `def change_password_view(request) -> Any` | 128 | Change user password |

---

## 📄 File: `backend/ats_app/models.py`
- **Language:** PYTHON
- **Lines:** 114
- **Classes:** `UserProfile` (line 8), `Meta` (line 28), `Job` (line 36), `Meta` (line 44), `ProcessRun` (line 51), `Meta` (line 73), `StageResult` (line 80), `Meta` (line 108)
- **Functions:** 4

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__str__` | `def __str__(self) -> Any` | 32 |  |
| `__str__` | `def __str__(self) -> Any` | 47 |  |
| `__str__` | `def __str__(self) -> Any` | 76 |  |
| `__str__` | `def __str__(self) -> Any` | 112 |  |

---

## 📄 File: `backend/ats_app/serializers.py`
- **Language:** PYTHON
- **Lines:** 129
- **Classes:** `UserSerializer` (line 9), `Meta` (line 13), `UserProfileSerializer` (line 27), `Meta` (line 29), `LoginSerializer` (line 37), `PasswordChangeSerializer` (line 43), `StageResultSerializer` (line 61), `Meta` (line 62), `ProcessRunSerializer` (line 67), `Meta` (line 71), `JobSerializer` (line 79), `Meta` (line 83), `JobCreateSerializer` (line 91), `Meta` (line 92), `ProcessRunCreateSerializer` (line 102), `Meta` (line 103), `ManualLatexSubmissionSerializer` (line 114)
- **Functions:** 6

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `create` | `def create(self, validated_data) -> Any` | 20 |  |
| `validate_old_password` | `def validate_old_password(self, value) -> Any` | 48 |  |
| `validate_new_password` | `def validate_new_password(self, value) -> Any` | 54 |  |
| `create` | `def create(self, validated_data) -> Any` | 96 |  |
| `create` | `def create(self, validated_data) -> Any` | 107 |  |
| `validate_latex_content` | `def validate_latex_content(self, value) -> Any` | 117 |  |

---

## 📄 File: `backend/ats_app/views.py`
- **Language:** PYTHON
- **Lines:** 338
- **Classes:** `JobViewSet` (line 74), `ProcessRunViewSet` (line 104), `StageResultViewSet` (line 335)
- **Functions:** 12

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `_run_orchestrator_async` | `def _run_orchestrator_async(process_run_id, user_id=None) -> Any` | 26 |  |
| `_resume_orchestrator_async` | `def _resume_orchestrator_async(process_run_id, user_id=None) -> Any` | 42 |  |
| `_restart_orchestrator_async` | `def _restart_orchestrator_async(process_run_id, user_id=None) -> Any` | 58 |  |
| `get_queryset` | `def get_queryset(self) -> Any` | 79 |  |
| `get_serializer_class` | `def get_serializer_class(self) -> Any` | 83 |  |
| `run_process` | `def run_process(self, request, pk=None) -> Any` | 89 |  |
| `get_queryset` | `def get_queryset(self) -> Any` | 109 |  |
| `get_prompt` | `def get_prompt(self, request, pk=None) -> Any` | 114 | Get the generated prompt from Agent 3 for manual LLM input. |
| `submit_manual_latex` | `def submit_manual_latex(self, request, pk=None) -> Any` | 154 | Submit manually updated LaTeX from external LLM and continue process. |
| `continue_iterating` | `def continue_iterating(self, request, pk=None) -> Any` | 215 | Trigger a new manual iteration after process completion. |
| `restart` | `def restart(self, request, pk=None) -> Any` | 263 | Restart a failed process from the point of failure. |
| `force_complete` | `def force_complete(self, request, pk=None) -> Any` | 302 | Force complete a process without running any agents. |

---
