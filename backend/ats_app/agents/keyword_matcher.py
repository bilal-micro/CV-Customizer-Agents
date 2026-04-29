import logging
import re
from typing import List, Dict, Tuple, Optional
from fuzzywuzzy import fuzz, process
from django.conf import settings

logger = logging.getLogger(__name__)

# Configuration for similarity matching
SIMILARITY_THRESHOLD = getattr(settings, 'SIMILARITY_THRESHOLD', 85)
MAX_CANDIDATES = getattr(settings, 'MAX_SIMILARITY_CANDIDATES', 3)
USE_LLM_VALIDATION = getattr(settings, 'USE_LLM_VALIDATION', True)
LLM_VALIDATION_THRESHOLD_LOW = getattr(settings, 'LLM_VALIDATION_THRESHOLD_LOW', 75)
LLM_VALIDATION_THRESHOLD_HIGH = getattr(settings, 'LLM_VALIDATION_THRESHOLD_HIGH', 90)

# Keyword categories
HARD_SKILL_CATEGORIES = getattr(settings, 'HARD_SKILL_CATEGORIES', ['hard_skills', 'keywords', 'must_have', 'nice_to_have'])
SOFT_SKILL_CATEGORIES = getattr(settings, 'SOFT_SKILL_CATEGORIES', ['soft_skills'])
QUALIFICATION_CATEGORIES = getattr(settings, 'QUALIFICATION_CATEGORIES', ['qualifications'])

# False positive patterns (words that should not match soft skills)
FALSE_POSITIVE_PATTERNS = [
    r'inter-service\s+communication',
    r'queue\s+management',
    r'time\s+management',
    r'data\s+management',
    r'project\s+management',
    r'service\s+communication',
    r'communication\s+using',
    r'management\s+system',
]

# Synonyms and normalizations
SKILL_SYNONYMS = {
    'git': ['git', 'github', 'gitlab', 'version control'],
    'machine learning': ['machine learning', 'ml', 'ai', 'artificial intelligence'],
    'natural language processing': ['nlp', 'natural language processing'],
    'kubernetes': ['kubernetes', 'k8s', 'k8'],
    'docker': ['docker', 'containerization', 'containers'],
    'ci/cd': ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment'],
    'python': ['python', 'python 3', 'py'],
}

# Quantification patterns (handle "5+ years" vs "7+ years")
QUANTIFICATION_PATTERNS = {
    r'(\d+)\+?\s*years?': 'years',  # "5+ years", "7 years"
    r'(\d+)\+?\s*months?': 'months',
}

# ============================================================================
# STRING-BASED KEYWORD MATCHER
# Focus: Fast, deterministic keyword detection using case-insensitive string search
# ============================================================================


class EnhancedKeywordMatcherAgent:
    """
    String-based keyword matching with case-insensitive search.
    Provides detailed analysis of keyword presence, location, and effectiveness
    using fast, deterministic string matching instead of LLM calls.
    """
    
    def __init__(self):
        """Initialize enhanced keyword matcher."""
        logger.info("EnhancedKeywordMatcherAgent initialized")
    
    def _flatten_keywords(self, keywords: Dict) -> List[Dict]:
        """
        Flatten keyword dictionary into list of keyword items with priorities.
        
        Args:
            keywords: Dictionary containing prioritized keywords
            
        Returns:
            List of keyword items with name and priority
        """
        keyword_items = []
        
        # Process each category
        categories = ['hard_skills', 'soft_skills', 'qualifications', 'keywords', 'must_have', 'nice_to_have']
        
        for category in categories:
            items = keywords.get(category, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        # Extract keyword/skill/item name
                        keyword_name = item.get('skill') or item.get('keyword') or item.get('item') or item.get('qualification', '')
                        if keyword_name:
                            keyword_items.append({
                                'name': keyword_name,
                                'priority': item.get('priority', 5),
                                'category': item.get('category', 'unknown'),
                                'placement_hints': item.get('placement_hints', []),
                                'confidence': item.get('confidence', 0.8)
                            })
        
        logger.info(f"Flattened {len(keyword_items)} keywords from {len(categories)} categories")
        return keyword_items
    
    def match_keywords(self, job_title: str, keywords: Dict, latex_cv: str) -> Dict:
        """
        Match keywords against LaTeX CV using case-insensitive string search.
        
        Args:
            job_title: The job title
            keywords: Dictionary containing prioritized keywords
            latex_cv: The LaTeX CV content
            
        Returns:
            Dictionary with detailed matched_keywords, missing_keywords, and coverage
        """
        logger.info(f"EnhancedKeywordMatcherAgent: Starting string-based matching for job '{job_title}'")
        
        # Flatten keywords for analysis
        flattened_keywords = self._flatten_keywords(keywords)
        
        if not flattened_keywords:
            logger.warning("No keywords found to match")
            return {
                'matched_keywords': [],
                'missing_keywords': [],
                'overall_keyword_coverage': 0.0,
                'keyword_details': []
            }
        
        # Detect sections in the LaTeX CV
        sections = self._detect_sections(latex_cv)
        
        # Convert CV to lowercase for case-insensitive matching
        latex_cv_lower = latex_cv.lower()
        
        # Match each keyword
        matched_keywords = []
        missing_keywords = []
        
        for keyword_item in flattened_keywords:
            keyword_name = keyword_item['name']
            keyword_lower = keyword_name.lower()
            
            # Use similarity matching instead of exact match
            similar_match = self._find_similar_match(keyword_name, latex_cv, keyword_item)
            
            if similar_match:
                # Keyword found via similarity matching
                matched_text = similar_match['text']
                similarity_score = similar_match['score']
                location = self._find_keyword_location(latex_cv, matched_text, sections)
                context = self._extract_context(latex_cv, matched_text)
                effectiveness_score = self._calculate_effectiveness_score(latex_cv_lower, matched_text.lower(), location, sections)
                usage_quality = self._determine_usage_quality(location, sections, keyword_item)
                
                matched_keywords.append({
                    'keyword': keyword_name,
                    'location': location,
                    'context': context,
                    'effectiveness_score': effectiveness_score,
                    'usage_quality': usage_quality,
                    'similarity_score': similarity_score
                })
            else:
                # Keyword not found
                priority_impact = self._get_priority_impact(keyword_item['priority'])
                suggested_location = self._get_suggested_location(keyword_item['category'])
                
                missing_keywords.append({
                    'keyword': keyword_name,
                    'reason': 'no similar match found in CV',
                    'priority_impact': priority_impact,
                    'suggested_location': suggested_location
                })
        
        # Calculate overall keyword coverage
        total_keywords = len(flattened_keywords)
        overall_coverage = len(matched_keywords) / total_keywords if total_keywords > 0 else 0.0
        
        # Build result
        result = {
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'overall_keyword_coverage': overall_coverage,
            'keyword_details': flattened_keywords,
            'total_keywords_analyzed': total_keywords
        }
        
        # Log summary
        matched = len(matched_keywords)
        missing = len(missing_keywords)
        
        logger.info(f"EnhancedKeywordMatcherAgent: Matched {matched}/{total_keywords} keywords, "
                   f"missing {missing}, coverage: {overall_coverage:.1%}")
        
        return result
    
    def _detect_sections(self, latex_cv: str) -> Dict[str, int]:
        """
        Detect section positions in LaTeX CV.
        
        Args:
            latex_cv: The LaTeX CV content
            
        Returns:
            Dictionary mapping section names to line numbers
        """
        sections = {}
        lines = latex_cv.split('\n')
        
        # Common LaTeX section patterns
        section_patterns = [
            r'\\section\{([^}]+)\}',
            r'\\subsection\{([^}]+)\}',
            r'\\section\*\{([^}]+)\}',
            r'\\subsection\*\{([^}]+)\}'
        ]
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in section_patterns:
                match = re.search(pattern, line)
                if match:
                    section_name = match.group(1).strip()
                    # Clean up section name
                    section_name = section_name.replace('\n', ' ').strip()
                    sections[section_name.lower()] = line_num
        
        logger.debug(f"Detected {len(sections)} sections in CV")
        return sections
    
    def _find_keyword_location(self, latex_cv: str, keyword: str, sections: Dict[str, int]) -> str:
        """
        Find the line number and section where keyword appears.
        
        Args:
            latex_cv: The LaTeX CV content
            keyword: The keyword to find
            sections: Dictionary of detected sections
            
        Returns:
            String describing the location (line and section)
        """
        keyword_lower = keyword.lower()
        lines = latex_cv.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            if keyword_lower in line.lower():
                # Find the nearest section before this line
                section_name = self._find_nearest_section(line_num, sections)
                if section_name:
                    return f"{section_name} section, line {line_num}"
                else:
                    return f"line {line_num}"
        
        return "unknown location"
    
    def _find_nearest_section(self, line_num: int, sections: Dict[str, int]) -> str:
        """
        Find the nearest section before the given line number.
        
        Args:
            line_num: The line number
            sections: Dictionary of detected sections
            
        Returns:
            Section name or None
        """
        nearest_section = None
        nearest_line = 0
        
        for section_name, section_line in sections.items():
            if section_line < line_num and section_line > nearest_line:
                nearest_line = section_line
                nearest_section = section_name
        
        return nearest_section
    
    def _find_similar_match(self, keyword: str, latex_cv: str, keyword_item: Dict) -> Optional[Dict]:
        """
        Find similar text in CV using fuzzy string matching.
        
        Args:
            keyword: The keyword to search for
            latex_cv: The LaTeX CV content
            keyword_item: Keyword item with category information
            
        Returns:
            Dictionary with 'text' (matched text) and 'score' (similarity percentage)
            or None if no similar match found above threshold
        """
        # First try exact match (case-insensitive)
        keyword_lower = keyword.lower()
        latex_cv_lower = latex_cv.lower()
        
        if keyword_lower in latex_cv_lower:
            return {
                'text': keyword,
                'score': 100
            }
        
        # Try synonym matching first (for known skills)
        synonym_match = self._check_synonyms(keyword, latex_cv_lower)
        if synonym_match:
            logger.debug(f"Found synonym match for '{keyword}': '{synonym_match}'")
            return {
                'text': synonym_match,
                'score': 95  # High score for synonym matches
            }
        
        # Try quantification matching (e.g., "7+ years" for "5+ years")
        quant_match = self._check_quantifications(keyword, latex_cv_lower)
        if quant_match:
            logger.debug(f"Found quantification match for '{keyword}': '{quant_match}'")
            return {
                'text': quant_match,
                'score': 90  # Good score for quantification matches
            }
        
        # Determine keyword category for hybrid matching
        keyword_category = keyword_item.get('category', 'unknown').lower()
        
        # For hard skills, use stricter matching and skip fuzzy for low scores
        if keyword_category in ['hard', 'technical', 'programming']:
            # Only use exact match for hard skills (or very high similarity)
            logger.debug(f"Hard skill '{keyword}' requires exact match")
            return None
        
        # If no exact match, try fuzzy matching
        # Split CV into words and phrases for better matching
        words = latex_cv.split()
        
        # Try to find similar words/phrases
        best_match = None
        best_score = 0
        
        # Use extractBests to get top N candidates
        candidates = process.extract(
            keyword,
            words,
            scorer=fuzz.token_sort_ratio,
            limit=MAX_CANDIDATES
        )
        
        # Find best candidate above threshold
        for candidate in candidates:
            score = candidate[1]  # Second element is the score
            if score > best_score and score >= SIMILARITY_THRESHOLD:
                best_match = candidate[0]
                best_score = score
        
        if best_match:
            # Check for false positive patterns (for soft skills)
            is_false_positive = self._is_false_positive(keyword, best_match)
            if is_false_positive:
                logger.debug(f"False positive detected: '{keyword}' matched to '{best_match}'")
                return None
            
            logger.debug(f"Found similar match for '{keyword}': '{best_match}' ({best_score}% similarity)")
            return {
                'text': best_match,
                'score': best_score
            }
        
        logger.debug(f"No similar match found for '{keyword}' (threshold: {SIMILARITY_THRESHOLD}%)")
        return None
    
    def _is_false_positive(self, keyword: str, matched_text: str) -> bool:
        """
        Check if a match is likely a false positive (word in context).
        
        Args:
            keyword: The original keyword being searched for
            matched_text: The text that was matched
            
        Returns:
            True if this is likely a false positive, False otherwise
        """
        # Check against false positive patterns
        matched_text_lower = matched_text.lower()
        
        for pattern in FALSE_POSITIVE_PATTERNS:
            if re.search(pattern, matched_text_lower):
                return True
        
        # Check if matched word is part of a longer phrase
        # For soft skills, we want standalone matches
        keyword_lower = keyword.lower()
        if keyword in ['communication', 'management', 'time management', 'problem-solving', 'adaptability']:
            # These are soft skills - check if they're part of longer phrases
            if matched_text_lower != keyword_lower and len(matched_text) > len(keyword) + 5:
                return True
        
        return False
    
    def _extract_context(self, latex_cv: str, keyword: str, context_length: int = 50) -> str:
        """
        Extract context around a keyword match.
        
        Args:
            latex_cv: The LaTeX CV content
            keyword: The keyword to find
            context_length: Number of characters before and after the keyword
            
        Returns:
            Context string with the keyword
        """
        keyword_lower = keyword.lower()
        latex_cv_lower = latex_cv.lower()
        
        # Find the first occurrence
        index = latex_cv_lower.find(keyword_lower)
        if index == -1:
            return ""
        
        # Extract context
        start = max(0, index - context_length)
        end = min(len(latex_cv), index + len(keyword) + context_length)
        
        context = latex_cv[start:end]
        
        # Clean up the context (remove newlines, limit length)
        context = context.replace('\n', ' ').strip()
        
        # Truncate if too long
        if len(context) > 100:
            context = context[:100] + "..."
        
        return context
    
    def _calculate_effectiveness_score(self, latex_cv_lower: str, keyword_lower: str, 
                                      location: str, sections: Dict[str, int]) -> float:
        """
        Calculate effectiveness score based on occurrences and location.
        
        Args:
            latex_cv_lower: Lowercase LaTeX CV
            keyword_lower: Lowercase keyword
            location: Location string
            sections: Dictionary of sections
            
        Returns:
            Effectiveness score (0.0-1.0)
        """
        # Count occurrences
        count = latex_cv_lower.count(keyword_lower)
        
        # Base score based on occurrences (capped at 5)
        occurrence_score = min(count / 5, 1.0)
        
        # Boost if in skills or summary section
        location_lower = location.lower()
        if 'skill' in location_lower or 'summary' in location_lower:
            location_boost = 0.2
        elif 'experience' in location_lower or 'project' in location_lower:
            location_boost = 0.1
        else:
            location_boost = 0.0
        
        # Calculate final score
        score = min(occurrence_score + location_boost, 1.0)
        
        return round(score, 2)
    
    def _determine_usage_quality(self, location: str, sections: Dict[str, int], 
                                 keyword_item: Dict) -> str:
        """
        Determine usage quality description based on location and category.
        
        Args:
            location: Location string
            sections: Dictionary of sections
            keyword_item: Keyword item with metadata
            
        Returns:
            Usage quality description
        """
        location_lower = location.lower()
        category = keyword_item.get('category', '').lower()
        
        # Determine quality based on section
        if 'skill' in location_lower:
            if 'hard' in category or category in ['technical', 'programming']:
                return "excellent - listed as core technical skill"
            else:
                return "good - listed in skills section"
        elif 'summary' in location_lower:
            return "excellent - highlighted in professional summary"
        elif 'experience' in location_lower:
            return "good - demonstrated in work experience"
        elif 'project' in location_lower:
            return "good - applied in project work"
        elif 'education' in location_lower:
            return "fair - mentioned in education"
        else:
            return "present in CV"
    
    def _get_priority_impact(self, priority: int) -> str:
        """
        Convert priority number to impact string.
        
        Args:
            priority: Priority value (1-10)
            
        Returns:
            Priority impact string (high/medium/low)
        """
        if priority >= 8:
            return "high"
        elif priority >= 5:
            return "medium"
        else:
            return "low"
    
    def _get_suggested_location(self, category: str) -> str:
        """
        Get suggested location for missing keyword based on category.
        
        Args:
            category: Keyword category
            
        Returns:
            Suggested location string
        """
        category_lower = category.lower()
        
        if 'skill' in category_lower or 'technical' in category_lower or 'hard' in category_lower:
            return "skills or experience sections"
        elif 'soft' in category_lower:
            return "summary or experience sections"
        elif 'qualification' in category_lower or 'education' in category_lower:
            return "education or certification sections"
        else:
            return "relevant section (skills, experience, or summary)"
    
    def _check_synonyms(self, keyword: str, latex_cv_lower: str) -> Optional[str]:
        """
        Check if any synonyms of the keyword exist in the CV.
        
        Args:
            keyword: The keyword to search for
            latex_cv_lower: Lowercase LaTeX CV content
            
        Returns:
            Found synonym text or None
        """
        keyword_lower = keyword.lower()
        
        # Check if keyword is in our synonym dictionary
        for base_term, synonyms in SKILL_SYNONYMS.items():
            if keyword_lower in [s.lower() for s in synonyms]:
                # This keyword is a synonym, check for other variants
                for synonym in synonyms:
                    if synonym.lower() != keyword_lower and synonym.lower() in latex_cv_lower:
                        return synonym
        
        return None
    
    def _check_quantifications(self, keyword: str, latex_cv_lower: str) -> Optional[str]:
        """
        Check if quantified versions of the keyword exist (e.g., "7+ years" for "5+ years").
        
        Args:
            keyword: The keyword to search for
            latex_cv_lower: Lowercase LaTeX CV content
            
        Returns:
            Found quantified text or None
        """
        keyword_lower = keyword.lower()
        
        # Check for years quantifications
        if 'years' in keyword_lower or 'year' in keyword_lower:
            # Extract the base keyword without quantification
            base = re.sub(r'\d+\+?\s*years?.*$', '', keyword_lower, flags=re.IGNORECASE).strip()
            base = re.sub(r'\d+\+?\s*year.*$', '', base, flags=re.IGNORECASE).strip()
            
            if base:
                # Search for any quantified version
                quant_pattern = rf'(\d+\+?\s*years?\s+{re.escape(base)}|{re.escape(base)}\s+\d+\+?\s*years?)'
                match = re.search(quant_pattern, latex_cv_lower, re.IGNORECASE)
                if match:
                    return match.group(0)
        
        # Check for bachelor's/master's degree quantifications
        if 'bachelor' in keyword_lower or 'master' in keyword_lower:
            degree_pattern = rf'(bachelor[\'\']?\s+of|master[\'\']?\s+of)\s+[^{{}}\n]+'
            match = re.search(degree_pattern, latex_cv_lower, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def get_keyword_effectiveness_summary(self, match_result: Dict) -> Dict:
        """
        Generate a summary of keyword effectiveness.
        
        Args:
            match_result: Result from match_keywords method
            
        Returns:
            Dictionary with effectiveness statistics
        """
        matched_keywords = match_result.get('matched_keywords', [])
        
        if not matched_keywords:
            return {
                'avg_effectiveness': 0.0,
                'excellent_count': 0,
                'good_count': 0,
                'fair_count': 0,
                'poor_count': 0
            }
        
        effectiveness_scores = [
            kw.get('effectiveness_score', 0.0) 
            for kw in matched_keywords
        ]
        
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0.0
        
        return {
            'avg_effectiveness': avg_effectiveness,
            'excellent_count': sum(1 for s in effectiveness_scores if s >= 0.9),
            'good_count': sum(1 for s in effectiveness_scores if 0.7 <= s < 0.9),
            'fair_count': sum(1 for s in effectiveness_scores if 0.5 <= s < 0.7),
            'poor_count': sum(1 for s in effectiveness_scores if s < 0.5)
        }