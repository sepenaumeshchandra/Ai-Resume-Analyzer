import re
import io
from datetime import datetime

# Optional heavy imports — gracefully degraded if not installed
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from docx import Document as DocxDocument
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


# ------------------------------------------------------------------ #
#  SKILL LISTS                                                         #
# ------------------------------------------------------------------ #
TECH_SKILLS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "swift", "kotlin", "ruby", "php", "scala", "r", "matlab", "perl",
    "dart", "elixir", "haskell", "lua", "bash", "shell",
    # Web
    "html", "css", "react", "angular", "vue", "nextjs", "nuxtjs", "svelte",
    "django", "flask", "fastapi", "spring", "node.js", "nodejs", "express",
    "graphql", "rest", "soap", "websocket",
    # Data / ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
    "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn",
    "nlp", "computer vision", "opencv", "hugging face", "transformers",
    "data science", "data analysis", "big data", "hadoop", "spark", "kafka",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "devops", "linux", "nginx",
    # Databases
    "sql", "mysql", "postgresql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "supabase",
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",
    # Other
    "git", "github", "gitlab", "jira", "agile", "scrum", "microservices",
    "blockchain", "solidity", "unity", "unreal engine",
}

SOFT_SKILLS = {
    "communication", "teamwork", "leadership", "problem solving", "critical thinking",
    "time management", "adaptability", "creativity", "collaboration", "attention to detail",
    "project management", "conflict resolution", "analytical thinking", "decision making",
    "emotional intelligence", "negotiation", "presentation", "mentoring", "innovation",
}

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "b.e", "m.e", "b.sc", "m.sc",
    "mba", "bca", "mca", "diploma", "associate", "doctorate", "degree", "university",
    "college", "institute", "school", "engineering", "technology", "science",
]

EXPERIENCE_PATTERNS = [
    r"(?:software|data|ml|ai|web|backend|frontend|full.?stack|mobile|cloud|devops|"
    r"product|project|tech|senior|junior|lead|principal|staff|associate)\s+"
    r"(?:engineer|developer|analyst|scientist|architect|manager|intern|consultant)",
    r"intern(?:ship)?",
    r"\b(?:worked|developed|designed|built|implemented|managed|led|created|"
    r"maintained|optimized|deployed|architected)\b.{5,80}",
]

PROJECT_PATTERNS = [
    r"(?:project|app|application|system|platform|tool|website|api|service|bot|"
    r"dashboard|pipeline|framework|library)[\s:]+[A-Za-z0-9\s\-_]{3,60}",
    r"(?:built|developed|created|implemented|designed)\s+(?:a|an|the)?\s*"
    r"[A-Za-z0-9\s\-_]{3,60}(?:app|system|tool|platform|website|api|service|bot)",
]


class ResumeParser:
    def __init__(self):
        self.tech_skills = TECH_SKILLS
        self.soft_skills = SOFT_SKILLS

    # ------------------------------------------------------------------ #
    #  PUBLIC API                                                          #
    # ------------------------------------------------------------------ #
    def extract_all(self, uploaded_file) -> dict:
        text = self._extract_text(uploaded_file)
        return {
            'raw_text':   text,
            'name':       self._extract_name(text),
            'email':      self._extract_email(text),
            'phone':      self._extract_phone(text),
            'linkedin':   self._extract_linkedin(text),
            'github':     self._extract_github(text),
            'skills':     self._extract_skills(text),
            'education':  self._extract_education(text),
            'experience': self._extract_experience(text),
            'projects':   self._extract_projects(text),
            'word_count': len(text.split()),
            'char_count': len(text),
        }

    def generate_improved(self, resume_data: dict, ats_result: dict) -> bytes:
        """Return a plain-text bytes representation of an improved resume."""
        lines = []
        lines.append(resume_data.get('name', 'Your Name'))
        lines.append(resume_data.get('email', '') + "  |  " + resume_data.get('phone', ''))
        if resume_data.get('linkedin'):
            lines.append(resume_data['linkedin'])
        lines.append("")
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("-" * 40)
        lines.append(
            "Results-driven professional with expertise in "
            + ", ".join(resume_data.get('skills', [])[:5])
            + ". Proven track record of delivering high-impact solutions."
        )
        lines.append("")
        lines.append("SKILLS")
        lines.append("-" * 40)
        lines.append(", ".join(resume_data.get('skills', [])))
        lines.append("")
        lines.append("EXPERIENCE")
        lines.append("-" * 40)
        for exp in resume_data.get('experience', []):
            lines.append(f"• {exp}")
        lines.append("")
        lines.append("EDUCATION")
        lines.append("-" * 40)
        for edu in resume_data.get('education', []):
            lines.append(f"• {edu}")
        lines.append("")
        lines.append("PROJECTS")
        lines.append("-" * 40)
        for proj in resume_data.get('projects', []):
            lines.append(f"• {proj}")
        return "\n".join(lines).encode('utf-8')

    # ------------------------------------------------------------------ #
    #  TEXT EXTRACTION                                                     #
    # ------------------------------------------------------------------ #
    def _extract_text(self, uploaded_file) -> str:
        name = uploaded_file.name.lower()
        raw = uploaded_file.read()
        uploaded_file.seek(0)

        if name.endswith('.pdf'):
            return self._pdf_to_text(raw)
        elif name.endswith('.docx'):
            return self._docx_to_text(raw)
        else:
            for enc in ('utf-8', 'latin-1', 'cp1252'):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode('utf-8', errors='replace')

    def _pdf_to_text(self, raw: bytes) -> str:
        if not HAS_PDFPLUMBER:
            return raw.decode('latin-1', errors='replace')
        try:
            with pdfplumber.open(io.BytesIO(raw)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            return "\n".join(pages)
        except Exception:
            return ""

    def _docx_to_text(self, raw: bytes) -> str:
        if not HAS_DOCX:
            return raw.decode('latin-1', errors='replace')
        try:
            doc = DocxDocument(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception:
            return ""

    # ------------------------------------------------------------------ #
    #  FIELD EXTRACTORS                                                    #
    # ------------------------------------------------------------------ #
    def _extract_email(self, text: str) -> str:
        m = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
        return m.group(0) if m else ""

    def _extract_phone(self, text: str) -> str:
        m = re.search(
            r'(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}', text
        )
        return m.group(0).strip() if m else ""

    def _extract_linkedin(self, text: str) -> str:
        m = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        return "https://" + m.group(0) if m else ""

    def _extract_github(self, text: str) -> str:
        m = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
        return "https://" + m.group(0) if m else ""

    def _extract_name(self, text: str) -> str:
        # Email line hint
        email = self._extract_email(text)
        if email:
            local = email.split('@')[0]
            parts = re.split(r'[._\-]', local)
            if 2 <= len(parts) <= 3:
                name = " ".join(p.capitalize() for p in parts if len(p) > 1)
                if name:
                    return name
        # First non-empty line that looks like a name
        for line in text.split('\n')[:10]:
            line = line.strip()
            words = line.split()
            if (2 <= len(words) <= 4
                    and all(re.match(r'^[A-Za-z\.\-]+$', w) for w in words)
                    and not any(kw in line.lower() for kw in
                                ['resume', 'cv', 'curriculum', 'vitae', 'profile', 'summary'])):
                return line
        return "Not found"

    def _extract_skills(self, text: str) -> list:
        text_lower = text.lower()
        found = set()
        for skill in self.tech_skills | self.soft_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found.add(skill.title())
        return sorted(found)

    def _extract_education(self, text: str) -> list:
        results = []
        for line in text.split('\n'):
            line_l = line.lower()
            if any(kw in line_l for kw in EDUCATION_KEYWORDS) and len(line.strip()) > 5:
                clean = line.strip()
                if clean and clean not in results:
                    results.append(clean)
        return results[:8]

    def _extract_experience(self, text: str) -> list:
        results = []
        for line in text.split('\n'):
            line_s = line.strip()
            if not line_s:
                continue
            for pat in EXPERIENCE_PATTERNS:
                if re.search(pat, line_s, re.IGNORECASE):
                    if len(line_s) > 10 and line_s not in results:
                        results.append(line_s)
                    break
        return results[:15]

    def _extract_projects(self, text: str) -> list:
        results = []
        in_project_section = False
        for line in text.split('\n'):
            line_s = line.strip()
            if re.search(r'\bprojects?\b', line_s, re.IGNORECASE) and len(line_s) < 30:
                in_project_section = True
                continue
            if in_project_section:
                if re.search(r'\b(experience|education|skills|certifications|awards)\b',
                             line_s, re.IGNORECASE) and len(line_s) < 30:
                    in_project_section = False
                elif len(line_s) > 10:
                    results.append(line_s)
        # Also scan full text for project patterns
        for pat in PROJECT_PATTERNS:
            for m in re.finditer(pat, text, re.IGNORECASE):
                found = m.group(0).strip()
                if found not in results:
                    results.append(found)
        return list(dict.fromkeys(results))[:10]