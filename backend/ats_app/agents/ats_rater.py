import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a STRICT ATS scoring expert. Evaluate CVs harshly like a demanding hiring manager.

CRITICAL: Respond with ONLY valid JSON. No markdown, no explanations, no text outside JSON.

JSON structure:
{
  "ats_score": 0-100 (BE HARSH, few above 85),
  "ats_breakdown": {"formatting": 0-100, "keyword_density": 0-100, "section_structure": 0-100, "content_quality": 0-100},
  "recruiter_appeal": 0-100 (BE PICKY),
  "strong_points": ["1-2 exceptional aspects ONLY"],
  "weak_points": ["2-3 SPECIFIC weaknesses"],
  "expected_interview_questions": ["2-3 likely questions"],
  "improvement_suggestions": ["2-3 actionable suggestions"],
  "overall_assessment": "50-100 words, BE HONEST about flaws"
}

BE CONCISE: Keep all points brief. Max 3 items per list. Total response under 1500 characters.

SCORING RULES:
- Score below 70 if top 3 keywords not prominent
- Score below 60 if bullets are generic ("worked on", "responsible for")
- Penalize: vagueness, no metrics, weak sections, bad formatting
- Be UNFORGIVING: find flaws, even in good CVs"""

RATING_PROMPT = """Rate following updated LaTeX CV for ATS compatibility and recruiter appeal against job requirements.

Job Title: {title}

Job Description:
{description}

Updated LaTeX CV:
{latex_cv}

Original Match Rate: {match_rate}%

Return a JSON object with: ats_score, ats_breakdown, recruiter_appeal, strong_points, weak_points, expected_interview_questions, improvement_suggestions, overall_assessment."""


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