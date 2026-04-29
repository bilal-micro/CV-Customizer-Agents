# 🗺️ Module: Services

**Description:** Provides reusable services like LLM integration and shared business logic.
**Goal:** To enable external service integrations and encapsulate common application utilities.
**Directories:** `backend/ats_app/services`
**Files:** 1 | **Functions:** 9

[⬅️ Back to Index](./index.md)

---

## 📄 File: `backend/ats_app/services/llm_service.py`
- **Language:** PYTHON
- **Lines:** 417
- **Classes:** `LLMService` (line 11)
- **Functions:** 9

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self) -> Any` | 12 |  |
| `generate` | `def generate(self, prompt: str, system: str = "", temperature: float = None) -> str` | 25 |  |
| `_generate_ollama` | `def _generate_ollama(self, prompt: str, system: str = "", temperature: float = None) -> str` | 31 |  |
| `_generate_openrouter` | `def _generate_openrouter(self, prompt: str, system: str = "", temperature: float = None) -> str` | 61 |  |
| `_sanitize_json_string` | `def _sanitize_json_string(self, raw: str) -> str` | 116 |  |
| `_is_truncated_json` | `def _is_truncated_json(self, json_str: str) -> bool` | 131 |  |
| `_complete_truncated_json` | `def _complete_truncated_json(self, json_str: str) -> str` | 167 |  |
| `_ensure_dict_result` | `def _ensure_dict_result(self, result) -> dict` | 224 | Ensure the result is always a dict. |
| `generate_json` | `def generate_json(self, prompt: str, system: str = "", temperature: float = None) -> dict` | 246 |  |

---
