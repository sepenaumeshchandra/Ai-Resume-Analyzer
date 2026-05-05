import random
import re

HR_QUESTIONS = [
    {
        "question": "Tell me about yourself.",
        "tip": "Use the Present–Past–Future structure: current role → background → why this company.",
        "keywords": ["experience", "skills", "background", "role", "team"],
    },
    {
        "question": "What is your greatest strength?",
        "tip": "Pick a strength relevant to the role and back it with a specific example.",
        "keywords": ["strength", "good at", "excel", "best", "proud"],
    },
    {
        "question": "What is your greatest weakness?",
        "tip": "Name a real weakness, but show what you're doing to improve it.",
        "keywords": ["improve", "learning", "working on", "challenge", "overcome"],
    },
    {
        "question": "Where do you see yourself in 5 years?",
        "tip": "Show ambition aligned with growth at this company — avoid generic answers.",
        "keywords": ["grow", "lead", "contribute", "learn", "goal"],
    },
    {
        "question": "Why do you want to work here?",
        "tip": "Research the company. Mention specific products, values, or mission.",
        "keywords": ["company", "mission", "product", "culture", "values"],
    },
    {
        "question": "Describe a time you handled a conflict with a teammate.",
        "tip": "Use the STAR method (Situation, Task, Action, Result). Focus on resolution.",
        "keywords": ["conflict", "disagree", "resolve", "communicate", "solution"],
    },
    {
        "question": "Tell me about a project you're most proud of.",
        "tip": "Pick a project with measurable impact. Explain your specific contribution.",
        "keywords": ["project", "built", "impact", "result", "team", "challenge"],
    },
    {
        "question": "How do you handle tight deadlines and pressure?",
        "tip": "Give a concrete example. Mention prioritisation and communication.",
        "keywords": ["deadline", "priorit", "manage", "deliver", "stress"],
    },
    {
        "question": "Why are you leaving your current job?",
        "tip": "Stay positive. Focus on growth opportunities, not complaints.",
        "keywords": ["growth", "learn", "opportunity", "challenge", "new"],
    },
    {
        "question": "What motivates you?",
        "tip": "Connect your motivators to the role — problem-solving, impact, mastery.",
        "keywords": ["challenge", "learn", "impact", "create", "solve"],
    },
]

TECH_QUESTIONS = {
    "python": [
        {
            "question": "What is the difference between a list and a tuple in Python?",
            "difficulty": "Beginner",
            "expected": ("Lists are mutable (can be changed); tuples are immutable. "
                         "Tuples are faster and can be used as dictionary keys."),
        },
        {
            "question": "Explain Python's GIL (Global Interpreter Lock).",
            "difficulty": "Intermediate",
            "expected": ("The GIL is a mutex that allows only one thread to execute Python bytecode at a time. "
                         "It simplifies memory management but limits CPU-bound multi-threading. "
                         "Use multiprocessing or async for parallelism."),
        },
        {
            "question": "Implement a decorator that logs the execution time of any function.",
            "difficulty": "Advanced",
            "code": (
                "import time\n"
                "def timer(func):\n"
                "    def wrapper(*args, **kwargs):\n"
                "        start = time.time()\n"
                "        result = func(*args, **kwargs)\n"
                "        print(f'{func.__name__} took {time.time()-start:.4f}s')\n"
                "        return result\n"
                "    return wrapper"
            ),
            "language": "python",
            "expected": "Use functools.wraps to preserve metadata. Track time.time() before and after the call.",
        },
        {
            "question": "What are Python generators and when would you use them?",
            "difficulty": "Intermediate",
            "expected": ("Generators are functions that yield values one at a time using 'yield', "
                         "enabling lazy evaluation. Use them for large datasets or infinite sequences "
                         "to save memory."),
        },
    ],
    "javascript": [
        {
            "question": "What is the difference between == and === in JavaScript?",
            "difficulty": "Beginner",
            "expected": "== compares values with type coercion; === compares value AND type without coercion. Always prefer ===.",
        },
        {
            "question": "Explain event bubbling and event capturing.",
            "difficulty": "Intermediate",
            "expected": ("Bubbling: event propagates from child → parent. "
                         "Capturing: event propagates from parent → child. "
                         "Use addEventListener's third argument (true = capture) to control this."),
        },
        {
            "question": "What is the event loop and how does async/await work?",
            "difficulty": "Advanced",
            "expected": ("The event loop processes the call stack and callback queues. "
                         "async/await is syntactic sugar over Promises; await pauses the async function "
                         "until the Promise resolves, without blocking the main thread."),
        },
    ],
    "react": [
        {
            "question": "What is the difference between state and props?",
            "difficulty": "Beginner",
            "expected": ("Props are read-only data passed from parent to child. "
                         "State is mutable data managed within a component. "
                         "State changes trigger re-renders."),
        },
        {
            "question": "Explain the useEffect hook and its dependency array.",
            "difficulty": "Intermediate",
            "expected": ("useEffect runs side effects after render. The dependency array controls when it runs: "
                         "empty [] = once on mount; [x] = when x changes; no array = every render."),
        },
        {
            "question": "How does React reconciliation work?",
            "difficulty": "Advanced",
            "expected": ("React compares the new virtual DOM with the previous one (diffing algorithm). "
                         "It updates only the changed nodes in the real DOM. Keys help identify list items "
                         "and avoid unnecessary re-renders."),
        },
    ],
    "sql": [
        {
            "question": "What is the difference between INNER JOIN and LEFT JOIN?",
            "difficulty": "Beginner",
            "expected": ("INNER JOIN returns rows where there is a match in both tables. "
                         "LEFT JOIN returns all rows from the left table even if there's no match in the right table."),
        },
        {
            "question": "Explain indexing and when you would use a composite index.",
            "difficulty": "Intermediate",
            "expected": ("Indexes speed up SELECT queries by creating a quick lookup structure. "
                         "Composite indexes cover multiple columns and are effective when queries filter by those columns in order."),
        },
    ],
    "machine learning": [
        {
            "question": "What is the bias-variance tradeoff?",
            "difficulty": "Intermediate",
            "expected": ("High bias = underfitting (model too simple). "
                         "High variance = overfitting (model too complex). "
                         "Good models balance both using regularization, cross-validation, and appropriate complexity."),
        },
        {
            "question": "Explain gradient descent and its variants.",
            "difficulty": "Advanced",
            "expected": ("Gradient descent minimizes the loss function by moving in the direction of the negative gradient. "
                         "Variants: SGD (one sample), Mini-batch (small batches), Adam (adaptive learning rates)."),
        },
    ],
}

DEFAULT_TECH_QUESTIONS = [
    {
        "question": "What is Big O notation and why is it important?",
        "difficulty": "Beginner",
        "expected": ("Big O describes the worst-case time or space complexity of an algorithm as input size grows. "
                     "It helps compare algorithms and choose the most efficient one for the problem."),
    },
    {
        "question": "Explain the difference between stack and heap memory.",
        "difficulty": "Intermediate",
        "expected": ("Stack: stores local variables and function calls (automatic management, LIFO). "
                     "Heap: stores dynamically allocated objects (manual or garbage-collected). "
                     "Stack is faster; heap is larger but slower."),
    },
    {
        "question": "What design patterns have you used and when?",
        "difficulty": "Advanced",
        "expected": ("Common patterns: Singleton (one instance), Factory (object creation), "
                     "Observer (event systems), Strategy (interchangeable algorithms), "
                     "Decorator (add behaviour). Explain a real example from your code."),
    },
]


class InterviewGenerator:
    # ------------------------------------------------------------------ #
    #  HR                                                                  #
    # ------------------------------------------------------------------ #
    def generate_hr_questions(self, resume_data: dict) -> list:
        questions = list(HR_QUESTIONS)
        random.shuffle(questions)
        return questions[:6]

    def analyze_hr_answer(self, answer: str, question: dict) -> dict:
        if not answer or not answer.strip():
            return {
                'score':      0,
                'tip':        'You did not provide an answer.',
                'suggestion': 'Try to answer using the STAR method or at least 2–3 sentences.',
            }
        answer_lower = answer.lower()
        keywords = question.get('keywords', [])
        hits = sum(1 for kw in keywords if kw in answer_lower)
        word_count = len(answer.split())

        # Scoring
        score = 40  # base
        score += min(hits * 10, 30)   # keyword coverage
        if word_count >= 50:
            score += 15
        elif word_count >= 20:
            score += 8
        if word_count > 200:
            score -= 5   # too verbose
        score = max(0, min(score, 100))

        tip = question.get('tip', 'Use the STAR method for best results.')
        suggestion = (
            f"Consider mentioning: {', '.join(keywords[:3])}. "
            "Structure your answer with a specific example."
        )
        return {'score': score, 'tip': tip, 'suggestion': suggestion}

    # ------------------------------------------------------------------ #
    #  TECHNICAL                                                           #
    # ------------------------------------------------------------------ #
    def generate_technical_questions(self, skill: str, difficulty: str,
                                     resume_data: dict) -> list:
        skill_lower = skill.lower()
        pool = TECH_QUESTIONS.get(skill_lower, DEFAULT_TECH_QUESTIONS)
        
        difficulty_order = ["Beginner", "Intermediate", "Advanced", "Expert"]
        diff_idx = difficulty_order.index(difficulty) if difficulty in difficulty_order else 1
        
        # Filter by difficulty if possible, else return all
        filtered = [q for q in pool if q.get('difficulty', 'Intermediate') == difficulty]
        if not filtered:
            filtered = pool

        random.shuffle(filtered)
        return filtered[:4]

    def evaluate_technical_answer(self, answer: str, question: dict) -> dict:
        if not answer or not answer.strip():
            return {
                'correct':     False,
                'hint':        'Please provide an answer before checking.',
                'explanation': question.get('expected', ''),
            }
        answer_lower = answer.lower()
        expected = question.get('expected', '').lower()

        # Extract key terms from expected answer
        expected_terms = set(re.findall(r'\b[a-z]{4,}\b', expected))
        answer_terms   = set(re.findall(r'\b[a-z]{4,}\b', answer_lower))

        overlap = expected_terms & answer_terms
        coverage = len(overlap) / max(len(expected_terms), 1)
        correct = coverage >= 0.35

        return {
            'correct':     correct,
            'hint':        question.get('expected', 'Review the expected answer.'),
            'explanation': (
                f"Your answer covered ~{round(coverage*100)}% of the key concepts. "
                + ("Great job!" if correct else "Review the suggested answer above.")
            ),
        }