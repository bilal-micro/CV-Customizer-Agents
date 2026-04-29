import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# ============================================================================
# KEYWORD GAP ANALYZER AGENT
# Focus: Analyze gaps in keyword coverage and suggest improvements
# ============================================================================

KEYWORD_GAP_ANALYZER_SYSTEM = """You are an expert keyword gap analyst. Your ONLY task is to analyze keyword coverage gaps and provide actionable insights for CV improvement.

CRITICAL: Respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{
  "gap_analysis": {
    "critical_missing": [
      {
        "keyword": "AWS",
        "category": "technical",
        "priority": 10,
        "section_suggestion": "skills",
        "alternative_approach": "highlight cloud infrastructure experience",
        "translation_opportunity": "map to general cloud knowledge"
      }
    ],
    "section_gaps": {
      "summary": {
        "missing_count": 3,
        "priority_score": 8.5,
        "recommendation": "add top 3 keywords to summary"
      },
      "skills": {
        "missing_count": 5,
        "priority_score": 9.0,
        "recommendation": "add all missing technical skills"
      },
      "experience": {
        "missing_count": 2,
        "priority_score": 7.0,
        "recommendation": "weave missing skills into project descriptions"
      }
    },
    "density_improvements": [
      {
        "keyword": "Python",
        "current_density": 0.02,
        "target_density": 0.05,
        "suggestion": "mention in 3+ experience bullet points"
      }
    ],
    "overall_assessment": "comprehensive summary of coverage gaps and priorities"
  },
  "action_plan": {
    "immediate_actions": [
      "Add AWS to skills section",
      "Add Docker to project descriptions"
    ],
    "short_term_actions": [
      "Rewrite experience to include more keywords",
      "Add summary with top 5 keywords"
    ],
    "long_term_actions": [
      "Consider upskilling in missing critical skills",
      "Gain experience in suggested tools"
    ]
  },
  "priority_score": 7.5
}

Rules:
- critical_missing: high-priority (8-10) keywords that are absent
- section_gaps: analyze each section for missing keywords
- density_improvements: keywords present but under-utilized
- overall_assessment: 100-150 words, concise and actionable
- action_plan: specific, actionable steps prioritized by impact
- priority_score: overall coverage score (0-10) indicating urgency"""

KEYWORD_GAP_ANALYZER_PROMPT = """Analyze keyword coverage gaps and create a comprehensive improvement plan.

Job Title: {title}

Extracted Keywords (with priorities):
{keywords}

Matching Results:
{match_results}

Section Analysis:
{section_analysis}

Prioritization:
{prioritization}

CRITICAL GAP ANALYSIS TASKS:
1. Identify critical missing: high-priority keywords (8-10) not in CV
2. Analyze section gaps: which sections are missing which keywords
3. Identify density improvements: keywords present but could be used more
4. Create action plan: immediate, short-term, and long-term actions
5. Calculate priority_score: how urgently improvements are needed (0-10)
6. For each critical missing keyword:
   - Suggest which section to add it to
   - Provide alternative approach if direct experience is missing
   - Identify translation opportunities (map to similar skills)

Respond with ONLY valid JSON containing: gap_analysis (with critical_missing, section_gaps, density_improvements, overall_assessment), action_plan, priority_score."""


class KeywordGapAnalyzerAgent:
    """
    Analyzes keyword coverage gaps and provides actionable improvement plan.
    Helps focus CV optimization on the most impactful areas.
    """
    
    def __init__(self, llm_service=None):
        """Initialize keyword gap analyzer."""
        self.llm_service = llm_service
        logger.info("KeywordGapAnalyzerAgent initialized")
    
    def analyze_gaps(self, job_title: str, keywords: Dict, match_results: Dict,
                     section_analysis: Dict, prioritization: Dict) -> Dict:
        """
        Analyze gaps in keyword coverage and create improvement plan.
        
        Args:
            job_title: The job title
            keywords: Extracted keywords with priorities
            match_results: Results from keyword matching
            section_analysis: Section analysis results
            prioritization: Prioritization results
            
        Returns:
            Dictionary with gap analysis and action plan
        """
        if not self.llm_service:
            raise ValueError("KeywordGapAnalyzerAgent requires an LLMService instance")
        
        logger.info(f"KeywordGapAnalyzerAgent: Starting gap analysis for job '{job_title}'")
        
        prompt = KEYWORD_GAP_ANALYZER_PROMPT.format(
            title=job_title,
            keywords=self._format_keywords_for_llm(keywords),
            match_results=self._format_match_results_for_llm(match_results),
            section_analysis=self._format_section_analysis_for_llm(section_analysis),
            prioritization=self._format_prioritization_for_llm(prioritization)
        )
        
        result = self.llm_service.generate_json(prompt, KEYWORD_GAP_ANALYZER_SYSTEM, temperature=0.5)
        
        # Log summary
        priority_score = result.get('priority_score', 0.0)
        gap_analysis = result.get('gap_analysis', {})
        critical_missing = gap_analysis.get('critical_missing', [])
        
        logger.info(f"KeywordGapAnalyzerAgent: Priority score: {priority_score:.1f}/10, "
                   f"{len(critical_missing)} critical gaps identified")
        
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
                        placement = item.get('placement_hints', [])
                        lines.append(f"  - {name} (priority: {priority}/10, suggested: {', '.join(placement)})")
        
        return "\n".join(lines)
    
    def _format_match_results_for_llm(self, match_results: Dict) -> str:
        """Format match results for LLM prompt."""
        lines = []
        
        # Overall coverage
        coverage = match_results.get('overall_keyword_coverage', 0.0)
        lines.append(f"Overall Keyword Coverage: {coverage:.1%}\n")
        
        # Missing keywords (focus on high priority)
        missing = match_results.get('missing_keywords', [])
        if missing:
            high_impact_missing = [kw for kw in missing if kw.get('priority_impact') == 'high']
            lines.append(f"HIGH IMPACT MISSING KEYWORDS ({len(high_impact_missing)}):")
            for kw in high_impact_missing:
                name = kw.get('keyword', 'Unknown')
                suggestion = kw.get('suggested_location', 'unknown')
                lines.append(f"  - {name} (add to: {suggestion})")
        
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
    
    def _format_prioritization_for_llm(self, prioritization: Dict) -> str:
        """Format prioritization for LLM prompt."""
        lines = ["\nPRIORITIZATION:"]
        
        # Critical gaps
        critical_gaps = prioritization.get('critical_gaps', [])
        if critical_gaps:
            lines.append(f"Critical Gaps ({len(critical_gaps)}):")
            for gap in critical_gaps:
                keyword = gap.get('keyword', 'Unknown')
                action = gap.get('action', 'unknown')
                lines.append(f"  - {keyword}: {action}")
        
        # Top priorities
        priority_order = prioritization.get('priority_order', [])
        if priority_order:
            top_priorities = [p for p in priority_order if p.get('optimization_priority') in ['critical', 'high']][:5]
            if top_priorities:
                lines.append(f"\nTop 5 Priorities:")
                for priority in top_priorities:
                    keyword = priority.get('keyword', 'Unknown')
                    opt_priority = priority.get('optimization_priority', 'unknown')
                    lines.append(f"  - {keyword} ({opt_priority} priority)")
        
        return "\n".join(lines)
    
    def get_immediate_actions(self, gap_analysis: Dict) -> List[str]:
        """
        Get immediate actions from gap analysis.
        
        Args:
            gap_analysis: Result from analyze_gaps method
            
        Returns:
            List of immediate actions
        """
        action_plan = gap_analysis.get('action_plan', {})
        immediate = action_plan.get('immediate_actions', [])
        logger.info(f"KeywordGapAnalyzerAgent: {len(immediate)} immediate actions identified")
        return immediate
    
    def get_critical_gaps(self, gap_analysis: Dict) -> List[Dict]:
        """
        Get critical gaps from gap analysis.
        
        Args:
            gap_analysis: Result from analyze_gaps method
            
        Returns:
            List of critical gaps
        """
        gap_data = gap_analysis.get('gap_analysis', {})
        critical = gap_data.get('critical_missing', [])
        logger.info(f"KeywordGapAnalyzerAgent: {len(critical)} critical gaps identified")
        return critical
    
    def get_section_recommendations(self, gap_analysis: Dict) -> Dict[str, Dict]:
        """
        Get section-specific recommendations.
        
        Args:
            gap_analysis: Result from analyze_gaps method
            
        Returns:
            Dictionary mapping section names to recommendations
        """
        gap_data = gap_analysis.get('gap_analysis', {})
        section_gaps = gap_data.get('section_gaps', {})
        logger.info(f"KeywordGapAnalyzerAgent: Recommendations for {len(section_gaps)} sections")
        return section_gaps