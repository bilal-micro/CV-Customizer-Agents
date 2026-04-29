# 🎯 Scope: Add Login option to frontend and backend with username/password authentication. Connect jobs and processes to logged-in users for filtering. Add option for users to provide their API key or select model based on OpenRouter provider model. Maintain existing flow integrity.

**Generated:** 2026-04-29T01:53:49
**Project:** `ATS-Agentic`
**Project Root:** `/home/belal/ATS-Agentic`

---

## 📊 Overview

**Implement user authentication with username/password, associate jobs/processes with users for filtering, and add API key/model selection capabilities while maintaining existing functionality.

| Metric | Value |
|--------|-------|
| **Affected Modules** | 3 |
| **Files to Modify** | 7 |
| **Files to Create** | 5 |
| **Functions to Update** | 13 |
| **Classes to Update** | 8 |

---

## 🏛️ Affected Modules

### 📦 Data Layer
**Reason:** Need to add User model and modify existing models to include user foreign keys and API key/model selection fields.

### 📦 Backend API
**Reason:** Need to implement authentication endpoints, update viewsets to filter by user, and modify serializers to include user context.

### 📦 Frontend Components
**Reason:** Need to add login forms, update existing components to handle authentication, and add UI elements for API key/model selection.

---

## ✏️ Files to Modify

### 📄 `backend/ats_app/models.py`
- **Language:** PYTHON
- **Reason:** Add User model and modify Job and ProcessRun models to include user foreign keys and API key/model selection fields.

**Classes to Update:**

- `Job` — Add user field to associate jobs with specific users.
- `ProcessRun` — Add user field to associate process runs with specific users.

### 📄 `backend/ats_app/serializers.py`
- **Language:** PYTHON
- **Reason:** Create user serializers and update existing serializers to include user context and API key/model selection.

**Classes to Update:**

- `JobSerializer` — Add user field to job serialization.
- `ProcessRunSerializer` — Add user field to process run serialization.
- `JobCreateSerializer` — Set current user when creating jobs.
- `ProcessRunCreateSerializer` — Set current user when creating process runs.

### 📄 `backend/ats_app/views.py`
- **Language:** PYTHON
- **Reason:** Implement authentication endpoints and update viewsets to filter by user.

**Classes to Update:**

- `JobViewSet` — Add user filtering to ensure users can only see their own jobs.
- `ProcessRunViewSet` — Add user filtering to ensure users can only see their own process runs.

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `run_process` | 100 | modify | Add authentication check and ensure process is associated with current user. |
| `get_prompt` | 150 | modify | Add authentication check and ensure process belongs to current user. |
| `submit_manual_latex` | 200 | modify | Add authentication check and ensure process belongs to current user. |
| `continue_iterating` | 250 | modify | Add authentication check and ensure process belongs to current user. |
| `restart` | 300 | modify | Add authentication check and ensure process belongs to current user. |
| `force_complete` | 350 | modify | Add authentication check and ensure process belongs to current user. |

### 📄 `frontend/src/api/index.ts`
- **Language:** JAVASCRIPT
- **Reason:** Add authentication functions and update existing API functions to include authentication headers.

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `createJob` | 10 | modify | Include authentication token in request headers. |
| `getJobs` | 20 | modify | Include authentication token in request headers and filter by user. |
| `runProcess` | 30 | modify | Include authentication token in request headers. |
| `getProcessRuns` | 40 | modify | Include authentication token in request headers and filter by user. |

### 📄 `frontend/src/components/JobForm.tsx`
- **Language:** JAVASCRIPT
- **Reason:** Add API key and model selection fields to the job form.

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `JobForm` | 5 | extend | Add API key and model selection fields to the form. |

### 📄 `frontend/src/components/ProcessList.tsx`
- **Language:** JAVASCRIPT
- **Reason:** Update to only show processes for the current user.

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `ProcessList` | 5 | modify | Filter processes to only show those belonging to the current user. |

### 📄 `backend/ats_app/agents/orchestrator.py`
- **Language:** PYTHON
- **Reason:** Modify agent initialization to use user's API key or selected model.

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `_execute_stage` | 100 | modify | Pass user's API key or selected model to the stage function. |

---

## 🆕 Files to Create

### 📄 `backend/ats_app/authentication.py`
- **Language:** PYTHON
- **Reason:** Create authentication backends, tokens, and utilities for user authentication.
- **Suggested Functions:** `authenticate_user`, `generate_token`, `validate_token`
- **Suggested Classes:** `UserAuthenticationBackend`, `TokenAuthentication`

### 📄 `backend/ats_app/urls.py`
- **Language:** PYTHON
- **Reason:** Add URL patterns for authentication endpoints.
- **Suggested Functions:** `urlpatterns`

### 📄 `frontend/src/components/LoginForm.tsx`
- **Language:** JAVASCRIPT
- **Reason:** Create a login form component for user authentication.
- **Suggested Functions:** `handleSubmit`, `handleInputChange`
- **Suggested Classes:** `LoginForm`

### 📄 `frontend/src/context/AuthContext.tsx`
- **Language:** JAVASCRIPT
- **Reason:** Create authentication context for state management across components.
- **Suggested Functions:** `login`, `logout`, `useAuth`
- **Suggested Classes:** `AuthContext`, `AuthContextProvider`

### 📄 `frontend/src/pages/LoginPage.tsx`
- **Language:** JAVASCRIPT
- **Reason:** Create a login page that uses the LoginForm component.
- **Suggested Functions:** `render`
- **Suggested Classes:** `LoginPage`

---

## 📝 Implementation Notes

- Ensure all database migrations are created when modifying models.
- Implement proper token-based authentication for API security.
- Add error handling for authentication failures and unauthorized access.
- Ensure the frontend properly stores and manages authentication tokens.
- Make sure user data is properly filtered in all API endpoints to prevent data leakage.
- Consider implementing password reset functionality for better user experience.
- Ensure API keys are stored securely and not exposed in client-side code.

---

## ⚠️ Risks & Considerations

- Existing functionality might break if not properly tested with the new authentication system.
- Data exposure could occur if user filtering is not implemented correctly in all viewsets.
- Frontend components might not handle authentication state changes properly, leading to UI issues.
- API key storage on the client-side could pose security risks if not handled properly.
- Adding user associations might impact performance if not properly indexed.

---

## 📋 Implementation Checklist

- [ ] Update class `Job` in `backend/ats_app/models.py` — Add user field to associate jobs with specific users.
- [ ] Update class `ProcessRun` in `backend/ats_app/models.py` — Add user field to associate process runs with specific users.
- [ ] Update class `JobSerializer` in `backend/ats_app/serializers.py` — Add user field to job serialization.
- [ ] Update class `ProcessRunSerializer` in `backend/ats_app/serializers.py` — Add user field to process run serialization.
- [ ] Update class `JobCreateSerializer` in `backend/ats_app/serializers.py` — Set current user when creating jobs.
- [ ] Update class `ProcessRunCreateSerializer` in `backend/ats_app/serializers.py` — Set current user when creating process runs.
- [ ] Modify `run_process` in `backend/ats_app/views.py` — Add authentication check and ensure process is associated with current user.
- [ ] Modify `get_prompt` in `backend/ats_app/views.py` — Add authentication check and ensure process belongs to current user.
- [ ] Modify `submit_manual_latex` in `backend/ats_app/views.py` — Add authentication check and ensure process belongs to current user.
- [ ] Modify `continue_iterating` in `backend/ats_app/views.py` — Add authentication check and ensure process belongs to current user.
- [ ] Modify `restart` in `backend/ats_app/views.py` — Add authentication check and ensure process belongs to current user.
- [ ] Modify `force_complete` in `backend/ats_app/views.py` — Add authentication check and ensure process belongs to current user.
- [ ] Update class `JobViewSet` in `backend/ats_app/views.py` — Add user filtering to ensure users can only see their own jobs.
- [ ] Update class `ProcessRunViewSet` in `backend/ats_app/views.py` — Add user filtering to ensure users can only see their own process runs.
- [ ] Modify `createJob` in `frontend/src/api/index.ts` — Include authentication token in request headers.
- [ ] Modify `getJobs` in `frontend/src/api/index.ts` — Include authentication token in request headers and filter by user.
- [ ] Modify `runProcess` in `frontend/src/api/index.ts` — Include authentication token in request headers.
- [ ] Modify `getProcessRuns` in `frontend/src/api/index.ts` — Include authentication token in request headers and filter by user.
- [ ] Extend `JobForm` in `frontend/src/components/JobForm.tsx` — Add API key and model selection fields to the form.
- [ ] Modify `ProcessList` in `frontend/src/components/ProcessList.tsx` — Filter processes to only show those belonging to the current user.
- [ ] Modify `_execute_stage` in `backend/ats_app/agents/orchestrator.py` — Pass user's API key or selected model to the stage function.
- [ ] Create `backend/ats_app/authentication.py` — Create authentication backends, tokens, and utilities for user authentication.
- [ ] Create `backend/ats_app/urls.py` — Add URL patterns for authentication endpoints.
- [ ] Create `frontend/src/components/LoginForm.tsx` — Create a login form component for user authentication.
- [ ] Create `frontend/src/context/AuthContext.tsx` — Create authentication context for state management across components.
- [ ] Create `frontend/src/pages/LoginPage.tsx` — Create a login page that uses the LoginForm component.
