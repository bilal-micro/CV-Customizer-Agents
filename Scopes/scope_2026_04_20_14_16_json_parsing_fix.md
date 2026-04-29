# Scope: JSON Parsing Error Fix

**Date**: April 20, 2026 - 14:16
**Status**: Active
**Priority**: High
**Type**: Bug Fix

---

## 🎯 Objective

Fix JSON parsing errors in the LLM service when the AI returns malformed JSON with invalid escape sequences or truncated responses.

---

## 📋 Problem Statement

**Error Observed**:
```
Strategy 4 (fix incomplete JSON) failed: Invalid \escape: line 14 column 77 (char 724)
JSON parse failed, raw: {
  "ats_score": 92,
  "ats_breakdown": {
    "formatting": 95,
    "keyword_density": 90,
    ...
  },
  "strong_points": [
    "Leveraging Generative AI and cloud-native technologies...",
    "Deep expertise in Artificial In...
```

**Root Causes**:
1. LLM generates JSON with invalid escape sequences (unescaped backslashes)
2. Responses are sometimes truncated mid-string
3. Current parsing strategies don't sanitize escape sequences
4. No handling for truncated JSON responses

---

## 🗺️ Affected Components

### Primary Files

#### 1. `backend/ats_app/services/llm_service.py`
- **Lines to modify**: Add after line 110 (before final fallback)
- **Changes needed**:
  - Add `_sanitize_json_string()` method
  - Add `_detect_truncation()` method
  - Add `_complete_truncated_json()` method
  - Add Strategy 5: Sanitize and parse
  - Add Strategy 6: Handle truncated JSON
  - Update error logging to DEBUG level

#### 2. `backend/ats_app/agents/ats_rater.py`
- **Lines to review**: 6-33 (SYSTEM_PROMPT)
- **Changes needed**: Optional - Consider adding constraints about JSON format

### Secondary Files

#### 3. `Scopes/00_MASTER_INDEX.md`
- **Lines to update**: Add entry for this new scope

#### 4. `Docs/00_MASTER_INDEX.md`
- **Lines to update**: May need to update component reference if significant changes

---

## 📝 Implementation Boundaries

### IN SCOPE

1. Add JSON sanitization strategy to handle invalid escape sequences
2. Add truncation detection and handling strategy
3. Update logging levels to DEBUG for parsing attempts
4. Ensure backward compatibility with existing strategies

### OUT OF SCOPE

1. Modifying LLM prompts (unless critically needed)
2. Changing database schema
3. Modifying API endpoints
4. Frontend changes
5. Changes to other agents (unless JSON parsing is affected)

---

## 🔧 Technical Requirements

### Strategy 5: JSON Sanitization

Must handle:
- Invalid escape sequences like `\n` in JSON strings
- Unescaped backslashes
- Malformed Unicode escapes
- Quote character issues

### Strategy 6: Truncation Handling

Must detect:
- Unclosed strings (ending with `"` but no closing quote)
- Unclosed arrays `[...]`
- Unclosed objects `{...}`
- Truncated mid-word or mid-sentence

### Error Handling

- Log each strategy attempt at DEBUG level
- Preserve original raw response in fallback
- Return partial data when possible
- Clear error messages for debugging

---

## ✅ Success Criteria

1. No more "Invalid \escape" errors in logs
2. Truncated JSON responses are handled gracefully
3. All existing JSON parsing strategies continue to work
4. Parsing failures fall back to raw response with clear error indication
5. System can recover from malformed JSON and continue processing

---

## 🚫 Constraints & Assumptions

### Constraints
- Must not break existing functionality
- Must maintain backward compatibility
- Changes should be isolated to `llm_service.py`
- No external dependencies added

### Assumptions
- LLM responses will generally be valid JSON most of the time
- Truncation is rare but should be handled
- Sanitization should not alter legitimate data

---

## 📊 Risk Assessment

**Low Risk**:
- Adding new strategies won't break existing ones
- Strategies are tried sequentially
- Changes are isolated

**Medium Risk**:
- Sanitization could alter legitimate data
- Need to test edge cases carefully

**Mitigation**:
- Comprehensive DEBUG logging
- Keep original response in fallback
- Test with various JSON formats

---

## 🔄 Dependencies

None - This is a self-contained bug fix.

---

## 📌 Notes

- All changes should be made in `llm_service.py`
- Add comprehensive logging for debugging
- Test with both valid and invalid JSON
- Consider adding unit tests for new strategies

---

**End of Scope Document**