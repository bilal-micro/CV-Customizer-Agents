# 🗺️ Module: Backend Infrastructure

**Description:** Manages database migrations and project configuration.
**Goal:** Supports structural integrity and deployment of the backend.
**Directories:** `backend, backend/ats_app/migrations, backend/ats_project`
**Files:** 7 | **Functions:** 2

[⬅️ Back to Index](./index.md)

---

## 📄 File: `backend/ats_app/migrations/0001_initial.py`
- **Language:** PYTHON
- **Lines:** 63
- **Classes:** `Migration` (line 8)
- **Functions:** 0

## 📄 File: `backend/ats_app/migrations/0002_processrun_iteration_count_and_more.py`
- **Language:** PYTHON
- **Lines:** 49
- **Classes:** `Migration` (line 6)
- **Functions:** 0

## 📄 File: `backend/ats_app/migrations/0003_alter_processrun_max_iterations.py`
- **Language:** PYTHON
- **Lines:** 19
- **Classes:** `Migration` (line 6)
- **Functions:** 0

## 📄 File: `backend/ats_app/migrations/0004_processrun_original_latex.py`
- **Language:** PYTHON
- **Lines:** 19
- **Classes:** `Migration` (line 6)
- **Functions:** 0

## 📄 File: `backend/ats_app/migrations/0006_alter_userprofile_fields.py`
- **Language:** PYTHON
- **Lines:** 23
- **Classes:** `Migration` (line 6)
- **Functions:** 0

## 📄 File: `backend/ats_project/urls.py`
- **Language:** PYTHON
- **Lines:** 43
- **Functions:** 1

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `health_check` | `def health_check(request) -> Any` | 11 | Health check endpoint that doesn't require authentication |

---

## 📄 File: `backend/manage.py`
- **Language:** PYTHON
- **Lines:** 23
- **Functions:** 1

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `main` | `def main() -> Any` | 7 | Run administrative tasks. |

---
