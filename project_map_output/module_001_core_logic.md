# 🗺️ Module: Core Logic

**Description:** Handles applicant tracking system operations and business rule processing.
**Goal:** Implements ATS functionality like CV matching, keyword analysis, and application orchestration.
**Directories:** `backend/ats_app, backend/ats_app/agents`
**Files:** 15 | **Functions:** 102

[⬅️ Back to Index](./index.md)

---

## 📄 File: `backend/ats_app/admin.py`
- **Language:** PYTHON
- **Lines:** 36
- **Classes:** `StageResultInline` (line 6), `ProcessRunInline` (line 12), `JobAdmin` (line 19), `ProcessRunAdmin` (line 26), `StageResultAdmin` (line 33)
- **Functions:** 0

## 📄 File: `backend/ats_app/agents/ats_rater.py`
- **Language:** PYTHON
- **Lines:** 123
- **Classes:** `ATSRaterAgent` (line 44)
- **Functions:** 4

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 45 |  |
| `run` | `def run(self, job_title: str, job_description: str, latex_cv: str, match_rate: float) -> dict` | 48 |  |
| `evaluate_results` | `def evaluate_results(self, result: dict, match_rate: float) -> tuple[bool, dict]` | 61 |  |
| `get_feedback_for_iteration` | `def get_feedback_for_iteration(self, result: dict, match_rate: float) -> dict` | 100 |  |

---

## 📄 File: `backend/ats_app/agents/cv_matcher.py`
- **Language:** PYTHON
- **Lines:** 326
- **Classes:** `SectionAnalyzerAgent` (line 89), `AnalysisSynthesizerAgent` (line 159), `CVMatcherAgent` (line 194)
- **Functions:** 6

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 90 |  |
| `run` | `def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict` | 93 |  |
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 160 |  |
| `run` | `def run(self, job_title: str, match_rate: float, keyword_results: dict,               section_analysis: dict, strengths: list, weaknesses: list,               detailed_feedback: str = "") -> dict` | 163 |  |
| `__init__` | `def __init__(self, include_advanced_analysis: bool = False, llm_service=None) -> Any` | 195 |  |
| `run` | `def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict` | 221 |  |

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
- **Lines:** 126
- **Classes:** `KeywordExtractorAgent` (line 73)
- **Functions:** 3

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 74 |  |
| `run` | `def run(self, job_title: str, job_description: str) -> dict` | 77 |  |
| `_log_extraction_summary` | `def _log_extraction_summary(self, result: dict) -> None` | 105 |  |

---

## 📄 File: `backend/ats_app/agents/keyword_gap_analyzer.py`
- **Language:** PYTHON
- **Lines:** 287
- **Classes:** `KeywordGapAnalyzerAgent` (line 110)
- **Functions:** 9

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 116 | Initialize keyword gap analyzer. |
| `analyze_gaps` | `def analyze_gaps(self, job_title: str, keywords: Dict, match_results: Dict,                      section_analysis: Dict, prioritization: Dict) -> Dict` | 121 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 161 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 181 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 201 |  |
| `_format_prioritization_for_llm` | `def _format_prioritization_for_llm(self, prioritization: Dict) -> str` | 218 |  |
| `get_immediate_actions` | `def get_immediate_actions(self, gap_analysis: Dict) -> List[str]` | 244 |  |
| `get_critical_gaps` | `def get_critical_gaps(self, gap_analysis: Dict) -> List[Dict]` | 259 |  |
| `get_section_recommendations` | `def get_section_recommendations(self, gap_analysis: Dict) -> Dict[str, Dict]` | 274 |  |

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
- **Lines:** 240
- **Classes:** `KeywordPrioritizerAgent` (line 89)
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 95 | Initialize keyword prioritizer. |
| `prioritize` | `def prioritize(self, job_title: str, keywords: Dict, match_results: Dict,                     section_analysis: Dict) -> Dict` | 100 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 136 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 156 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 189 |  |
| `get_top_priorities` | `def get_top_priorities(self, prioritization: Dict, limit: int = 5) -> List[Dict]` | 206 |  |
| `get_critical_gaps` | `def get_critical_gaps(self, prioritization: Dict) -> List[Dict]` | 228 |  |

---

## 📄 File: `backend/ats_app/agents/match_evaluator.py`
- **Language:** PYTHON
- **Lines:** 241
- **Classes:** `MatchEvaluatorAgent` (line 76)
- **Functions:** 7

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, llm_service=None) -> Any` | 82 | Initialize match evaluator. |
| `run` | `def run(self, job_title: str, keywords: Dict, match_results: Dict,              section_analysis: Dict, latex_cv: str) -> Dict` | 86 |  |
| `_format_keywords_for_llm` | `def _format_keywords_for_llm(self, keywords: Dict) -> str` | 132 |  |
| `_format_match_results_for_llm` | `def _format_match_results_for_llm(self, match_results: Dict) -> str` | 151 |  |
| `_format_section_analysis_for_llm` | `def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str` | 183 |  |
| `get_match_quality_assessment` | `def get_match_quality_assessment(self, evaluation: Dict) -> Dict` | 207 |  |
| `_get_quality_level` | `def _get_quality_level(self, match_rate: float) -> str` | 230 |  |

---

## 📄 File: `backend/ats_app/agents/orchestrator.py`
- **Language:** PYTHON
- **Lines:** 761
- **Classes:** `OrchestratorAgent` (line 21)
- **Functions:** 21

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__init__` | `def __init__(self, user=None) -> Any` | 36 |  |
| `start_process` | `def start_process(self, process_run: ProcessRun) -> None` | 88 |  |
| `_run_iteration_loop` | `def _run_iteration_loop(self, process_run: ProcessRun, job: Job,                             keywords: dict, current_latex: str) -> None` | 139 |  |
| `resume_after_manual_input` | `def resume_after_manual_input(self, process_run: ProcessRun) -> None` | 183 |  |
| `_continue_to_next_iteration` | `def _continue_to_next_iteration(self, process_run: ProcessRun, job: Job,                                   keywords: dict, latex_cv: str, feedback: dict) -> None` | 281 |  |
| `_execute_keyword_extraction` | `def _execute_keyword_extraction(self, process_run: ProcessRun, job: Job) -> dict` | 324 |  |
| `_execute_cv_matching` | `def _execute_cv_matching(self, process_run: ProcessRun, job: Job,                            keywords: dict, latex_cv: str) -> dict` | 331 |  |
| `_execute_cv_update_stage` | `def _execute_cv_update_stage(self, process_run: ProcessRun, job: Job,                                 keywords: dict, latex_cv: str,                                 iteration: int = 1, feedback: dict = None) -> str` | 339 |  |
| `_execute_ats_rating` | `def _execute_ats_rating(self, process_run: ProcessRun, job: Job,                            latex_cv: str, match_result: dict) -> dict` | 393 |  |
| `_execute_stage` | `def _execute_stage(self, process_run: ProcessRun, stage_name: str,                      stage_func) -> dict` | 404 |  |
| `_evaluate_results` | `def _evaluate_results(self, match_result: dict, rating_result: dict) -> dict` | 466 |  |
| `_prepare_feedback_for_next_iteration` | `def _prepare_feedback_for_next_iteration(self, process_run: ProcessRun, rating_result: dict,                                          match_result: dict,                                           evaluation: dict) -> dict` | 489 |  |
| `_get_stage_result_safely` | `def _get_stage_result_safely(self, process_run: ProcessRun, stage_name: str) -> Any` | 522 |  |
| `_get_or_create_stage` | `def _get_or_create_stage(self, process_run: ProcessRun, stage_name: str) -> StageResult` | 549 |  |
| `_should_retry_stage` | `def _should_retry_stage(self, stage: str, result: dict) -> bool` | 557 |  |
| `_rate_stage_result` | `def _rate_stage_result(self, stage: str, result: dict) -> float` | 571 |  |
| `_get_stage_notes` | `def _get_stage_notes(self, stage: str, result: dict) -> str` | 585 |  |
| `_complete_process` | `def _complete_process(self, process_run: ProcessRun, reason: str) -> None` | 597 |  |
| `trigger_manual_iteration` | `def trigger_manual_iteration(self, process_run: ProcessRun) -> bool` | 603 |  |
| `_fail_process` | `def _fail_process(self, process_run: ProcessRun, reason: str) -> None` | 650 |  |
| `restart_from_failure` | `def restart_from_failure(self, process_run: ProcessRun) -> None` | 656 |  |

---

## 📄 File: `backend/ats_app/apps.py`
- **Language:** PYTHON
- **Lines:** 6
- **Classes:** `AtsAppConfig` (line 4)
- **Functions:** 0

## 📄 File: `backend/ats_app/authentication.py`
- **Language:** PYTHON
- **Lines:** 141
- **Functions:** 5

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `register_view` | `def register_view(request) -> Any` | 23 | Register a new user and return JWT tokens for automatic login |
| `login_view` | `def login_view(request) -> Any` | 47 | Login user and return JWT tokens |
| `logout_view` | `def logout_view(request) -> Any` | 79 | Logout user - blacklist the refresh token to invalidate it |
| `profile_view` | `def profile_view(request) -> Any` | 101 | Get or update user profile |
| `change_password_view` | `def change_password_view(request) -> Any` | 128 | Change user password |

---

## 📄 File: `backend/ats_app/models.py`
- **Language:** PYTHON
- **Lines:** 114
- **Classes:** `UserProfile` (line 8), `Meta` (line 28), `Job` (line 36), `Meta` (line 44), `ProcessRun` (line 51), `Meta` (line 73), `StageResult` (line 80), `Meta` (line 108)
- **Functions:** 4

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `__str__` | `def __str__(self) -> Any` | 32 |  |
| `__str__` | `def __str__(self) -> Any` | 47 |  |
| `__str__` | `def __str__(self) -> Any` | 76 |  |
| `__str__` | `def __str__(self) -> Any` | 112 |  |

---

## 📄 File: `backend/ats_app/serializers.py`
- **Language:** PYTHON
- **Lines:** 129
- **Classes:** `UserSerializer` (line 9), `Meta` (line 13), `UserProfileSerializer` (line 27), `Meta` (line 29), `LoginSerializer` (line 37), `PasswordChangeSerializer` (line 43), `StageResultSerializer` (line 61), `Meta` (line 62), `ProcessRunSerializer` (line 67), `Meta` (line 71), `JobSerializer` (line 79), `Meta` (line 83), `JobCreateSerializer` (line 91), `Meta` (line 92), `ProcessRunCreateSerializer` (line 102), `Meta` (line 103), `ManualLatexSubmissionSerializer` (line 114)
- **Functions:** 6

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `create` | `def create(self, validated_data) -> Any` | 20 |  |
| `validate_old_password` | `def validate_old_password(self, value) -> Any` | 48 |  |
| `validate_new_password` | `def validate_new_password(self, value) -> Any` | 54 |  |
| `create` | `def create(self, validated_data) -> Any` | 96 |  |
| `create` | `def create(self, validated_data) -> Any` | 107 |  |
| `validate_latex_content` | `def validate_latex_content(self, value) -> Any` | 117 |  |

---

## 📄 File: `backend/ats_app/views.py`
- **Language:** PYTHON
- **Lines:** 330
- **Classes:** `JobViewSet` (line 70), `ProcessRunViewSet` (line 100), `StageResultViewSet` (line 327)
- **Functions:** 12

| Function | Signature | Line | Description |
|----------|-----------|------|-------------|
| `_run_orchestrator_async` | `def _run_orchestrator_async(process_run_id, user_id=None) -> Any` | 26 |  |
| `_resume_orchestrator_async` | `def _resume_orchestrator_async(process_run_id) -> Any` | 42 |  |
| `_restart_orchestrator_async` | `def _restart_orchestrator_async(process_run_id) -> Any` | 56 |  |
| `get_queryset` | `def get_queryset(self) -> Any` | 75 |  |
| `get_serializer_class` | `def get_serializer_class(self) -> Any` | 79 |  |
| `run_process` | `def run_process(self, request, pk=None) -> Any` | 85 |  |
| `get_queryset` | `def get_queryset(self) -> Any` | 105 |  |
| `get_prompt` | `def get_prompt(self, request, pk=None) -> Any` | 110 | Get the generated prompt from Agent 3 for manual LLM input. |
| `submit_manual_latex` | `def submit_manual_latex(self, request, pk=None) -> Any` | 150 | Submit manually updated LaTeX from external LLM and continue process. |
| `continue_iterating` | `def continue_iterating(self, request, pk=None) -> Any` | 209 | Trigger a new manual iteration after process completion. |
| `restart` | `def restart(self, request, pk=None) -> Any` | 257 | Restart a failed process from the point of failure. |
| `force_complete` | `def force_complete(self, request, pk=None) -> Any` | 294 | Force complete a process without running any agents. |

---
