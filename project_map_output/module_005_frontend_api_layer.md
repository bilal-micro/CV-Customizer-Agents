# 🗺️ Module: Frontend API Layer

**Description:** Handles API requests and responses to the backend.
**Goal:** Facilitates communication between frontend and backend services.
**Directories:** `frontend/src/api`
**Files:** 1 | **Functions:** 16

[⬅️ Back to Index](./index.md)

---

## 📄 File: `frontend/src/api/index.ts`
- **Language:** JAVASCRIPT
- **Lines:** 96
- **Functions:** 16

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `login` | `export const login = (username: string, password: string) => any` | 47 |  |
| `logout` | `export const logout = (refreshToken: string) => any` | 50 |  |
| `getProfile` | `export const getProfile = () => any` | 53 |  |
| `updateProfile` | `export const updateProfile = (data: { openrouter_api_key?: string; preferred_model?: string }) => any` | 56 |  |
| `register` | `export const register = (username: string, email: string, password: string) => any` | 59 |  |
| `createJob` | `export const createJob = (data: { title: string; description: string; latex_cv: string }) => any` | 62 |  |
| `getJobs` | `export const getJobs = () => any` | 68 |  |
| `getJob` | `export const getJob = (id: string) => any` | 70 |  |
| `runProcess` | `export const runProcess = (jobId: string, maxRetries = 3) => any` | 72 |  |
| `getProcessRuns` | `export const getProcessRuns = () => any` | 78 |  |
| `getProcessRun` | `export const getProcessRun = (id: string) => any` | 80 |  |
| `getPrompt` | `export const getPrompt = (id: string) => any` | 82 |  |
| `submitManualLatex` | `export const submitManualLatex = (id: string, latexContent: string) => any` | 85 |  |
| `continueIterating` | `export const continueIterating = (id: string) => any` | 88 |  |
| `restartProcess` | `export const restartProcess = (id: string) => any` | 91 |  |
| `forceComplete` | `export const forceComplete = (id: string) => any` | 94 |  |

---
