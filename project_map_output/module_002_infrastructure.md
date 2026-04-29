# 🗺️ Module: Infrastructure

**Description:** Manages data persistence, external service integrations, and project configuration.
**Goal:** Provides database migrations, LLM service connectivity, and routing capabilities.
**Directories:** `backend/ats_app/migrations, backend/ats_app/services, backend, backend/ats_project`
**Files:** 8 | **Functions:** 11

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

## 📄 File: `backend/ats_app/services/llm_service.py`
- **Language:** PYTHON
- **Lines:** 440
- **Classes:** `LLMService` (line 11)
- **Functions:** 9

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, api_key=None, model=None) -> Any` | 12 |  |
| `generate` | `def generate(self, prompt: str, system: str = "", temperature: float = None) -> str` | 50 |  |
| `_generate_ollama` | `def _generate_ollama(self, prompt: str, system: str = "", temperature: float = None) -> str` | 56 |  |
| `_generate_openrouter` | `def _generate_openrouter(self, prompt: str, system: str = "", temperature: float = None) -> str` | 86 |  |
| `_sanitize_json_string` | `def _sanitize_json_string(self, raw: str) -> str` | 141 |  |
| `_is_truncated_json` | `def _is_truncated_json(self, json_str: str) -> bool` | 156 |  |
| `_complete_truncated_json` | `def _complete_truncated_json(self, json_str: str) -> str` | 192 |  |
| `_ensure_dict_result` | `def _ensure_dict_result(self, result) -> dict` | 249 | Ensure the result is always a dict. |
| `generate_json` | `def generate_json(self, prompt: str, system: str = "", temperature: float = None) -> dict` | 271 |  |

---

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
