# CV Updater: Skill Translation & Analysis Validation Update

## Date: April 18, 2026 (Update)

## Objective
Enhance the CV updater role with "Skill Translation" approach and add analysis validation layer to ensure accuracy of keyword matching.

## Changes Made

### 1. Added CRITICAL ANALYSIS VALIDATION STEP
Both `INITIAL_PROMPT_TEMPLATE` and `ITERATION_PROMPT_TEMPLATE` now include a validation step:

```
CRITICAL ANALYSIS VALIDATION STEP:
Before modifying the CV, you MUST verify the accuracy of the matching analysis:
1. Check each "matched_keyword" - is it genuinely present in the CV?
2. Check each "missing_keyword" - is it truly absent from the CV?
3. If you find errors in the analysis, note them but proceed with the CV update based on your own accurate assessment
4. Trust your own keyword detection over the provided analysis if there are discrepancies
```

**Purpose:**
- Ensures the external LLM verifies the accuracy of the keyword matching analysis
- Allows the external LLM to correct any errors in the matching analysis
- Prevents false positives/negatives from affecting CV updates
- Creates a safeguard against incorrect keyword detection

### 2. Aligned ITERATION_PROMPT_TEMPLATE with INITIAL_PROMPT_TEMPLATE
Both templates now use the same "Skill Translation" approach:

#### CORE PRINCIPLES
- Build ONLY upon the candidate's actual existing experience and skills
- Create compelling narratives that showcase how foundational skills translate to job requirements
- NEVER invent metrics, percentages, tools, or experiences that are not explicitly in the original CV
- Use job keywords to frame and elevate existing work, not to invent new work

#### SKILL TRANSLATION RULES (CRITICAL)
- If a required tool is missing from the CV, DO NOT claim direct experience with it
- INSTEAD, map the missing tool to the candidate's existing architectural knowledge
- Rewrite the bullet point to bridge the two
- Example: Map "Zapier" to "custom webhooks/Celery/message brokers"

#### STANDARD ENGINEERING PRACTICES (SAFE INFERENCE)
- MAY safely infer standard senior engineering practices (documentation, debugging, technical research, etc.)
- Weave soft skills naturally into existing project narratives
- WARNING: Safe inference applies ONLY to general practices and soft skills
- NEVER infer specific technologies, frameworks, or tools unless explicitly found in the original CV

#### IMPORTANT RULES
- 100% TRUTH RATE: Every modification must be traceable back to the original CV content
- Maintain professional, high-impact technical tone
- Elevate technical tone to reflect deep understanding of system design and high-performance backend architecture

## Key Differences from Previous Approach

### Before: Reasonable Inference
- Allowed adding quantifiable impact metrics realistic for the role level
- Allowed elaborating on project details based on project type and candidate's experience
- Risked adding information that wasn't explicitly in the CV

### After: Skill Translation (Current)
- Uses 100% TRUTH RATE - every modification must be traceable to original CV
- Maps missing keywords to existing foundational skills
- Bridges gaps through narrative, not by adding new information
- Only allows safe inference for general engineering practices and soft skills

## Example Transformations

### Example 1: Missing Tool (Zapier)
**CV has:** Custom webhooks, API integrations, message queues
**Job requires:** Zapier experience

**Skill Translation:**
```
"Architected custom event-driven workflows and API integrations, demonstrating 
the foundational system design expertise required to rapidly adopt and deploy 
automation platforms like Zapier."
```

### Example 2: Missing Tool (AWS SQS)
**CV has:** Celery, Redis, message brokers, background tasks
**Job requires:** AWS SQS experience

**Skill Translation:**
```
"Implemented scalable message queuing systems using Celery and Redis, with 
deep understanding of distributed messaging patterns applicable to cloud-native 
solutions like AWS SQS."
```

### Example 3: Safe Inference (Documentation)
**CV has:** "Developed backend API for e-commerce platform"
**Job requires:** Documentation skills

**Safe Inference:**
```
"Developed backend API for e-commerce platform and created comprehensive 
technical documentation to enable cross-functional teams."
```

## Files Modified
- `backend/ats_app/agents/cv_updater.py`
  - Updated `INITIAL_PROMPT_TEMPLATE` (added analysis validation step)
  - Completely rewrote `ITERATION_PROMPT_TEMPLATE` to match initial prompt structure
  - Both now use "Skill Translation" approach instead of "reasonable inferences"

## Impact
- **Improved Accuracy:** External LLM verifies matching analysis before making changes
- **Maintained Truthfulness:** 100% TRUTH RATE ensures all content is traceable to original CV
- **Better Keyword Coverage:** Skill Translation bridges gaps without inventing experience
- **Consistent Approach:** Both initial and iteration prompts use same methodology
- **Reduced Risk:** Safe inference limited to general practices and soft skills only

## Benefits of Analysis Validation Layer
1. **Self-Correction:** External LLM can identify and correct errors in keyword matching
2. **Quality Control:** Ensures CV updates are based on accurate analysis
3. **Reduced False Positives:** Prevents claiming skills that aren't actually present
4. **Reduced False Negatives:** Identifies skills that were incorrectly marked as missing
5. **Improved Trust:** External LLM uses its own judgment when discrepancies exist

## Previous Documentation
- See `Plans/2026-04-18_13:16_CV_UPDATER_IMPROVEMENTS_SUMMARY.md` for initial storytelling approach implementation