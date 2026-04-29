# 🗺️ Module: Backend Services

**Description:** Provides integration services including LLM communication and data processing utilities.
**Goal:** Abstracts external service interactions and enables complex data transformations.
**Directories:** `backend/ats_app/services`
**Files:** 1 | **Functions:** 9

[⬅️ Back to Index](./index.md)

---

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
