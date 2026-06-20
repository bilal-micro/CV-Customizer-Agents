import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a STRICT and UNFORGIVING ATS (Applicant Tracking System) scoring expert and technical recruiter. Evaluate the provided LaTeX CV against the job description with absolute precision. 

CRITICAL: Respond with ONLY a valid, raw JSON object. No markdown formatting blocks (e.g., ```json), no preambles, no explanations, no text outside the JSON structure.

JSON STRUCTURE:
{
  "ats_score": 0-100 (BE HARSH. 90+ requires perfect alignment),
  "parsing_safety_score": 0-100 (Evaluate LaTeX structure readability),
  "ats_breakdown": {
    "formatting_and_structure": 0-100, 
    "keyword_context_match": 0-100, 
    "action_verbs_and_metrics": 0-100
  },
  "recruiter_appeal": 0-100 (Focus on impact and readability),
  "parsing_risks": ["1-3 technical ATS parsing risks in the LaTeX code"],
  "strong_points": ["1-2 exceptional alignment aspects ONLY"],
  "weak_points": ["2-3 SPECIFIC gaps or formatting failures"],
  "expected_interview_questions": ["2-3 likely technical/behavioral questions"],
  "improvement_suggestions": ["2-3 highly actionable suggestions"],
  "overall_assessment": "50-100 words, BE HONEST about flaws and exact alignment"
}

BE CONCISE: Keep all array items brief. Total response must be lightweight and fast to parse.

STRICT SCORING RULES:
1. Parsing Safety (ATS Fatal Flaws): Penalize heavily (score < 60) if the LaTeX contains complex multi-column layouts (e.g., minipage, tabular used for layout), missing standard section headers (Experience, Education, Skills), or merged contact info blocks.
2. Keyword Context: Do not just count keywords. Penalize if keywords are "stuffed" in a generic skills list but not demonstrated in the experience bullets.
3. Content Quality: Score "action_verbs_and_metrics" below 50 if bullets start with weak phrases ("Responsible for", "Worked on") instead of strong action verbs ("Architected", "Engineered", "Orchestrated") or if they lack quantifiable metrics (%, $, time).
4. Fluff Penalty: Deduct points for subjective, unquantifiable summaries ("Passionate and driven professional").
5. Be UNFORGIVING. Your goal is to find reasons to reject the CV."""

RATING_PROMPT = """Rate the following updated LaTeX CV for ATS parsing compatibility and human recruiter appeal against the provided job requirements. 

Job Title: {title}

Job Description:
{description}

Original Match Rate (Pre-Update): {match_rate}%

Updated LaTeX CV Content:
{latex_cv}

Return ONLY the raw JSON object as instructed."""


class ATSRaterAgent:
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    def run(self, job_title: str, job_description: str, latex_cv: str, match_rate: float) -> dict:
        if not self.llm_service:
            raise ValueError("ATSRaterAgent requires an LLMService instance")
        
        prompt = RATING_PROMPT.format(
            title=job_title,
            description=job_description,
            latex_cv=latex_cv,
            match_rate=match_rate,
        )
        # Use temperature=0 for strict, deterministic, consistent evaluations
        return self.llm_service.generate_json(prompt, SYSTEM_PROMPT, temperature=0)
    
    def evaluate_results(self, result: dict, match_rate: float) -> tuple[bool, dict]:
        """
        Evaluate if CV results are good enough to finish, or if another iteration is needed.
        
        Args:
            result: The result dictionary from run() method
            match_rate: The match rate from CV matching
        
        Returns:
            Tuple of (is_good_enough, feedback_dict)
            - is_good_enough: True if results meet criteria (ATS >= 80 AND match_rate >= 75)
            - feedback_dict: Dictionary with feedback for next iteration
        """
        ats_score = result.get('ats_score', 0.0)
        improvement_suggestions = result.get('improvement_suggestions', [])
        weak_points = result.get('weak_points', [])
        
        # Criteria: ATS score >= 80 AND match rate >= 75
        is_good_enough = ats_score >= 80.0 and match_rate >= 75.0
        
        feedback = {
            'ats_score': ats_score,
            'match_rate': match_rate,
            'meets_criteria': is_good_enough,
            'improvement_suggestions': improvement_suggestions,
            'weak_points': weak_points,
            'overall_assessment': result.get('overall_assessment', ''),
            'reason': ''
        }
        
        if is_good_enough:
            feedback['reason'] = 'CV meets criteria: ATS score >= 80 and match rate >= 75'
            logger.info(f"CV results are good enough - ATS: {ats_score}, Match: {match_rate}")
        else:
            feedback['reason'] = f'CV does not meet criteria - ATS: {ats_score} (needs >= 80), Match: {match_rate} (needs >= 75)'
            logger.info(f"CV results need improvement - ATS: {ats_score}, Match: {match_rate}")
        
        return is_good_enough, feedback
    
    def get_feedback_for_iteration(self, result: dict, match_rate: float) -> dict:
        """
        Get detailed feedback for the next iteration.
        
        Args:
            result: The result dictionary from run() method
            match_rate: The match rate from CV matching
        
        Returns:
            Dictionary with detailed feedback for the next CV update iteration
        """
        is_good, feedback = self.evaluate_results(result, match_rate)
        
        # Add more detailed feedback for iteration
        ats_breakdown = result.get('ats_breakdown', {})
        feedback['ats_breakdown'] = ats_breakdown
        feedback['strong_points'] = result.get('strong_points', [])
        feedback['recruiter_appeal'] = result.get('recruiter_appeal', 0.0)
        
        # Prioritize improvement suggestions
        if feedback['improvement_suggestions']:
            feedback['top_priorities'] = feedback['improvement_suggestions'][:3]
        
        return feedback