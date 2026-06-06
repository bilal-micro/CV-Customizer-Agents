import json
import logging

logger = logging.getLogger(__name__)

INITIAL_PROMPT_TEMPLATE = """You are an expert LaTeX CV optimizer for ATS systems. Your task is to improve the given CV to better match job requirements through compelling storytelling and strategic "Skill Translation".

CRITICAL ANALYSIS VALIDATION STEP:
Before modifying the CV, you MUST verify the accuracy of the matching analysis:
1. Check each "matched_keyword" - is it genuinely present in the CV?
2. Check each "missing_keyword" - is it truly absent from the CV?
3. If you find errors in the analysis, note them but proceed with the CV update based on your own accurate assessment
4. Trust your own keyword detection over the provided analysis if there are discrepancies

CORE PRINCIPLES:
- Build ONLY upon the candidate's actual existing experience and skills.
- Create compelling narratives that showcase how foundational skills translate to job requirements.
- NEVER invent metrics, percentages, tools, or experiences that are not explicitly in the original CV.
- Use job keywords to frame and elevate existing work, not to invent new work.
- Add Numbers and statistics to show the impact ( Middle Asuumption acceptable Like Number users , clients )

SKILL TRANSLATION RULES (CRITICAL):
- If a required tool (e.g., "Zapier", "AWS") is missing, DO NOT claim direct experience.
- INSTEAD, map the missing tool to existing foundational knowledge (e.g., mapping Zapier to custom webhooks, or AWS to general cloud architecture).
- ORGANIC EMBEDDING (SHOW, DON'T TELL): Rewrite the bullet point to show the architecture is conceptually identical or adaptable. 
- STRICT BAN: NEVER use phrases like "demonstrating the readiness to adopt", "prepared to use", or "required to rapidly adopt". 
- Correct Example: "Architected custom event-driven workflows and webhooks, establishing the foundational event-processing architecture parallel to platforms like Zapier."
- Correct Example: "Designed a centralized API Gateway and RESTful architecture, ensuring system adaptability with regional e-commerce ecosystems like Zid and Salla."

INSTRUCTIONS:
1. Read the job description and current CV carefully.
2. Analyze the missing keywords and matching analysis.
3. Modify the LaTeX CV to:
   - Apply "Skill Translation" to naturally weave missing keywords into the context of existing foundational skills.
   - Rearrange sections to prioritize the most relevant information matching the job.
   - Improve bullet points using strong action verbs.
   - Elevate the technical tone to reflect a deep understanding of system design and high-performance backend architecture.
   - Ensure all LaTeX syntax remains valid and well-formatted.

IMPORTANT RULES:
- Keep all LaTeX braces, environments, and commands properly closed.
- Maintain a professional, high-impact technical tone.
- 100% TRUTH RATE: Every modification must be traceable back to the original CV content.
- LATEX SYNTAX SAFETY: NEVER use the `$` symbol for regular text or tool names (e.g., NEVER write $(C\\#/WPF)$). Only use standard text formatting. Properly escape special characters like \\&, \\%, and \\#.
- AVOID REDUNDANCY: Ensure the "Professional Summary" does not directly repeat the phrase used in the \\quote{{}} section. Merge them or make them distinct.

STANDARD ENGINEERING PRACTICES (SAFE INFERENCE):
- You MAY safely infer and highlight standard senior engineering practices (e.g., writing technical documentation, rapid self-learning, debugging, technical research, or simplifying complex concepts for non-technical stakeholders) IF they are requested in the job description.
- Weave these soft skills naturally into existing project narratives. For example, if the job requires "Documentation", update an existing project bullet to include: "...and created comprehensive technical documentation to enable cross-functional teams."
- WARNING: This "safe inference" applies ONLY to general practices and soft skills. NEVER infer specific technologies, frameworks, or tools (e.g., WordPress, AWS) unless explicitly found in the original CV.

JOB TITLE: {job_title}

EXTRACTED KEYWORDS:
{keywords_json}

MATCHING ANALYSIS:
{matching_analysis_json}

{additional_skills_section}
CURRENT LATEX CV:
{latex_cv}

OUTPUT REQUIREMENTS:
- Return ONLY the updated LaTeX code.
- No markdown formatting, no code blocks around the output.
- Start with the first LaTeX command and end with the last LaTeX command.
- Ensure the output is valid, compilable LaTeX.

Please provide the updated LaTeX CV now:"""

ITERATION_PROMPT_TEMPLATE = """You are an expert LaTeX CV optimizer for ATS systems. This is iteration {iteration_number} of CV optimization through compelling storytelling and strategic "Skill Translation".

CRITICAL ANALYSIS VALIDATION STEP:
Before modifying the CV, you MUST verify the accuracy of the matching analysis:
1. Check each "matched_keyword" - is it genuinely present in the CV?
2. Check each "missing_keyword" - is it truly absent from the CV?
3. If you find errors in the analysis, note them but proceed with the CV update based on your own accurate assessment
4. Trust your own keyword detection over the provided analysis if there are discrepancies

CORE PRINCIPLES:
- Build ONLY upon the candidate's actual existing experience and skills.
- Create compelling narratives that showcase how foundational skills translate to job requirements.
- NEVER invent metrics, percentages, tools, or experiences that are not explicitly in the original CV.
- Use job keywords to frame and elevate existing work, not to invent new work.

SKILL TRANSLATION RULES (CRITICAL):
- If a required tool (e.g., "Zapier", "AWS SQS") is missing from the CV, DO NOT claim direct experience with it.
- INSTEAD, map the missing tool to the candidate's existing architectural knowledge (e.g., mapping Zapier to custom webhooks/Celery/message brokers, or mapping AWS to general cloud architecture).
- Rewrite the bullet point to bridge the two. Example: "Architected custom event-driven workflows and API integrations, demonstrating the foundational system design expertise required to rapidly adopt and deploy automation platforms like Zapier."

PREVIOUS ITERATION FEEDBACK (from ATS Rater):
{feedback_json}

JOB TITLE: {job_title}

EXTRACTED KEYWORDS:
{keywords_json}

MATCHING ANALYSIS:
{matching_analysis_json}

{additional_skills_section}
CURRENT LATEX CV (from iteration {previous_iteration}):
{latex_cv}

INSTRUCTIONS FOR THIS ITERATION:
Based on the ATS Rater's feedback provided above, make targeted improvements to address the identified issues:

HOW TO USE THE FEEDBACK:
- Review "improvement_suggestions" carefully - these are specific, actionable improvements from the ATS Rater
- Address "weak_points" by improving those areas of the CV
- Use "ats_breakdown" to understand which scoring areas need improvement (formatting, keyword_density, section_structure, content_quality)
- Consider "strong_points" when maintaining what works well in the CV
- Use "overall_assessment" to understand the general direction for improvement

SPECIFIC IMPROVEMENT STEPS:
1. Review the feedback carefully, especially the improvement_suggestions and weak_points
2. Focus on the specific areas mentioned in the feedback
3. Apply "Skill Translation" to naturally weave missing keywords into the context of existing foundational skills
4. Rearrange sections to prioritize the most relevant information matching the job
5. Improve bullet points using strong action verbs from the job description
6. Elevate the technical tone to reflect a deep understanding of system design and high-performance backend architecture
7. Ensure all LaTeX syntax remains valid and well-formatted
8. Address the "improvement_suggestions" specifically - these are the top priorities

IMPORTANT RULES:
- Keep all LaTeX braces, environments, and commands properly closed
- Maintain a professional, high-impact technical tone
- 100% TRUTH RATE: Every modification must be traceable back to the original CV content

STANDARD ENGINEERING PRACTICES (SAFE INFERENCE):
- You MAY safely infer and highlight standard senior engineering practices (e.g., writing technical documentation, rapid self-learning, debugging, technical research, or simplifying complex concepts for non-technical stakeholders) IF they are requested in the job description
- Weave these soft skills naturally into existing project narratives. For example, if the job requires "Documentation", update an existing project bullet to include: "...and created comprehensive technical documentation to enable cross-functional teams"
- WARNING: This "safe inference" applies ONLY to general practices and soft skills. NEVER infer specific technologies, frameworks, or tools (e.g., WordPress, AWS) unless explicitly found in the original CV

OUTPUT REQUIREMENTS:
- Return ONLY the updated LaTeX code
- No markdown formatting, no code blocks around the output
- Start with the first LaTeX command and end with the last LaTeX command
- Ensure the output is valid, compilable LaTeX

Please provide the updated LaTeX CV now:"""


class CVUpdaterAgent:
    def generate_prompt(self, job_title: str, keywords: dict, matching_analysis: dict, 
                        latex_cv: str, iteration_number: int = 1, feedback: dict = None,
                        additional_skills: str = '') -> str:
        """
        Generate a prompt for the external LLM to improve the CV.
        
        Args:
            job_title: The job title
            keywords: Extracted keywords from the job
            matching_analysis: Analysis of CV-job match
            latex_cv: Current LaTeX CV content
            iteration_number: Current iteration number (1, 2, or 3)
            feedback: Feedback from Agent 4 (for iterations 2 and 3)
            additional_skills: Additional skills, tools, and technologies provided by the candidate
        
        Returns:
            A formatted prompt string ready to be copied to an external LLM
        """
        keywords_json = json.dumps(keywords, indent=2)
        matching_analysis_json = json.dumps(matching_analysis, indent=2)
        
        # Build additional skills section if provided
        additional_skills_section = ''
        if additional_skills and additional_skills.strip():
            additional_skills_section = (
                "CANDIDATE'S ADDITIONAL SKILLS & EXPERIENCE (provided by candidate):\n"
                "The following is a comprehensive list of tools, technologies, frameworks, and skills "
                "that the candidate has direct experience with. Use this information to:\n"
                "1. Enrich the CV by incorporating these skills where relevant to the job requirements.\n"
                "2. Strengthen \"Skill Translation\" by mapping job requirements to these known competencies.\n"
                "3. Add these skills to appropriate sections (Skills, Technologies, Projects) when they match "
                "the job's needs.\n"
                "IMPORTANT: Only include skills that are genuinely relevant to the target position.\n\n"
                f"{additional_skills.strip()}\n"
            )
        
        if iteration_number == 1:
            # First iteration - initial prompt
            prompt = INITIAL_PROMPT_TEMPLATE.format(
                job_title=job_title,
                keywords_json=keywords_json,
                matching_analysis_json=matching_analysis_json,
                additional_skills_section=additional_skills_section,
                latex_cv=latex_cv,
            )
        else:
            # Subsequent iterations - include feedback
            feedback_json = json.dumps(feedback or {}, indent=2)
            previous_iteration = iteration_number - 1
            prompt = ITERATION_PROMPT_TEMPLATE.format(
                iteration_number=iteration_number,
                previous_iteration=previous_iteration,
                feedback_json=feedback_json,
                job_title=job_title,
                keywords_json=keywords_json,
                matching_analysis_json=matching_analysis_json,
                additional_skills_section=additional_skills_section,
                latex_cv=latex_cv,
            )
        
        logger.info(f"Generated prompt for iteration {iteration_number}")
        return prompt
    
    def validate_manual_latex(self, latex_content: str) -> dict:
        """
        Validate manually submitted LaTeX content.
        
        Args:
            latex_content: The LaTeX content to validate
        
        Returns:
            Dictionary with 'valid' (bool) and 'error' (str or None)
        """
        if not latex_content or not latex_content.strip():
            return {'valid': False, 'error': 'LaTeX content is empty'}
        
        # Basic LaTeX structure validation
        if r'\begin{document}' not in latex_content:
            return {'valid': False, 'error': 'LaTeX must contain \\begin{document}'}
        
        if r'\end{document}' not in latex_content:
            return {'valid': False, 'error': 'LaTeX must contain \\end{document}'}
        
        # Check for balanced braces (basic check)
        open_braces = latex_content.count('{')
        close_braces = latex_content.count('}')
        if open_braces != close_braces:
            return {'valid': False, 'error': f'Unbalanced braces: {open_braces} open, {close_braces} close'}
        
        logger.info("Manual LaTeX validation passed")
        return {'valid': True, 'error': None}