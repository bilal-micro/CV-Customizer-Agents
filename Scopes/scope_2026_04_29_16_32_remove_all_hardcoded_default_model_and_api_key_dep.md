# 🎯 Scope: Remove all hardcoded default model and API key dependencies from settings, deprecate Ollama support, and enforce user-provided OpenRouter configuration only

**Generated:** 2026-04-29T16:32:23
**Project:** `ATS-Agentic`
**Project Root:** `/home/belal/ATS-Agentic`

---

## 📊 Overview

**Remove hardcoded model and API key dependencies from settings, deprecate Ollama support, and enforce user-provided OpenRouter configuration only.

| Metric | Value |
|--------|-------|
| **Affected Modules** | 4 |
| **Files to Modify** | 4 |
| **Files to Create** | 2 |
| **Functions to Update** | 4 |
| **Classes to Update** | 3 |

---

## 🏛️ Affected Modules

### 📦 LLM Service
**Reason:** Contains hardcoded configurations and both Ollama and OpenRouter implementations

### 📦 Application Configuration
**Reason:** May contain default settings that need to be removed

### 📦 API Serializers
**Reason:** Need to handle user-provided API configurations

### 📦 Frontend Registration
**Reason:** May need to collect API configuration from users

---

## ✏️ Files to Modify

### 📄 `backend/ats_app/services/llm_service.py`
- **Language:** PYTHON
- **Reason:** Contains hardcoded model and API key dependencies and needs to deprecate Ollama support

**Classes to Update:**

- `LLMService` — Modify to enforce user-provided OpenRouter configuration only

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `__init__` | 1 | refactor | Remove hardcoded default model and API key configurations, make it require user-provided config |
| `_generate_ollama` | 1 | modify | Deprecate Ollama support by adding deprecation warning and possibly removing functionality in future |
| `_generate_openrouter` | 1 | modify | Update to use only user-provided OpenRouter configuration instead of hardcoded values |

### 📄 `backend/ats_app/apps.py`
- **Language:** PYTHON
- **Reason:** May contain hardcoded default settings that need to be removed

**Classes to Update:**

- `AtsAppConfig` — Remove hardcoded default model and API key configurations

### 📄 `backend/ats_app/serializers.py`
- **Language:** PYTHON
- **Reason:** Need to handle user-provided API configurations

**Classes to Update:**

- `UserSerializer` — May need to include API configuration fields like OpenRouter API key

### 📄 `frontend/src/components/RegistrationForm.tsx`
- **Language:** JAVASCRIPT
- **Reason:** May need to collect OpenRouter API configuration from users

| Function | Line | Change Type | Reason |
|----------|------|-------------|--------|
| `handleSubmit` | 1 | modify | Update to handle API configuration submission during registration |

---

## 🆕 Files to Create

### 📄 `backend/ats_app/services/api_config_service.py`
- **Language:** PYTHON
- **Reason:** Create a new service to handle user API configurations
- **Suggested Functions:** `save_user_config`, `get_user_config`, `validate_config`
- **Suggested Classes:** `UserApiConfig`

### 📄 `backend/ats_app/serializers/api_config_serializer.py`
- **Language:** PYTHON
- **Reason:** Create a new serializer for handling API configuration data
- **Suggested Functions:** `validate_api_key`, `validate_model`
- **Suggested Classes:** `ApiConfigSerializer`

---

## 📝 Implementation Notes

- All LLM interactions should use user-provided OpenRouter configuration only
- Ollama support should be deprecated but may remain temporarily for backward compatibility
- API keys should be encrypted when stored in the database
- Proper error handling should be added for invalid configurations

---

## ⚠️ Risks & Considerations

- Breaking existing functionality if not properly deprecated
- Potential security risks if API keys are not properly encrypted
- User experience issues if API configuration is required for all functionality

---

## 📋 Implementation Checklist

- [ ] Refactor `__init__` in `backend/ats_app/services/llm_service.py` — Remove hardcoded default model and API key configurations, make it require user-provided config
- [ ] Modify `_generate_ollama` in `backend/ats_app/services/llm_service.py` — Deprecate Ollama support by adding deprecation warning and possibly removing functionality in future
- [ ] Modify `_generate_openrouter` in `backend/ats_app/services/llm_service.py` — Update to use only user-provided OpenRouter configuration instead of hardcoded values
- [ ] Update class `LLMService` in `backend/ats_app/services/llm_service.py` — Modify to enforce user-provided OpenRouter configuration only
- [ ] Update class `AtsAppConfig` in `backend/ats_app/apps.py` — Remove hardcoded default model and API key configurations
- [ ] Update class `UserSerializer` in `backend/ats_app/serializers.py` — May need to include API configuration fields like OpenRouter API key
- [ ] Modify `handleSubmit` in `frontend/src/components/RegistrationForm.tsx` — Update to handle API configuration submission during registration
- [ ] Create `backend/ats_app/services/api_config_service.py` — Create a new service to handle user API configurations
- [ ] Create `backend/ats_app/serializers/api_config_serializer.py` — Create a new serializer for handling API configuration data
