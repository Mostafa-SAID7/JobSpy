"""
Skill Extraction Service

Domain service for extracting skills from job descriptions.
Single responsibility: skill extraction algorithm.
"""

import re
from typing import List, Set, Dict


class SkillExtractionService:
    """
    Domain service for extracting skills from text.
    
    Single Responsibility: Extract and normalize skills from job descriptions.
    
    Uses pattern matching to identify:
    - Programming languages
    - Frameworks and libraries
    - Databases
    - Cloud platforms
    - Tools and technologies
    """
    
    # Skill patterns organized by category
    SKILL_PATTERNS: Dict[str, List[str]] = {
        'programming_languages': [
            r'\b(?:python|java|javascript|typescript|c\+\+|c#|php|ruby|go|rust|swift|kotlin|scala)\b',
            r'\b(?:r|matlab|perl|shell|bash|powershell|sql|html|css)\b',
        ],
        'frameworks': [
            r'\b(?:react|angular|vue|svelte|next\.js|nuxt)\b',
            r'\b(?:django|flask|fastapi|express|spring|laravel|rails)\b',
            r'\b(?:tensorflow|pytorch|scikit-learn|keras|pandas|numpy)\b',
            r'\b(?:junit|pytest|jest|mocha|cypress)\b',
        ],
        'databases': [
            r'\b(?:mysql|postgresql|mongodb|redis|elasticsearch|cassandra)\b',
            r'\b(?:oracle|sqlite|mariadb|dynamodb|firestore)\b',
        ],
        'cloud_platforms': [
            r'\b(?:aws|azure|gcp|google cloud|amazon web services|microsoft azure)\b',
            r'\b(?:heroku|digitalocean|linode|vercel|netlify)\b',
        ],
        'devops_tools': [
            r'\b(?:docker|kubernetes|jenkins|gitlab|github actions|circleci)\b',
            r'\b(?:terraform|ansible|puppet|chef|vagrant)\b',
        ],
        'version_control': [
            r'\b(?:git|github|gitlab|bitbucket|svn)\b',
        ],
        'design_tools': [
            r'\b(?:figma|sketch|adobe xd|photoshop|illustrator|indesign)\b',
        ],
        'project_management': [
            r'\b(?:jira|confluence|trello|asana|monday|notion)\b',
        ],
        'communication': [
            r'\b(?:slack|teams|zoom|discord)\b',
        ],
    }
    
    def __init__(self):
        """Initialize skill extraction service"""
        # Compile patterns for better performance
        self._compiled_patterns = {}
        for category, patterns in self.SKILL_PATTERNS.items():
            self._compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def extract_skills(
        self,
        description: str,
        requirements: List[str] = None
    ) -> List[str]:
        """
        Extract skills from job description and requirements.
        
        Args:
            description: Job description text
            requirements: List of requirement strings
        
        Returns:
            List of unique extracted skills (lowercase, normalized)
        """
        # Combine all text
        text_parts = [description]
        if requirements:
            text_parts.extend(requirements)
        
        combined_text = " ".join(text_parts).lower()
        
        # Extract skills
        extracted_skills: Set[str] = set()
        
        for category, compiled_patterns in self._compiled_patterns.items():
            for pattern in compiled_patterns:
                matches = pattern.findall(combined_text)
                extracted_skills.update(matches)
        
        # Normalize and deduplicate
        normalized_skills = self._normalize_skills(extracted_skills)
        
        return sorted(list(normalized_skills))
    
    def extract_by_category(
        self,
        description: str,
        requirements: List[str] = None
    ) -> Dict[str, List[str]]:
        """
        Extract skills organized by category.
        
        Args:
            description: Job description text
            requirements: List of requirement strings
        
        Returns:
            Dictionary mapping category to list of skills
        """
        # Combine all text
        text_parts = [description]
        if requirements:
            text_parts.extend(requirements)
        
        combined_text = " ".join(text_parts).lower()
        
        # Extract by category
        skills_by_category = {}
        
        for category, compiled_patterns in self._compiled_patterns.items():
            category_skills: Set[str] = set()
            
            for pattern in compiled_patterns:
                matches = pattern.findall(combined_text)
                category_skills.update(matches)
            
            if category_skills:
                skills_by_category[category] = sorted(list(category_skills))
        
        return skills_by_category
    
    def _normalize_skills(self, skills: Set[str]) -> Set[str]:
        """
        Normalize skill names.
        
        Handles:
        - Case normalization
        - Alias resolution (e.g., "js" -> "javascript")
        - Whitespace trimming
        
        Args:
            skills: Set of raw skill strings
        
        Returns:
            Set of normalized skill strings
        """
        normalized = set()
        
        # Skill aliases
        aliases = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'k8s': 'kubernetes',
            'tf': 'terraform',
            'next.js': 'nextjs',
            'vue.js': 'vue',
            'react.js': 'react',
            'node.js': 'nodejs',
        }
        
        for skill in skills:
            skill = skill.strip().lower()
            
            # Apply alias if exists
            skill = aliases.get(skill, skill)
            
            if skill:
                normalized.add(skill)
        
        return normalized
    
    def count_skills_by_category(
        self,
        description: str,
        requirements: List[str] = None
    ) -> Dict[str, int]:
        """
        Count skills by category.
        
        Useful for analyzing job requirements.
        
        Args:
            description: Job description text
            requirements: List of requirement strings
        
        Returns:
            Dictionary mapping category to skill count
        """
        skills_by_category = self.extract_by_category(description, requirements)
        
        return {
            category: len(skills)
            for category, skills in skills_by_category.items()
        }
    
    def has_skill(self, description: str, skill: str) -> bool:
        """
        Check if description mentions a specific skill.
        
        Args:
            description: Job description text
            skill: Skill to search for
        
        Returns:
            True if skill is mentioned
        """
        pattern = re.compile(rf'\b{re.escape(skill)}\b', re.IGNORECASE)
        return bool(pattern.search(description))
    
    def skill_match_percentage(
        self,
        job_skills: List[str],
        candidate_skills: List[str]
    ) -> float:
        """
        Calculate percentage of candidate skills that match job requirements.
        
        Args:
            job_skills: Skills required by job
            candidate_skills: Skills possessed by candidate
        
        Returns:
            Match percentage (0.0 to 100.0)
        """
        if not job_skills:
            return 100.0  # No requirements = perfect match
        
        if not candidate_skills:
            return 0.0
        
        job_skills_set = {skill.lower() for skill in job_skills}
        candidate_skills_set = {skill.lower() for skill in candidate_skills}
        
        matching_skills = job_skills_set.intersection(candidate_skills_set)
        
        return (len(matching_skills) / len(job_skills_set)) * 100.0
