from ats_app.services.llm_service import llm_service
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ============================================================================
# MATCH EVALUATOR AGENT
# Focus: Comprehensive CV evaluation (strengths, weaknesses, match rate)
# Merges 3 separate agents into 1 for efficiency
# ============================================================================

MATCH_EVALUATOR_SYSTEM = """You are an expert CV evaluator. Your ONLY task is to comprehensively evaluate a CV against job requirements, identifying strengths, weaknesses, and calculating an accurate match rate.

CRITICAL: Respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{
  "strengths": [
    "Specific strength with evidence from CV"
  ],
  "weaknesses": [
    "Specific weakness with reference to job requirements"
  ],
  "match_rate": float,
  "evaluation_summary": {
    "overall_score": float,
    "keyword_alignment": float,
    "section_quality": float,
    "content_completeness": float
  },
  "detailed_feedback": "comprehensive analysis of CV quality (150-200 words)"
}

Rules:
- Find 3-7 specific strengths: look for relevant experience, matching skills, impressive projects, appropriate education
- Find 3-7 specific weaknesses: look for missing skills, lack of experience, weak project descriptions, poor keyword placement
- match_rate: Calculate based on:
  * Keyword coverage (40%): percentage of job keywords found in CV
  * Section relevance (40%): average relevance across all sections
  * Content quality (20%): strength of descriptions and achievements
- Round match_rate to 1 decimal place
- evaluation_summary: Breakdown of scoring components (0-100 each)
- detailed_feedback: 150-200 words, concise and actionable
- NEVER return N/A values or empty arrays
- ALWAYS find specific strengths and weaknesses based on the CV content"""

MATCH_EVALUATOR_PROMPT = """Comprehensively evaluate this CV against job requirements.

Job Title: {title}

Extracted Keywords:
{keywords}

Keyword Matching Results:
{match_results}

Section Analysis:
{section_analysis}

LaTeX CV:
{latex_cv}

CRITICAL EVALUATION REQUIREMENTS:
1. Identify 3-7 specific strengths with evidence from CV
2. Identify 3-7 specific weaknesses with reference to job requirements
3. Calculate match_rate based on:
   - Keyword coverage: what percentage of job keywords are present?
   - Section relevance: how well does each section align?
   - Content quality: are descriptions strong and specific?
4. Provide evaluation_summary with component scores
5. Write detailed_feedback (150-200 words) with specific, actionable suggestions

Respond with ONLY valid JSON containing: strengths, weaknesses, match_rate, evaluation_summary, detailed_feedback."""


class MatchEvaluatorAgent:
    """
    Comprehensive CV evaluator that identifies strengths, weaknesses,
    and calculates match rate in a single efficient LLM call.
    """
    
    def run(self, job_title: str, keywords: Dict, match_results: Dict,
             section_analysis: Dict, latex_cv: str) -> Dict:
        """
        Evaluate CV comprehensively against job requirements.
        
        Args:
            job_title: The job title
            keywords: Extracted keywords with priorities
            match_results: Results from keyword matching
            section_analysis: Section analysis with keyword density
            latex_cv: The LaTeX CV content
            
        Returns:
            Dictionary with strengths, weaknesses, match_rate, and evaluation details
        """
        logger.info(f"MatchEvaluatorAgent: Starting comprehensive evaluation for job '{job_title}'")
        
        # Format data for LLM
        keywords_formatted = self._format_keywords_for_llm(keywords)
        match_results_formatted = self._format_match_results_for_llm(match_results)
        section_analysis_formatted = self._format_section_analysis_for_llm(section_analysis)
        
        prompt = MATCH_EVALUATOR_PROMPT.format(
            title=job_title,
            keywords=keywords_formatted,
            match_results=match_results_formatted,
            section_analysis=section_analysis_formatted,
            latex_cv=latex_cv
        )
        
        # Use temperature=0.4 for balanced, analytical evaluation
        result = llm_service.generate_json(prompt, MATCH_EVALUATOR_SYSTEM, temperature=0.4)
        
        # Log summary
        strengths = result.get('strengths', [])
        weaknesses = result.get('weaknesses', [])
        match_rate = result.get('match_rate', 0.0)
        
        logger.info(f"MatchEvaluatorAgent: Evaluated CV - Match rate: {match_rate}%, "
                   f"{len(strengths)} strengths, {len(weaknesses)} weaknesses")
        
        return result
    
    def _format_keywords_for_llm(self, keywords: Dict) -> str:
        """Format keywords for LLM prompt."""
        lines = []
        
        categories = ['hard_skills', 'soft_skills', 'qualifications', 'keywords', 'must_have', 'nice_to_have']
        
        for category in categories:
            items = keywords.get(category, [])
            if isinstance(items, list) and items:
                high_priority = [i for i in items if isinstance(i, dict) and i.get('priority', 0) >= 8]
                if high_priority:
                    lines.append(f"\n{category.upper().replace('_', ' ')} (HIGH PRIORITY):")
                    for item in high_priority[:5]:
                        name = item.get('skill') or item.get('keyword') or item.get('item') or item.get('qualification', '')
                        priority = item.get('priority', 5)
                        lines.append(f"  - {name} (priority: {priority}/10)")
        
        return "\n".join(lines)
    
    def _format_match_results_for_llm(self, match_results: Dict) -> str:
        """Format match results for LLM prompt."""
        lines = []
        
        # Overall coverage
        coverage = match_results.get('overall_keyword_coverage', 0.0)
        lines.append(f"Overall Keyword Coverage: {coverage:.1%}\n")
        
        # Matched keywords
        matched = match_results.get('matched_keywords', [])
        if matched:
            lines.append(f"MATCHED KEYWORDS ({len(matched)}):")
            for kw in matched[:8]:
                name = kw.get('keyword', 'Unknown')
                effectiveness = kw.get('effectiveness_score', 0.0)
                lines.append(f"  - {name} (effectiveness: {effectiveness:.2f})")
            if len(matched) > 8:
                lines.append(f"  ... and {len(matched) - 8} more")
        
        # Missing keywords
        missing = match_results.get('missing_keywords', [])
        if missing:
            lines.append(f"\nMISSING KEYWORDS ({len(missing)}):")
            high_impact = [kw for kw in missing if kw.get('priority_impact') == 'high']
            for kw in high_impact[:5]:
                name = kw.get('keyword', 'Unknown')
                lines.append(f"  - {name} (high impact)")
            if len(high_impact) > 5:
                lines.append(f"  ... and {len(high_impact) - 5} more high-impact keywords")
        
        return "\n".join(lines)
    
    def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str:
        """Format section analysis for LLM prompt."""
        lines = ["\nSECTION ANALYSIS (with keyword density):"]
        
        sections = section_analysis.get('section_analysis', {})
        if sections:
            for section_name, section_data in sections.items():
                if isinstance(section_data, dict):
                    present = section_data.get('present', False)
                    relevance = section_data.get('relevance', 0.0)
                    density = section_data.get('keyword_density', 0.0)
                    keyword_count = section_data.get('keyword_count', 0)
                    top_keywords = section_data.get('top_keywords', [])
                    
                    status = "present" if present else "absent"
                    lines.append(f"  - {section_name}: {status}")
                    if present:
                        lines.append(f"    Relevance: {relevance:.0%}, Density: {density:.0%}, "
                                   f"Keywords: {keyword_count}, Top: {', '.join(top_keywords)}")
        else:
            lines.append("  No section analysis available")
        
        return "\n".join(lines)
    
    def get_match_quality_assessment(self, evaluation: Dict) -> Dict:
        """
        Get detailed assessment of match quality.
        
        Args:
            evaluation: Result from run method
            
        Returns:
            Dictionary with quality metrics
        """
        match_rate = evaluation.get('match_rate', 0.0)
        eval_summary = evaluation.get('evaluation_summary', {})
        
        return {
            'match_rate': match_rate,
            'quality_level': self._get_quality_level(match_rate),
            'keyword_alignment': eval_summary.get('keyword_alignment', 0.0),
            'section_quality': eval_summary.get('section_quality', 0.0),
            'content_completeness': eval_summary.get('content_completeness', 0.0),
            'strength_count': len(evaluation.get('strengths', [])),
            'weakness_count': len(evaluation.get('weaknesses', []))
        }
    
    def _get_quality_level(self, match_rate: float) -> str:
        """Determine quality level based on match rate."""
        if match_rate >= 80:
            return "excellent"
        elif match_rate >= 70:
            return "good"
        elif match_rate >= 60:
            return "acceptable"
        elif match_rate >= 50:
            return "needs improvement"
        else:
            return "poor"