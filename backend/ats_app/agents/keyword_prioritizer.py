from ats_app.services.llm_service import llm_service
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ============================================================================
# KEYWORD PRIORITIZER AGENT
# Focus: Weight, categorize, and prioritize keywords for CV optimization
# ============================================================================

KEYWORD_PRIORITIZER_SYSTEM = """You are an expert keyword prioritization specialist. Your ONLY task is to analyze keyword matching results and prioritize which keywords to focus on for CV optimization.

CRITICAL: Respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{
  "priority_order": [
    {
      "keyword": "Python",
      "current_status": "matched",
      "optimization_priority": "critical",
      "reason": "high-priority skill but poorly used",
      "suggested_improvement": "add to skills section and experience",
      "expected_impact": "high"
    }
  ],
  "critical_gaps": [
    {
      "keyword": "AWS",
      "category": "technical",
      "reason": "missing high-priority skill",
      "action": "add to CV immediately"
    }
  ],
  "enhancement_opportunities": [
    {
      "keyword": "Machine Learning",
      "current_status": "matched",
      "improvement": "add more context and examples"
    }
  ],
  "summary": {
    "total_keywords": 50,
    "matched": 35,
    "missing": 15,
    "critical_missing": 5,
    "needs_improvement": 8,
    "top_priority_count": 5
  }
}

Rules:
- optimization_priority: critical/high/medium/low
- current_status: matched/missing/poorly_matched
- expected_impact: high/medium/low
- Prioritize by: missing high-priority > poorly used high-priority > missing medium-priority
- critical_gaps: keywords that MUST be in the CV
- enhancement_opportunities: matched keywords that could be better used
- Be specific about what needs to be done"""

KEYWORD_PRIORITIZER_PROMPT = """Analyze the keyword matching results and create an optimization priority plan.

Job Title: {title}

Extracted Keywords (with priorities):
{keywords}

Matching Results:
{match_results}

Section Analysis:
{section_analysis}

CRITICAL PRIORITIZATION TASKS:
1. Identify critical gaps: high-priority keywords (8-10) that are missing
2. Identify poorly matched keywords: present but used ineffectively
3. Identify enhancement opportunities: matched keywords that could be better
4. Create priority order: list all keywords with optimization priority
5. For each keyword, specify:
   - Current status (matched/missing/poorly_matched)
   - Optimization priority (critical/high/medium/low)
   - Reason for priority
   - Suggested improvement action
   - Expected impact (high/medium/low)

Respond with ONLY valid JSON containing: priority_order, critical_gaps, enhancement_opportunities, summary."""


class KeywordPrioritizerAgent:
    """
    Analyzes and prioritizes keywords for CV optimization.
    Helps focus efforts on the most impactful improvements.
    """
    
    def __init__(self):
        """Initialize keyword prioritizer."""
        logger.info("KeywordPrioritizerAgent initialized")
    
    def prioritize(self, job_title: str, keywords: Dict, match_results: Dict, 
                   section_analysis: Dict) -> Dict:
        """
        Prioritize keywords based on matching results and importance.
        
        Args:
            job_title: The job title
            keywords: Extracted keywords with priorities
            match_results: Results from keyword matching
            section_analysis: Section analysis results
            
        Returns:
            Dictionary with prioritized optimization plan
        """
        logger.info(f"KeywordPrioritizerAgent: Starting prioritization for job '{job_title}'")
        
        prompt = KEYWORD_PRIORITIZER_PROMPT.format(
            title=job_title,
            keywords=self._format_keywords_for_llm(keywords),
            match_results=self._format_match_results_for_llm(match_results),
            section_analysis=self._format_section_analysis_for_llm(section_analysis)
        )
        
        result = llm_service.generate_json(prompt, KEYWORD_PRIORITIZER_SYSTEM, temperature=0.4)
        
        # Log summary
        summary = result.get('summary', {})
        logger.info(f"KeywordPrioritizerAgent: Prioritized {summary.get('total_keywords', 0)} keywords, "
                   f"{summary.get('critical_missing', 0)} critical gaps, "
                   f"{summary.get('top_priority_count', 0)} top priorities")
        
        return result
    
    def _format_keywords_for_llm(self, keywords: Dict) -> str:
        """Format keywords for LLM prompt."""
        lines = []
        
        categories = ['hard_skills', 'soft_skills', 'qualifications', 'keywords', 'must_have', 'nice_to_have']
        
        for category in categories:
            items = keywords.get(category, [])
            if isinstance(items, list) and items:
                lines.append(f"\n{category.upper().replace('_', ' ')}:")
                
                for item in items:
                    if isinstance(item, dict):
                        name = item.get('skill') or item.get('keyword') or item.get('item') or item.get('qualification', '')
                        priority = item.get('priority', 5)
                        placement = item.get('placement_hints', [])
                        lines.append(f"  - {name} (priority: {priority}/10, placement: {', '.join(placement)})")
        
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
            for kw in matched[:10]:  # Show first 10
                name = kw.get('keyword', 'Unknown')
                location = kw.get('location', 'Unknown')
                effectiveness = kw.get('effectiveness_score', 0.0)
                lines.append(f"  - {name} (location: {location}, effectiveness: {effectiveness:.2f})")
            if len(matched) > 10:
                lines.append(f"  ... and {len(matched) - 10} more matched keywords")
        
        # Missing keywords
        missing = match_results.get('missing_keywords', [])
        if missing:
            lines.append(f"\nMISSING KEYWORDS ({len(missing)}):")
            for kw in missing[:10]:  # Show first 10
                name = kw.get('keyword', 'Unknown')
                impact = kw.get('priority_impact', 'unknown')
                lines.append(f"  - {name} (impact: {impact})")
            if len(missing) > 10:
                lines.append(f"  ... and {len(missing) - 10} more missing keywords")
        
        return "\n".join(lines)
    
    def _format_section_analysis_for_llm(self, section_analysis: Dict) -> str:
        """Format section analysis for LLM prompt."""
        lines = ["SECTION ANALYSIS:"]
        
        sections = section_analysis.get('section_analysis', {})
        if sections:
            for section_name, section_data in sections.items():
                if isinstance(section_data, dict):
                    present = section_data.get('present', False)
                    relevance = section_data.get('relevance', 0.0)
                    status = "present" if present else "absent"
                    lines.append(f"  - {section_name}: {status}, relevance: {relevance:.0%}")
        else:
            lines.append("  No section analysis available")
        
        return "\n".join(lines)
    
    def get_top_priorities(self, prioritization: Dict, limit: int = 5) -> List[Dict]:
        """
        Get the top priority keywords for immediate action.
        
        Args:
            prioritization: Result from prioritize method
            limit: Maximum number of priorities to return
            
        Returns:
            List of top priority keywords
        """
        priority_order = prioritization.get('priority_order', [])
        
        # Filter for critical and high priority
        top = [
            item for item in priority_order 
            if item.get('optimization_priority', 'low') in ['critical', 'high']
        ][:limit]
        
        logger.info(f"KeywordPrioritizerAgent: Retrieved {len(top)} top priorities (limit: {limit})")
        return top
    
    def get_critical_gaps(self, prioritization: Dict) -> List[Dict]:
        """
        Get critical gaps that must be addressed.
        
        Args:
            prioritization: Result from prioritize method
            
        Returns:
            List of critical gaps
        """
        critical_gaps = prioritization.get('critical_gaps', [])
        logger.info(f"KeywordPrioritizerAgent: Found {len(critical_gaps)} critical gaps")
        return critical_gaps