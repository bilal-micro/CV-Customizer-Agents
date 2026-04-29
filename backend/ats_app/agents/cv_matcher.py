from ats_app.agents.keyword_matcher import EnhancedKeywordMatcherAgent
from ats_app.agents.match_evaluator import MatchEvaluatorAgent
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# AGENT 2: SectionAnalyzerAgent
# Focus: Section-by-section relevance scoring with keyword density
# ============================================================================
SECTION_ANALYZER_SYSTEM = """You are an expert at analyzing CV sections for job relevance. Your ONLY task is to evaluate how relevant each CV section is to job keywords, including keyword density analysis.

IMPORTANT: Respond with ONLY a valid JSON object. Do not include any introductory text, explanations, or markdown formatting.

JSON format:
{
  "section_analysis": {
    "education": {
      "present": bool,
      "relevance": float,
      "keyword_density": float,
      "keyword_count": int,
      "top_keywords": ["keyword1", "keyword2"]
    },
    "experience": {
      "present": bool,
      "relevance": float,
      "keyword_density": float,
      "keyword_count": int,
      "top_keywords": ["keyword1", "keyword2"]
    },
    "skills": {
      "present": bool,
      "relevance": float,
      "keyword_density": float,
      "keyword_count": int,
      "top_keywords": ["keyword1", "keyword2"]
    },
    "projects": {
      "present": bool,
      "relevance": float,
      "keyword_density": float,
      "keyword_count": int,
      "top_keywords": ["keyword1", "keyword2"]
    },
    "summary": {
      "present": bool,
      "relevance": float,
      "keyword_density": float,
      "keyword_count": int,
      "top_keywords": ["keyword1", "keyword2"]
    }
  }
}

Rules:
- "present": true if section exists in CV, false otherwise
- "relevance": percentage (0-100) of how well section content matches job keywords
- "keyword_density": percentage (0-100) of text that contains job keywords
- "keyword_count": number of unique job keywords found in section
- "top_keywords": list of 2-3 most important keywords found in this section
- Base relevance on keyword density, specific skills mentioned, and alignment with job requirements
- If a section is not present, set relevance, keyword_density, and keyword_count to 0"""

SECTION_ANALYZER_PROMPT = """Analyze each section of the following LaTeX CV for relevance to the job, including keyword density analysis.

Job Title: {title}

Extracted Keywords:
{keywords}

LaTeX CV:
{latex_cv}

CRITICAL ANALYSIS REQUIREMENTS:
1. Check which sections are present in the CV
2. For each present section:
   - Calculate relevance (0-100): how well it matches job keywords
   - Calculate keyword_density (0-100): what percentage of text contains keywords
   - Count keyword_count: how many unique job keywords appear
   - List top_keywords: 2-3 most important keywords in this section
3. For absent sections, set all values to 0
4. Include these sections: education, experience, skills, projects, summary

Respond with ONLY valid JSON containing: section_analysis with present, relevance, keyword_density, keyword_count, and top_keywords for each section."""


class SectionAnalyzerAgent:
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict:
        if not self.llm_service:
            raise ValueError("SectionAnalyzerAgent requires an LLMService instance")
        
        import json
        logger.info(f"SectionAnalyzerAgent: Starting section analysis for job '{job_title}'")
        
        prompt = SECTION_ANALYZER_PROMPT.format(
            title=job_title,
            keywords=json.dumps(keywords, indent=2),
            latex_cv=latex_cv,
        )
        
        result = self.llm_service.generate_json(prompt, SECTION_ANALYZER_SYSTEM, temperature=0.3)
        
        section_analysis = result.get('section_analysis', {})
        logger.info(f"SectionAnalyzerAgent: Analyzed {len(section_analysis)} sections")
        
        return result


# ============================================================================
# AGENT 6: AnalysisSynthesizerAgent
# Focus: Synthesize findings into actionable insights
# ============================================================================
ANALYSIS_SYNTHESIZER_SYSTEM = """You are an expert ATS analyst. Your ONLY task is to synthesize CV matching results into a comprehensive analysis.

CRITICAL: Respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{
  "matching_notes": "comprehensive analysis text"
}

Rules:
- Provide a concise summary of the CV's match quality
- Highlight the most important strengths and weaknesses
- Give specific, actionable suggestions for improvement
- Mention which sections need the most attention
- Keep the analysis clear, professional, and encouraging
- Length: 100-200 words (BE CONCISE)"""

ANALYSIS_SYNTHESIZER_PROMPT = """Synthesize a comprehensive analysis of this CV matching results.

Job Title: {title}

Match Rate: {match_rate}%

Keyword Results:
{keyword_results}

Section Analysis:
{section_analysis}

Strengths:
{strengths}

Weaknesses:
{weaknesses}

Detailed Feedback:
{detailed_feedback}

Respond with ONLY valid JSON containing: matching_notes (detailed analysis and suggestions)."""


class AnalysisSynthesizerAgent:
    def __init__(self, llm_service=None):
        self.llm_service = llm_service
    
    def run(self, job_title: str, match_rate: float, keyword_results: dict, 
             section_analysis: dict, strengths: list, weaknesses: list, 
             detailed_feedback: str = "") -> dict:
        if not self.llm_service:
            raise ValueError("AnalysisSynthesizerAgent requires an LLMService instance")
        
        import json
        logger.info(f"AnalysisSynthesizerAgent: Starting analysis synthesis for job '{job_title}'")
        
        prompt = ANALYSIS_SYNTHESIZER_PROMPT.format(
            title=job_title,
            match_rate=match_rate,
            keyword_results=json.dumps(keyword_results, indent=2),
            section_analysis=json.dumps(section_analysis, indent=2),
            strengths=json.dumps(strengths, indent=2),
            weaknesses=json.dumps(weaknesses, indent=2),
            detailed_feedback=detailed_feedback or "No detailed feedback available"
        )
        
        result = self.llm_service.generate_json(prompt, ANALYSIS_SYNTHESIZER_SYSTEM, temperature=0.5)
        
        notes_length = len(result.get('matching_notes', ''))
        logger.info(f"AnalysisSynthesizerAgent: Generated analysis notes ({notes_length} chars)")
        
        return result


# ============================================================================
# MAIN ORCHESTRATOR: CVMatcherAgent
# Coordinates enhanced keyword matching pipeline
# ============================================================================
class CVMatcherAgent:
    def __init__(self, include_advanced_analysis: bool = False, llm_service=None):
        """
        Initialize CV matcher.
        
        Args:
            include_advanced_analysis: If True, include keyword prioritization and gap analysis
            llm_service: LLMService instance for LLM operations
        """
        self.include_advanced_analysis = include_advanced_analysis
        self.keyword_matcher = EnhancedKeywordMatcherAgent()
        self.section_analyzer = SectionAnalyzerAgent(llm_service=llm_service)
        self.match_evaluator = MatchEvaluatorAgent(llm_service=llm_service)
        self.analysis_synthesizer = AnalysisSynthesizerAgent(llm_service=llm_service)
        
        # Optional advanced agents
        self.keyword_prioritizer = None
        self.keyword_gap_analyzer = None
        
        if include_advanced_analysis:
            from ats_app.agents.keyword_prioritizer import KeywordPrioritizerAgent
            from ats_app.agents.keyword_gap_analyzer import KeywordGapAnalyzerAgent
            self.keyword_prioritizer = KeywordPrioritizerAgent(llm_service=llm_service)
            self.keyword_gap_analyzer = KeywordGapAnalyzerAgent(llm_service=llm_service)
        
        logger.info(f"CVMatcherAgent initialized (advanced_analysis={include_advanced_analysis})")
    
    def run(self, job_title: str, keywords: dict, latex_cv: str) -> dict:
        """
        Orchestrate enhanced keyword matching pipeline.
        
        Simplified Pipeline:
        1. EnhancedKeywordMatcherAgent - Find matched/missing keywords with context
        2. SectionAnalyzerAgent - Score section relevance with keyword density
        3. MatchEvaluatorAgent - Identify strengths, weaknesses, calculate match rate
        4. AnalysisSynthesizerAgent - Generate comprehensive notes
        5. Optional: KeywordPrioritizerAgent - Prioritize keywords for optimization
        6. Optional: KeywordGapAnalyzerAgent - Analyze gaps and create action plan
        """
        logger.info(f"CVMatcherAgent: Starting enhanced CV matching for job '{job_title}'")
        
        # Agent 1: Match keywords with enhanced analysis
        logger.info(f"CVMatcherAgent: [1/4] Running EnhancedKeywordMatcherAgent")
        keyword_results = self.keyword_matcher.match_keywords(job_title, keywords, latex_cv)
        
        # Agent 2: Analyze sections with keyword density
        logger.info(f"CVMatcherAgent: [2/4] Running SectionAnalyzerAgent")
        section_results = self.section_analyzer.run(job_title, keywords, latex_cv)
        
        # Agent 3: Comprehensive evaluation (strengths, weaknesses, match rate)
        logger.info(f"CVMatcherAgent: [3/4] Running MatchEvaluatorAgent")
        evaluation_results = self.match_evaluator.run(
            job_title, keywords, keyword_results, 
            section_results.get('section_analysis', {}), latex_cv
        )
        
        # Extract results from evaluation
        strengths = evaluation_results.get('strengths', [])
        weaknesses = evaluation_results.get('weaknesses', [])
        match_rate = evaluation_results.get('match_rate', 0.0)
        detailed_feedback = evaluation_results.get('detailed_feedback', '')
        
        # Optional advanced analysis
        prioritization = None
        gap_analysis = None
        
        if self.include_advanced_analysis:
            # Agent 4: Prioritize keywords
            logger.info(f"CVMatcherAgent: [4a] Running KeywordPrioritizerAgent")
            prioritization = self.keyword_prioritizer.prioritize(
                job_title, keywords, keyword_results, section_results
            )
            
            # Agent 5: Analyze gaps
            logger.info(f"CVMatcherAgent: [4b] Running KeywordGapAnalyzerAgent")
            gap_analysis = self.keyword_gap_analyzer.analyze_gaps(
                job_title, keywords, keyword_results, 
                section_results, prioritization
            )
        
        # Agent 4/6: Synthesize analysis
        logger.info(f"CVMatcherAgent: [4/4] Running AnalysisSynthesizerAgent")
        analysis_results = self.analysis_synthesizer.run(
            job_title, 
            match_rate,
            keyword_results,
            section_results.get('section_analysis', {}),
            strengths,
            weaknesses,
            detailed_feedback
        )
        
        # Combine all results into final response
        # Ensure all values are expected types before assembling
        final_result = {
            "match_rate": float(match_rate) if isinstance(match_rate, (int, float)) else 0.0,
            "matched_keywords": keyword_results.get('matched_keywords', []) if isinstance(keyword_results, dict) else [],
            "missing_keywords": keyword_results.get('missing_keywords', []) if isinstance(keyword_results, dict) else [],
            "strengths": strengths if isinstance(strengths, list) else [],
            "weaknesses": weaknesses if isinstance(weaknesses, list) else [],
            "matching_notes": analysis_results.get('matching_notes', '') if isinstance(analysis_results, dict) else '',
            "section_analysis": section_results.get('section_analysis', {}) if isinstance(section_results, dict) else {},
            "overall_keyword_coverage": keyword_results.get('overall_keyword_coverage', 0.0) if isinstance(keyword_results, dict) else 0.0,
            "evaluation_summary": evaluation_results.get('evaluation_summary', {}) if isinstance(evaluation_results, dict) else {},
            "detailed_feedback": detailed_feedback if isinstance(detailed_feedback, str) else ''
        }
        
        # Type safety check - ensure we're returning a dict
        if not isinstance(final_result, dict):
            logger.error(f"CVMatcherAgent: Final result is {type(final_result)}, expected dict")
            final_result = {
                "match_rate": 0.0,
                "matched_keywords": [],
                "missing_keywords": [],
                "strengths": [],
                "weaknesses": [],
                "matching_notes": "Error: Invalid result type",
                "section_analysis": {},
                "overall_keyword_coverage": 0.0,
                "evaluation_summary": {},
                "detailed_feedback": ""
            }
        
        # Add advanced analysis if enabled
        if self.include_advanced_analysis:
            final_result['keyword_prioritization'] = prioritization
            final_result['gap_analysis'] = gap_analysis
        
        logger.info(f"CVMatcherAgent: Completed analysis - Match rate: {match_rate}%, "
                   f"{len(final_result['matched_keywords'])} matched keywords, "
                   f"{len(strengths)} strengths, {len(weaknesses)} weaknesses")
        
        return final_result