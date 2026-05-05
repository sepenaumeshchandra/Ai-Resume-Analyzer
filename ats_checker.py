import re
from resume_parser import TECH_SKILLS, SOFT_SKILLS

POWER_VERBS = [
    "achieved", "built", "created", "delivered", "designed", "developed",
    "engineered", "established", "executed", "generated", "improved",
    "implemented", "increased", "launched", "led", "managed", "optimized",
    "produced", "reduced", "resolved", "scaled", "shipped", "spearheaded",
    "streamlined", "transformed",
]

IMPORTANT_SECTIONS = [
    "experience", "education", "skills", "projects", "summary", "objective",
    "certifications", "achievements", "publications", "awards",
]

FORBIDDEN_CHARS = ["♦", "◆", "●", "►", "✓", "✔", "◉", "☑", "★", "☆"]


class ATSChecker:
    def analyze(self, resume_data: dict) -> dict:
        text = resume_data.get('raw_text', '')
        text_lower = text.lower()
        skills = resume_data.get('skills', [])

        # 1. Keywords found (ATS keyword density)
        all_skills = TECH_SKILLS | SOFT_SKILLS
        keywords_found = sum(
            1 for s in all_skills
            if re.search(r'\b' + re.escape(s) + r'\b', text_lower)
        )
        keywords_found = min(keywords_found, 10)

        # 2. Formatting score
        formatting_score = self._formatting_score(text)

        # 3. Sections score
        sections_score = self._sections_score(text_lower)

        # 4. Overall score
        kw_score    = min(keywords_found * 10, 40)
        fmt_score   = formatting_score * 0.30
        sec_score   = sections_score   * 0.30
        score = round(kw_score + fmt_score + sec_score, 1)
        score = max(10.0, min(score, 100.0))

        # 5. Issues
        issues = self._collect_issues(resume_data, text, text_lower)

        # 6. Suggestions
        suggestions = self._build_suggestions(resume_data, text_lower, keywords_found)

        return {
            'score':            score,
            'keywords_found':   keywords_found,
            'formatting_score': formatting_score,
            'sections_score':   sections_score,
            'issues':           issues,
            'suggestions':      suggestions,
        }

    # ------------------------------------------------------------------ #
    #  SCORING HELPERS                                                     #
    # ------------------------------------------------------------------ #
    def _formatting_score(self, text: str) -> float:
        score = 100.0
        # Tables / complex chars reduce ATS readability
        if any(ch in text for ch in FORBIDDEN_CHARS):
            score -= 15
        # Very short resume
        words = len(text.split())
        if words < 150:
            score -= 25
        elif words < 300:
            score -= 10
        # Very long resume
        if words > 1200:
            score -= 10
        # Quantified achievements (numbers)
        numbers = re.findall(r'\b\d+\b', text)
        if len(numbers) < 5:
            score -= 15
        # Power verbs present
        verb_count = sum(1 for v in POWER_VERBS if v in text.lower())
        if verb_count < 3:
            score -= 10
        # Contact info present
        if not re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text):
            score -= 20
        return max(0.0, min(round(score, 1), 100.0))

    def _sections_score(self, text_lower: str) -> float:
        found = sum(1 for s in IMPORTANT_SECTIONS if s in text_lower)
        return round((found / len(IMPORTANT_SECTIONS)) * 100, 1)

    # ------------------------------------------------------------------ #
    #  ISSUES                                                              #
    # ------------------------------------------------------------------ #
    def _collect_issues(self, resume_data: dict, text: str, text_lower: str) -> list:
        issues = []

        if not resume_data.get('email'):
            issues.append({'severity': 'high',
                           'message': 'No email address found — ATS cannot contact you.'})

        if not resume_data.get('phone'):
            issues.append({'severity': 'high',
                           'message': 'No phone number found.'})

        if not resume_data.get('name') or resume_data['name'] == 'Not found':
            issues.append({'severity': 'high',
                           'message': 'Could not detect your name. Make it the largest text at the top.'})

        word_count = len(text.split())
        if word_count < 200:
            issues.append({'severity': 'high',
                           'message': f'Resume is very short ({word_count} words). Aim for 400–800 words.'})
        elif word_count > 1000:
            issues.append({'severity': 'medium',
                           'message': f'Resume is long ({word_count} words). Consider trimming to 1–2 pages.'})

        if len(resume_data.get('skills', [])) < 5:
            issues.append({'severity': 'medium',
                           'message': 'Fewer than 5 skills detected. Add a dedicated Skills section.'})

        if not resume_data.get('experience'):
            issues.append({'severity': 'medium',
                           'message': 'No work experience detected. Ensure the section is clearly labelled.'})

        if not resume_data.get('education'):
            issues.append({'severity': 'low',
                           'message': 'No education section detected.'})

        numbers = re.findall(r'\b\d+[\+%]?\b', text)
        if len(numbers) < 5:
            issues.append({'severity': 'medium',
                           'message': 'Few quantified achievements found. Add metrics (e.g., "Reduced load time by 40%").'})

        verb_count = sum(1 for v in POWER_VERBS if v in text_lower)
        if verb_count < 3:
            issues.append({'severity': 'low',
                           'message': 'Use more action verbs (achieved, built, optimized, led…) to start bullet points.'})

        if not resume_data.get('linkedin') and 'linkedin' not in text_lower:
            issues.append({'severity': 'low',
                           'message': 'No LinkedIn URL found. Add it to boost credibility.'})

        return issues

    # ------------------------------------------------------------------ #
    #  SUGGESTIONS                                                         #
    # ------------------------------------------------------------------ #
    def _build_suggestions(self, resume_data: dict, text_lower: str,
                            keywords_found: int) -> list:
        suggestions = []

        if keywords_found < 5:
            suggestions.append({
                'title':       'Add More Technical Keywords',
                'description': 'ATS systems scan for specific skill keywords. Your resume has few detectable skills.',
                'action':      'Mirror the exact keywords from the job description in your Skills section.',
                'example':     'Skills: Python, Django, REST APIs, AWS, PostgreSQL, Docker',
            })

        if len(resume_data.get('experience', [])) < 3:
            suggestions.append({
                'title':       'Expand Work Experience',
                'description': 'More detailed experience entries improve ATS ranking and recruiter confidence.',
                'action':      'Add 3–5 bullet points per role using the CAR format (Context, Action, Result).',
                'example':     '• Reduced API response time by 35% by implementing Redis caching (Python, Redis)',
            })

        if not re.search(r'\b\d+[\+%]?\b.*(?:improve|increase|reduce|save|grow)', text_lower):
            suggestions.append({
                'title':       'Quantify Your Achievements',
                'description': 'Numbers make your impact concrete and memorable.',
                'action':      'Add at least one metric per bullet point.',
                'example':     '• Increased test coverage from 45% → 92%, reducing production bugs by 60%',
            })

        if 'summary' not in text_lower and 'objective' not in text_lower:
            suggestions.append({
                'title':       'Add a Professional Summary',
                'description': 'A 3–4 line summary at the top gives recruiters an immediate value proposition.',
                'action':      'Write a summary highlighting your years of experience, top skills, and career goal.',
                'example':     ('SUMMARY\nFull-Stack Developer with 3 years of experience in React & Django. '
                                'Passionate about building scalable APIs and intuitive UIs.'),
            })

        if not resume_data.get('github') and 'github' not in text_lower:
            suggestions.append({
                'title':       'Add Your GitHub / Portfolio',
                'description': 'For technical roles, a GitHub link is almost mandatory.',
                'action':      'Add "GitHub: github.com/your-username" in the header.',
            })

        return suggestions