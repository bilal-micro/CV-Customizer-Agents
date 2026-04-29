# Backend AI Agents

**Purpose**: AI agents for CV optimization workflow  
**Location**: `backend/ats_app/agents/`  

---

## Agent Overview

The ATS-Agentic system uses a multi-agent architecture where each agent has a specific responsibility in the CV optimization pipeline.

### Agent Pipeline

```
OrchestratorAgent (Controller)
    │
    ├─► KeywordExtractorAgent (Phase 1)
    │
    ├─► CVMatcherAgent (Phase 1, Phase 2)
    │       ├─► EnhancedKeywordMatcher
    │       ├─► SectionAnalyzer
    │       ├─► MatchEvaluator
    │       └─► AnalysisSynthesizer
    │
    ├─► CVUpdaterAgent (Phase 2)
    │
    └─► ATSRaterAgent (Phase 2)
```

---

## 1. OrchestratorAgent

**File**: `orchestrator.py`  
**Purpose**: Main workflow controller that orchestrates all agents  
**Lines**: 1-715

### Key Methods

#### `start_process(process_run: ProcessRun) -> None`
**Input**: ProcessRun object  
**Output**: None (saves state to database)  
**Purpose**: Start a new CV optimization process  
**Flow**:
1. Set status to 'running'
2. Execute Phase 1: Keyword Extraction
3. Execute Phase 1: CV Matching
4. Start Phase 2: Iteration Loop
5. Generate prompt for external LLM
6. Pause for manual input

#### `resume_after_manual_input(process_run: ProcessRun) -> None`
**Input**: ProcessRun object  
**Output**: None (saves state to database)  
**Purpose**: Resume process after user submits updated LaTeX  
**Flow**:
1. Set status to 'running'
2. Re-match CV with new LaTeX
3. Rate CV with ATS analysis
4. Evaluate results
5. Continue or complete based on criteria

#### `trigger_manual_iteration(process_run: ProcessRun) -> bool`
**Input**: ProcessRun object  
**Output**: Boolean (success/failure)  
**Purpose**: Trigger additional iteration after completion  
**Flow**:
1. Increment max_iterations
2. Generate new prompt with feedback
3. Set status to 'awaiting_manual_input'

#### `restart_from_failure(process_run: ProcessRun) -> None`
**Input**: ProcessRun object  
**Output**: None (saves state to database)  
**Purpose**: Restart failed process from point of failure  
**Flow**:
1. Identify failed stage
2. Reset failed and subsequent stages to 'pending'
3. Resume from failed stage
4. Preserve all completed stage results

---

## 2. KeywordExtractorAgent

**File**: `keyword_extractor.py`  
**Purpose**: Extract prioritized keywords from job description  
**Phase**: Phase 1 (one-time)

### Run Method

#### `run(job_title: str, job_description: str) -> dict`
**Input**: 
- `job_title`: String (e.g., "Senior Backend Developer")
- `job_description`: String (full job posting text)

**Output**: 
```json
{
  "hard_skills": [
    {
      "skill": "Python",
      "priority": 10,
      "category": "programming",
      "placement_hints": ["skills", "experience"],
      "confidence": 0.95
    }
  ],
  "soft_skills": [...],
  "qualifications": [...],
  "must_have": [...],
  "nice_to_have": [...],
  "job_notes": "Summary of job requirements..."
}
```

**Process**:
1. Analyze job description with LLM
2. Extract hard skills (technical)
3. Extract soft skills (interpersonal)
4. Extract qualifications (education, certifications)
5. Categorize as must-have vs nice-to-have
6. Prioritize keywords (1-10 scale)
7. Suggest placement in CV

---

## 3. CVMatcherAgent

**File**: `cv_matcher.py`  
**Purpose**: Orchestrate CV matching against keywords  
**Phase**: Phase 1, Phase 2 (per iteration)

### Sub-Agents

1. **EnhancedKeywordMatcher** - Match keywords with context
2. **SectionAnalyzer** - Score each CV section
3. **MatchEvaluator** - Calculate match rate
4. **AnalysisSynthesizer** - Generate human-readable summary

### Run Method

#### `run(job_title: str, keywords: dict, latex_cv: str) -> dict`
**Input**:
- `job_title`: String
- `keywords`: Dictionary (from KeywordExtractorAgent)
- `latex_cv`: String (LaTeX CV content)

**Output**:
```json
{
  "match_rate": 65.5,
  "section_analysis": {
    "summary": {"relevance": 0.8, "density": 0.7},
    "experience": {"relevance": 0.9, "density": 0.8},
    "education": {"relevance": 0.6, "density": 0.5},
    "skills": {"relevance": 0.95, "density": 0.9}
  },
  "matched_keywords": [
    {"keyword": "Python", "found_in": "experience", "context": "..."}
  ],
  "missing_keywords": [
    {"keyword": "AWS", "importance": 8, "priority": "must_have"}
  ],
  "strengths": [
    "Strong Python experience",
    "Well-structured experience section"
  ],
  "weaknesses": [
    "Missing cloud experience",
    "Limited quantifiable metrics"
  ],
  "matching_notes": "Overall CV shows good alignment but needs improvement in..."
}
```

**Process**:
1. Parse LaTeX CV into sections
2. Match keywords with context
3. Score each section for relevance and density
4. Calculate overall match rate (0-100)
5. Identify strengths and weaknesses
6. Generate actionable feedback

---

## 4. CVUpdaterAgent

**File**: `cv_updater.py`  
**Purpose**: Generate prompts for external LLM  
**Phase**: Phase 2 (per iteration)

### Key Methods

#### `generate_prompt(job_title: str, keywords: dict, matching_analysis: dict, latex_cv: str, iteration_number: int, feedback: dict = None) -> str`
**Input**:
- `job_title`: String
- `keywords`: Dictionary (from KeywordExtractorAgent)
- `matching_analysis`: Dictionary (from CVMatcherAgent)
- `latex_cv`: String (current LaTeX CV)
- `iteration_number`: Integer (current iteration)
- `feedback`: Dictionary (optional, from previous iteration)

**Output**: String (formatted prompt for external LLM)

**Prompt Structure**:
```
You are an expert CV writer. Please optimize this LaTeX CV for the position of {job_title}.

KEYWORDS TO INCLUDE:
{formatted_keywords}

CURRENT CV ANALYSIS:
- Match Rate: {match_rate}%
- Strengths: {strengths}
- Weaknesses: {weaknesses}

CURRENT CV:
{latex_cv}

INSTRUCTIONS:
1. Incorporate missing keywords
2. Address identified weaknesses
3. Maintain professional tone
4. Keep LaTeX formatting valid

FEEDBACK FROM PREVIOUS ITERATION:
{feedback}

Please provide the optimized LaTeX CV.
```

#### `validate_manual_latex(latex_content: str) -> dict`
**Input**: String (LaTeX content)  
**Output**: 
```json
{
  "valid": true,
  "error": null
}
```

**Validation Checks**:
- Contains `\documentclass`
- Contains `\begin{document}` and `\end{document}`
- No unclosed braces/brackets
- No invalid LaTeX commands

---

## 5. ATSRaterAgent

**File**: `ats_rater.py`  
**Purpose**: Rate CV against ATS standards  
**Phase**: Phase 2 (per iteration)

### Run Method

#### `run(job_title: str, job_description: str, latex_cv: str, match_rate: float) -> dict`
**Input**:
- `job_title`: String
- `job_description`: String
- `latex_cv`: String (LaTeX CV)
- `match_rate`: Float (from CVMatcherAgent)

**Output**:
```json
{
  "ats_score": 78.5,
  "ats_breakdown": {
    "keyword_density": 0.75,
    "formatting": 0.85,
    "readability": 0.80,
    "completeness": 0.70
  },
  "recruiter_appeal": 76.0,
  "strong_points": [
    "Good keyword density",
    "Clean formatting",
    "Clear structure"
  ],
  "weak_points": [
    "Missing quantifiable metrics",
    "Could improve section ordering"
  ],
  "improvement_suggestions": [
    "Add specific project outcomes",
    "Include more measurable achievements"
  ],
  "overall_assessment": "CV shows good ATS compatibility with room for improvement..."
}
```

**Rating Criteria**:
1. **Keyword Density** (0-100): How well keywords are integrated
2. **Formatting** (0-100): ATS-friendly formatting
3. **Readability** (0-100): Clear and concise language
4. **Completeness** (0-100): All required sections present

**ATS Score Calculation**: Weighted average of breakdown scores


---

## LLM Service

**File**: `backend/ats_app/services/llm_service.py`

The LLM service provides a unified interface for interacting with Ollama (the local LLM service), with robust JSON parsing capabilities.

### Configuration

The service is configured via Django settings:
- `OLLAMA_BASE_URL`: Base URL for Ollama API (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Model to use (default: `llama3.1`)

### Methods

#### `generate(prompt: str, system: str = "", temperature: float = None) -> str`

Generate text from the LLM.

**Parameters:**
- `prompt`: The prompt to send to the LLM
- `system`: System prompt (optional)
- `temperature`: Sampling temperature (optional, default: 0.3)

**Returns:** Generated text as a string

#### `generate_json(prompt: str, system: str = "", temperature: float = None) -> dict`

Generate structured JSON output from the LLM.

**Parameters:**
- `prompt`: The prompt to send to the LLM
- `system`: System prompt (optional)
- `temperature`: Sampling temperature (optional, default: 0.3)

**Returns:** Parsed JSON as a dictionary

**Parsing Strategies:**

The method uses six fallback strategies to extract valid JSON from LLM responses:

1. **Strategy 1**: Direct JSON parse
   - Attempts to parse the raw response directly
   
2. **Strategy 2**: Find JSON in markdown blocks
   - Extracts JSON between `{` and `}` delimiters
   
3. **Strategy 3**: Extract from code blocks
   - Searches for JSON within markdown code blocks
   
4. **Strategy 4**: Fix incomplete JSON
   - Adds missing closing brackets and braces
   
5. **Strategy 5**: Sanitize JSON string
   - Handles invalid escape sequences in JSON strings
   - Escapes unescaped backslashes properly
   - Fixes malformed Unicode escapes
   
6. **Strategy 6**: Handle truncated JSON
   - Detects and completes truncated JSON responses
   - Closes unclosed strings, arrays, and objects
   - Smart completion for mid-sentence truncations

**Helper Methods:**

- `_sanitize_json_string(raw: str) -> str`: Sanitizes JSON strings by fixing invalid escape sequences
- `_is_truncated_json(json_str: str) -> bool`: Detects if JSON is truncated
- `_complete_truncated_json(json_str: str) -> str`: Attempts to complete truncated JSON

**Error Handling:**

If all strategies fail, the method returns:
```python
{
    "raw_response": raw,
    "parse_error": "Failed to extract valid JSON"
}
```

This allows agents to handle parsing failures gracefully. All parsing attempts are logged at DEBUG level for troubleshooting.

---

## Execution Order

### Phase 1: Initial Analysis (One-time)
```
1. KeywordExtractorAgent
   ↓
2. CVMatcherAgent
   ├─ EnhancedKeywordMatcher
   ├─ SectionAnalyzer
   ├─ MatchEvaluator
   └─ AnalysisSynthesizer
```

### Phase 2: Iterative Optimization (Per Iteration)
```
1. CVUpdaterAgent (generate prompt)
   ↓
   [Manual: User submits LaTeX]
   ↓
2. CVMatcherAgent (re-match)
   ├─ EnhancedKeywordMatcher
   ├─ SectionAnalyzer
   ├─ MatchEvaluator
   └─ AnalysisSynthesizer
   ↓
3. ATSRaterAgent (rate CV)
   ↓
4. Evaluation (Orchestrator)
   ├─ Meets criteria? → Complete
   ├─ Max iterations? → Complete
   └─ Need improvement? → Next iteration
```

---

## Success Criteria

The optimization completes when:
- **ATS Score** ≥ 80%
- **Match Rate** ≥ 75%
- **Recruiter Appeal** ≥ 75%

OR
- **Max Iterations** reached (default: 3)

---

## Error Handling

Each agent handles:
- LLM timeout (retries with fallback)
- Parse errors (returns error in result)
- Invalid inputs (validates before processing)
- API failures (logs and marks stage as failed)

---

**End of Backend Agents Documentation**