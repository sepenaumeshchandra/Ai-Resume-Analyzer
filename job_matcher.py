import re
import random
from resume_parser import TECH_SKILLS, SOFT_SKILLS

LEARNING_RESOURCES = {
    "python":           {"Coursera": "https://www.coursera.org/learn/python",
                         "freeCodeCamp": "https://www.freecodecamp.org/news/tag/python/",
                         "Official Docs": "https://docs.python.org/3/tutorial/"},
    "javascript":       {"MDN": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript",
                         "freeCodeCamp": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/"},
    "react":            {"Official Docs": "https://react.dev/learn",
                         "Scrimba": "https://scrimba.com/learn/learnreact"},
    "machine learning": {"Coursera": "https://www.coursera.org/learn/machine-learning",
                         "fast.ai": "https://www.fast.ai/"},
    "aws":              {"AWS Training": "https://aws.amazon.com/training/",
                         "freeCodeCamp": "https://www.freecodecamp.org/news/tag/aws/"},
    "docker":           {"Official Docs": "https://docs.docker.com/get-started/",
                         "YouTube": "https://www.youtube.com/results?search_query=docker+tutorial"},
    "kubernetes":       {"Official Docs": "https://kubernetes.io/docs/tutorials/",
                         "KodeKloud": "https://kodekloud.com/courses/kubernetes-for-the-absolute-beginners/"},
    "sql":              {"SQLZoo": "https://sqlzoo.net/",
                         "Mode Analytics": "https://mode.com/sql-tutorial/"},
    "default":          {"Udemy": "https://www.udemy.com/",
                         "YouTube": "https://www.youtube.com/",
                         "freeCodeCamp": "https://www.freecodecamp.org/"},
}

SAMPLE_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple", "Netflix", "Spotify",
    "Uber", "Airbnb", "Stripe", "Shopify", "Salesforce", "Oracle", "IBM",
    "Infosys", "TCS", "Wipro", "HCL", "Cognizant", "Accenture",
    "Startups Inc.", "TechCorp", "DataVentures", "CloudBase", "AI Dynamics",
]

SAMPLE_LOCATIONS = [
    "Bangalore, India", "Hyderabad, India", "Mumbai, India", "Pune, India",
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
    "Remote", "Hybrid (Bangalore)", "Hybrid (Hyderabad)",
]

SALARY_RANGES = [
    "₹6–10 LPA", "₹10–18 LPA", "₹18–30 LPA", "₹30–50 LPA",
    "$80k–$110k", "$110k–$150k", "$150k–$200k",
]

JOB_TYPES = ["Full-time", "Remote", "Hybrid", "Contract", "Internship"]


class JobMatcher:
    # ------------------------------------------------------------------ #
    #  CORE MATCH ANALYSIS                                                 #
    # ------------------------------------------------------------------ #
    def analyze_match(self, resume_skills: list, job_description: str) -> dict:
        jd_lower = job_description.lower()

        # Extract required skills from JD
        all_skills = TECH_SKILLS | SOFT_SKILLS
        jd_skills = {
            s for s in all_skills
            if re.search(r'\b' + re.escape(s) + r'\b', jd_lower)
        }
        # Also catch raw words that look like skills
        jd_words = set(re.findall(r'\b[a-z][a-z0-9\.\+\#]{1,20}\b', jd_lower))
        jd_skills |= jd_words & all_skills

        resume_set = {s.lower() for s in resume_skills}

        matched  = [s for s in jd_skills if s in resume_set]
        missing  = [s for s in jd_skills if s not in resume_set]

        total = len(jd_skills) if jd_skills else 1
        match_pct = round((len(matched) / total) * 100) if total else 0

        # Experience match heuristic
        exp_match = 0
        exp_nums = re.findall(r'(\d+)\+?\s*years?', jd_lower)
        if exp_nums:
            required_years = int(exp_nums[0])
            # Give partial credit always (we don't know actual years from JD alone)
            exp_match = max(0, 100 - required_years * 10)
        else:
            exp_match = 75  # No explicit requirement

        return {
            'match_score':          min(match_pct, 100),
            'matched':              sorted(matched),
            'missing':              sorted(missing),
            'matched_skills':       len(matched),
            'total_skills':         total,
            'missing_skills_count': len(missing),
            'exp_match':            exp_match,
            'jd_skills':            sorted(jd_skills),
        }

    # ------------------------------------------------------------------ #
    #  JOB RECOMMENDATIONS                                                 #
    # ------------------------------------------------------------------ #
    def get_job_recommendations(self, matched_skills: list, job_description: str) -> list:
        role = self._infer_role(job_description)
        jobs = []
        random.seed(42)
        companies = random.sample(SAMPLE_COMPANIES, min(6, len(SAMPLE_COMPANIES)))
        for i, company in enumerate(companies):
            match_score = max(50, 95 - i * 7 + random.randint(-5, 5))
            jobs.append({
                'title':     role,
                'company':   company,
                'location':  random.choice(SAMPLE_LOCATIONS),
                'salary':    random.choice(SALARY_RANGES),
                'match':     match_score,
                'type':      random.choice(JOB_TYPES),
                'apply_url': f"https://www.linkedin.com/jobs/search/?keywords={role.replace(' ', '+')}",
            })
        return sorted(jobs, key=lambda x: x['match'], reverse=True)

    # ------------------------------------------------------------------ #
    #  LEARNING RESOURCES                                                  #
    # ------------------------------------------------------------------ #
    def get_learning_resources(self, skill: str) -> dict:
        key = skill.lower()
        return LEARNING_RESOURCES.get(key, LEARNING_RESOURCES['default'])

    # ------------------------------------------------------------------ #
    #  HELPERS                                                             #
    # ------------------------------------------------------------------ #
    def _infer_role(self, job_description: str) -> str:
        jd = job_description.lower()
        role_map = {
            "data scientist":         ["data science", "machine learning", "ml engineer"],
            "frontend developer":     ["react", "angular", "vue", "frontend"],
            "backend developer":      ["django", "flask", "spring", "backend", "node.js"],
            "full stack developer":   ["full stack", "fullstack", "mern", "mean"],
            "devops engineer":        ["devops", "kubernetes", "docker", "ci/cd", "terraform"],
            "mobile developer":       ["android", "ios", "flutter", "react native"],
            "machine learning engineer": ["deep learning", "tensorflow", "pytorch", "nlp"],
            "data analyst":           ["sql", "tableau", "power bi", "data analyst"],
            "cloud engineer":         ["aws", "azure", "gcp", "cloud"],
            "software engineer":      ["software engineer", "software developer", "swe"],
        }
        for role, keywords in role_map.items():
            if any(kw in jd for kw in keywords):
                return role.title()
        return "Software Engineer"