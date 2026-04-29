# 🗺️ Module: Backend Infrastructure

**Description:** Handles project configuration, URL routing, and database migrations.
**Goal:** Ensures proper backend setup and data schema management.
**Directories:** `backend, backend/ats_project, backend/ats_app/migrations`
**Files:** 6 | **Functions:** 2

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
