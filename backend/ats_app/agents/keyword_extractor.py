from ats_app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# ENHANCED KEYWORD EXTRACTOR WITH PRIORITIES
# Focus: Extract, prioritize, and categorize job keywords
# ============================================================================

ENHANCED_KEYWORD_EXTRACTOR_SYSTEM = """You are an expert ATS keyword extraction specialist. Your job is to analyze job descriptions and extract comprehensive, prioritized keywords, skills, and qualifications that an ATS (Applicant Tracking System) would look for.

CRITICAL: Respond with ONLY a valid JSON object. No other text, no explanations, no markdown formatting.

JSON format:
{
  "hard_skills": [
    {"skill": "Python", "priority": 10, "category": "programming_language", "placement_hints": ["skills", "experience", "projects"], "confidence": 0.95}
  ],
  "soft_skills": [
    {"skill": "Communication", "priority": 8, "category": "interpersonal", "placement_hints": ["summary", "experience"], "confidence": 0.90}
  ],
  "qualifications": [
    {"qualification": "Bachelor's in Computer Science", "priority": 10, "category": "education", "placement_hints": ["education"], "confidence": 1.0}
  ],
  "keywords": [
    {"keyword": "Machine Learning", "priority": 9, "category": "domain_knowledge", "placement_hints": ["summary", "skills", "projects"], "confidence": 0.92}
  ],
  "job_notes": "comprehensive analysis about the job, employer values, and applicant tips",
  "must_have": [
    {"item": "5+ years Python", "priority": 10, "category": "experience", "placement_hints": ["summary", "experience"], "confidence": 1.0}
  ],
  "nice_to_have": [
    {"item": "AWS certification", "priority": 5, "category": "certification", "placement_hints": ["skills", "certifications"], "confidence": 0.85}
  ]
}

Rules:
- priority: 1-10 scale (10 = critical/must-have, 7-9 = highly important, 4-6 = moderately important, 1-3 = nice-to-have)
- category: technical/soft/tools/domain/education/experience/certification/leadership/etc.
- placement_hints: suggested CV sections where this should appear
- confidence: 0.0-1.0 (how certain you are this is required)
- Extract 10-20 hard skills
- Extract 5-10 soft skills
- Extract 3-8 qualifications
- Extract 8-15 keywords
- Extract 3-5 must-have items
- Extract 3-5 nice-to-have items
- Be comprehensive but focused on ATS-critical terms
- Include variations of terms (e.g., both "Python" and "Python 3")"""

ENHANCED_EXTRACTION_PROMPT = """Analyze the following job description and extract comprehensive, prioritized ATS-critical keywords, skills, and qualifications.

Job Title: {title}

Job Description:
{description}

CRITICAL REQUIREMENTS:
1. Extract hard skills with priority scores (10 = critical, 1 = optional)
2. Extract soft skills with priority scores
3. Extract qualifications with priority scores
4. Extract industry keywords with priority scores
5. Identify must-have vs nice-to-have items
6. For each item, specify:
   - Priority (1-10)
   - Category (type of skill/qualification)
   - Placement hints (where in CV it should appear)
   - Confidence (0-1)

Return a JSON object with: hard_skills, soft_skills, qualifications, keywords, job_notes, must_have, nice_to_have. Each item should be an object with skill/item, priority, category, placement_hints, and confidence."""


class KeywordExtractorAgent:
    def run(self, job_title: str, job_description: str) -> dict:
        """
        Extract keywords with priorities and detailed metadata.
        
        Args:
            job_title: The job title
            job_description: The job description text
            
        Returns:
            Dictionary with prioritized keywords and metadata
        """
        logger.info(f"KeywordExtractorAgent: Starting enhanced extraction for job '{job_title}'")
        
        prompt = ENHANCED_EXTRACTION_PROMPT.format(
            title=job_title,
            description=job_description,
        )
        
        result = llm_service.generate_json(prompt, ENHANCED_KEYWORD_EXTRACTOR_SYSTEM, temperature=0.3)
        
        # Validate and log extraction results
        self._log_extraction_summary(result)
        
        return result
    
    def _log_extraction_summary(self, result: dict) -> None:
        """Log a summary of extracted keywords."""
        total_keywords = 0
        total_priority = 0
        
        for category in ['hard_skills', 'soft_skills', 'qualifications', 'keywords', 'must_have', 'nice_to_have']:
            items = result.get(category, [])
            total_keywords += len(items)
            total_priority += sum(item.get('priority', 0) for item in items)
            
        avg_priority = total_priority / total_keywords if total_keywords > 0 else 0
        
        logger.info(f"KeywordExtractorAgent: Extracted {total_keywords} items, avg priority: {avg_priority:.1f}/10")
        
        # Count high-priority items
        high_priority = sum(
            1 for items in result.values() 
            if isinstance(items, list) 
            for item in items 
            if isinstance(item, dict) and item.get('priority', 0) >= 8
        )
        logger.info(f"KeywordExtractorAgent: {high_priority} high-priority items (priority >= 8)")