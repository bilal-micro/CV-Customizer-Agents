# 🗺️ Module: Unclassified

**Description:** Files not matched to any architectural module.
**Goal:** Miscellaneous project functionality.
**Directories:** `backend/ats_app/services, backend/ats_app/agents, frontend/src, backend, backend/ats_app/migrations`
**Files:** 16 | **Functions:** 87

[⬅️ Back to Index](./index.md)

---

## 📄 File: `backend/ats_app/agents/ats_rater.py`
- **Language:** PYTHON
- **Lines:** 118
- **Classes:** `ATSRaterAgent` (line 45)
- **Functions:** 3

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `run` | `def run(self, job_title: str, job_description: str, latex_cv: str, match_rate: float) -> dict` | 46 |  |
| `evaluate_results` | `def evaluate_results(self, result: dict, match_rate: float) -> tuple[bool, dict]` | 56 |  |
| `get_feedback_for_iteration` | `def get_feedback_for_iteration(self, result: dict, match_rate: float) -> dict` | 95 |  |

---

## 📄 File: `backend/ats_app/agents/cv_matcher.py`
- **Language:** PYTHON
- **Lines:** 314
- **Classes:** `SectionAnalyzerAgent` (line 90), `AnalysisSynthesizerAgent` (line 154), `CVMatcherAgent` (line 183)
- **Functions:** 4

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `run` | `def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict` | 91 |  |
| `run` | `def run(self, job_title: str, match_rate: float, keyword_results: dict,               section_analysis: dict, strengths: list, weaknesses: list,               detailed_feedback: str = "") -> dict` | 155 |  |
| `__init__` | `def __init__(self, include_advanced_analysis: bool = False) -> Any` | 184 |  |
| `run` | `def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict` | 209 |  |

---

## 📄 File: `backend/ats_app/agents/cv_updater.py`
- **Language:** PYTHON
- **Lines:** 215
- **Classes:** `CVUpdaterAgent` (line 143)
- **Functions:** 2

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `generate_prompt` | `def generate_prompt(self, job_title: str, keywords: dict, matching_analysis: dict,                          latex_cv: str, iteration_number: int = 1, feedback: dict = None) -> str` | 144 |  |
| `validate_manual_latex` | `def validate_manual_latex(self, latex_content: str) -> dict` | 188 |  |

---

## 📄 File: `backend/ats_app/agents/keyword_extractor.py`
- **Language:** PYTHON
- **Lines:** 121
- **Classes:** `KeywordExtractorAgent` (line 74)
- **Functions:** 2

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `run` | `def run(self, job_title: str, job_description: str) -> dict` | 75 |  |
| `_log_extraction_summary` | `def _log_extraction_summary(self, result: dict) -> None` | 100 |  |

---

## 📄 File: `backend/ats_app/agents/keyword_gap_analyzer.py`
- **Language:** PYTHON
- **Lines:** 284
- **Classes:** `KeywordGapAnalyzerAgent` (line 111)
- **Functions:** 9

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self) -> Any` | 117 | Initialize keyword gap analyzer. |
| `analyze_gaps` | `def analyze_gaps(self, job_title: str, keywords: Dict, match_results: Dict,                      section_analysis: Dict, prioritization: Dict) -> Dict` | 121 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 158 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 178 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 198 |  |
| `_format_prioritization_for_llm` | `def _format_prioritization_for_llm(self, prioritization: Dict) -> str` | 215 |  |
| `get_immediate_actions` | `def get_immediate_actions(self, gap_analysis: Dict) -> List[str]` | 241 |  |
| `get_critical_gaps` | `def get_critical_gaps(self, gap_analysis: Dict) -> List[Dict]` | 256 |  |
| `get_section_recommendations` | `def get_section_recommendations(self, gap_analysis: Dict) -> Dict[str, Dict]` | 271 |  |

---

## 📄 File: `backend/ats_app/agents/keyword_matcher.py`
- **Language:** PYTHON
- **Lines:** 624
- **Classes:** `EnhancedKeywordMatcherAgent` (line 56)
- **Functions:** 16

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self) -> Any` | 63 | Initialize enhanced keyword matcher. |
| `_flatten_keywords` | `def _flatten_keywords(self, keywords: Dict) -> List[Dict]` | 67 |  |
| `match_keywords` | `def match_keywords(self, job_title: str, keywords: Dict, latex_cv: str) -> Dict` | 101 |  |
| `_detect_sections` | `def _detect_sections(self, latex_cv: str) -> Dict[str, int]` | 195 |  |
| `_find_keyword_location` | `def _find_keyword_location(self, latex_cv: str, keyword: str, sections: Dict[str, int]) -> str` | 228 |  |
| `_find_nearest_section` | `def _find_nearest_section(self, line_num: int, sections: Dict[str, int]) -> str` | 254 |  |
| `_find_similar_match` | `def _find_similar_match(self, keyword: str, latex_cv: str, keyword_item: Dict) -> Optional[Dict]` | 275 |  |
| `_is_false_positive` | `def _is_false_positive(self, keyword: str, matched_text: str) -> bool` | 364 |  |
| `_extract_context` | `def _extract_context(self, latex_cv: str, keyword: str, context_length: int = 50) -> str` | 392 |  |
| `_calculate_effectiveness_score` | `def _calculate_effectiveness_score(self, latex_cv_lower: str, keyword_lower: str,                                        location: str, sections: Dict[str, int]) -> float` | 427 |  |
| `_determine_usage_quality` | `def _determine_usage_quality(self, location: str, sections: Dict[str, int],                                   keyword_item: Dict) -> str` | 461 |  |
| `_get_priority_impact` | `def _get_priority_impact(self, priority: int) -> str` | 494 |  |
| `_get_suggested_location` | `def _get_suggested_location(self, category: str) -> str` | 511 |  |
| `_check_synonyms` | `def _check_synonyms(self, keyword: str, latex_cv_lower: str) -> Optional[str]` | 532 |  |
| `_check_quantifications` | `def _check_quantifications(self, keyword: str, latex_cv_lower: str) -> Optional[str]` | 555 |  |
| `get_keyword_effectiveness_summary` | `def get_keyword_effectiveness_summary(self, match_result: Dict) -> Dict` | 590 |  |

---

## 📄 File: `backend/ats_app/agents/keyword_prioritizer.py`
- **Language:** PYTHON
- **Lines:** 237
- **Classes:** `KeywordPrioritizerAgent` (line 90)
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self) -> Any` | 96 | Initialize keyword prioritizer. |
| `prioritize` | `def prioritize(self, job_title: str, keywords: Dict, match_results: Dict,                     section_analysis: Dict) -> Dict` | 100 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 133 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 153 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 186 |  |
| `get_top_priorities` | `def get_top_priorities(self, prioritization: Dict, limit: int = 5) -> List[Dict]` | 203 |  |
| `get_critical_gaps` | `def get_critical_gaps(self, prioritization: Dict) -> List[Dict]` | 225 |  |

---

## 📄 File: `backend/ats_app/agents/match_evaluator.py`
- **Language:** PYTHON
- **Lines:** 235
- **Classes:** `MatchEvaluatorAgent` (line 77)
- **Functions:** 6

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `run` | `def run(self, job_title: str, keywords: Dict, match_results: Dict,              section_analysis: Dict, latex_cv: str) -> Dict` | 83 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 126 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 145 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 177 |  |
| `get_match_quality_assessment` | `def get_match_quality_assessment(self, evaluation: Dict) -> Dict` | 201 |  |
| `_get_quality_level` | `def _get_quality_level(self, match_rate: float) -> str` | 224 |  |

---

## 📄 File: `backend/ats_app/agents/orchestrator.py`
- **Language:** PYTHON
- **Lines:** 731
- **Classes:** `OrchestratorAgent` (line 20)
- **Functions:** 21

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, user=None) -> Any` | 35 |  |
| `start_process` | `def start_process(self, process_run: ProcessRun) -> None` | 58 |  |
| `_run_iteration_loop` | `def _run_iteration_loop(self, process_run: ProcessRun, job: Job,                             keywords: dict, current_latex: str) -> None` | 109 |  |
| `resume_after_manual_input` | `def resume_after_manual_input(self, process_run: ProcessRun) -> None` | 153 |  |
| `_continue_to_next_iteration` | `def _continue_to_next_iteration(self, process_run: ProcessRun, job: Job,                                   keywords: dict, latex_cv: str, feedback: dict) -> None` | 251 |  |
| `_execute_keyword_extraction` | `def _execute_keyword_extraction(self, process_run: ProcessRun, job: Job) -> dict` | 294 |  |
| `_execute_cv_matching` | `def _execute_cv_matching(self, process_run: ProcessRun, job: Job,                            keywords: dict, latex_cv: str) -> dict` | 301 |  |
| `_execute_cv_update_stage` | `def _execute_cv_update_stage(self, process_run: ProcessRun, job: Job,                                 keywords: dict, latex_cv: str,                                 iteration: int = 1, feedback: dict = None) -> str` | 309 |  |
| `_execute_ats_rating` | `def _execute_ats_rating(self, process_run: ProcessRun, job: Job,                            latex_cv: str, match_result: dict) -> dict` | 363 |  |
| `_execute_stage` | `def _execute_stage(self, process_run: ProcessRun, stage_name: str,                      stage_func) -> dict` | 374 |  |
| `_evaluate_results` | `def _evaluate_results(self, match_result: dict, rating_result: dict) -> dict` | 436 |  |
| `_prepare_feedback_for_next_iteration` | `def _prepare_feedback_for_next_iteration(self, process_run: ProcessRun, rating_result: dict,                                          match_result: dict,                                           evaluation: dict) -> dict` | 459 |  |
| `_get_stage_result_safely` | `def _get_stage_result_safely(self, process_run: ProcessRun, stage_name: str) -> Any` | 492 |  |
| `_get_or_create_stage` | `def _get_or_create_stage(self, process_run: ProcessRun, stage_name: str) -> StageResult` | 519 |  |
| `_should_retry_stage` | `def _should_retry_stage(self, stage: str, result: dict) -> bool` | 527 |  |
| `_rate_stage_result` | `def _rate_stage_result(self, stage: str, result: dict) -> float` | 541 |  |
| `_get_stage_notes` | `def _get_stage_notes(self, stage: str, result: dict) -> str` | 555 |  |
| `_complete_process` | `def _complete_process(self, process_run: ProcessRun, reason: str) -> None` | 567 |  |
| `trigger_manual_iteration` | `def trigger_manual_iteration(self, process_run: ProcessRun) -> bool` | 573 |  |
| `_fail_process` | `def _fail_process(self, process_run: ProcessRun, reason: str) -> None` | 620 |  |
| `restart_from_failure` | `def restart_from_failure(self, process_run: ProcessRun) -> None` | 626 |  |

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

## 📄 File: `backend/manage.py`
- **Language:** PYTHON
- **Lines:** 23
- **Functions:** 1

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `main` | `def main() -> Any` | 7 | Run administrative tasks. |

---

## 📄 File: `frontend/src/App.tsx`
- **Language:** JAVASCRIPT
- **Lines:** 130
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `NavLinks` | `function NavLinks() : any` | 12 |  |
| `App` | `function App() : any` | 104 |  |
| `isActive` | `const isActive = (path: string) => any` | 17 |  |
| `handleLogoutClick` | `const handleLogoutClick = () => any` | 19 |  |
| `confirmLogout` | `const confirmLogout = async () => any` | 23 |  |
| `cancelLogout` | `const cancelLogout = () => any` | 33 |  |
| `getUserInitials` | `const getUserInitials = () => any` | 38 |  |

---
