import random
import sqlite3
import subprocess
import sys
import tempfile
import os
from datetime import datetime, date


class CodingPractice:
    def __init__(self):
        self.db_path = "dossierai.db"
        self._init_db()

    # ------------------------------------------------------------------ #
    #  DB SETUP                                                            #
    # ------------------------------------------------------------------ #
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS coding_progress (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                challenge_id INTEGER,
                solved_date TEXT,
                skill       TEXT,
                difficulty  TEXT,
                passed      INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------ #
    #  DAILY CHALLENGE                                                     #
    # ------------------------------------------------------------------ #
    def get_daily_challenge(self) -> dict:
        """Return a deterministic daily challenge (changes every day)."""
        challenges = [
            {
                "id": 1,
                "title": "Two Sum",
                "difficulty": "Easy",
                "topic": "Arrays & Hashing",
                "time": 20,
                "description": (
                    "Given an array of integers `nums` and an integer `target`, "
                    "return indices of the two numbers such that they add up to `target`.\n\n"
                    "You may assume that each input would have **exactly one solution**, "
                    "and you may not use the same element twice."
                ),
                "examples": [
                    {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]",
                     "explanation": "nums[0] + nums[1] == 9, so return [0, 1]."},
                    {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": ""},
                ],
                "starter_code": (
                    "def two_sum(nums, target):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "Use a hash map to store complement values for O(n) time complexity.",
                "test_cases": [
                    {"input": ([2, 7, 11, 15], 9), "expected": [0, 1]},
                    {"input": ([3, 2, 4], 6), "expected": [1, 2]},
                    {"input": ([3, 3], 6), "expected": [0, 1]},
                ],
            },
            {
                "id": 2,
                "title": "Valid Palindrome",
                "difficulty": "Easy",
                "topic": "Two Pointers",
                "time": 15,
                "description": (
                    "A phrase is a palindrome if, after converting all uppercase letters "
                    "to lowercase and removing all non-alphanumeric characters, it reads "
                    "the same forward and backward.\n\n"
                    "Given a string `s`, return `True` if it is a palindrome, or `False` otherwise."
                ),
                "examples": [
                    {"input": 's = "A man, a plan, a canal: Panama"', "output": "True",
                     "explanation": '"amanaplanacanalpanama" is a palindrome.'},
                    {"input": 's = "race a car"', "output": "False", "explanation": ""},
                ],
                "starter_code": (
                    "def is_palindrome(s):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "Filter the string first, then use two pointers from both ends.",
                "test_cases": [
                    {"input": ("A man, a plan, a canal: Panama",), "expected": True},
                    {"input": ("race a car",), "expected": False},
                    {"input": (" ",), "expected": True},
                ],
            },
            {
                "id": 3,
                "title": "Best Time to Buy and Sell Stock",
                "difficulty": "Easy",
                "topic": "Sliding Window",
                "time": 20,
                "description": (
                    "You are given an array `prices` where `prices[i]` is the price of a "
                    "given stock on the i-th day.\n\n"
                    "You want to maximize your profit by choosing a single day to buy one stock "
                    "and choosing a different day in the future to sell that stock.\n\n"
                    "Return the maximum profit you can achieve. If you cannot achieve any profit, return 0."
                ),
                "examples": [
                    {"input": "prices = [7,1,5,3,6,4]", "output": "5",
                     "explanation": "Buy on day 2 (price=1) and sell on day 5 (price=6), profit = 5."},
                    {"input": "prices = [7,6,4,3,1]", "output": "0",
                     "explanation": "No profitable transaction possible."},
                ],
                "starter_code": (
                    "def max_profit(prices):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "Track the minimum price seen so far and the maximum profit achievable.",
                "test_cases": [
                    {"input": ([7, 1, 5, 3, 6, 4],), "expected": 5},
                    {"input": ([7, 6, 4, 3, 1],), "expected": 0},
                    {"input": ([1, 2],), "expected": 1},
                ],
            },
            {
                "id": 4,
                "title": "Valid Anagram",
                "difficulty": "Easy",
                "topic": "Arrays & Hashing",
                "time": 15,
                "description": (
                    "Given two strings `s` and `t`, return `True` if `t` is an anagram of `s`, "
                    "and `False` otherwise.\n\n"
                    "An anagram is a word or phrase formed by rearranging the letters of a "
                    "different word or phrase, typically using all the original letters exactly once."
                ),
                "examples": [
                    {"input": 's = "anagram", t = "nagaram"', "output": "True", "explanation": ""},
                    {"input": 's = "rat", t = "car"', "output": "False", "explanation": ""},
                ],
                "starter_code": (
                    "def is_anagram(s, t):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "Use a frequency counter (dictionary) for each string and compare.",
                "test_cases": [
                    {"input": ("anagram", "nagaram"), "expected": True},
                    {"input": ("rat", "car"), "expected": False},
                    {"input": ("", ""), "expected": True},
                ],
            },
            {
                "id": 5,
                "title": "Maximum Subarray",
                "difficulty": "Medium",
                "topic": "Dynamic Programming",
                "time": 30,
                "description": (
                    "Given an integer array `nums`, find the subarray with the largest sum, "
                    "and return its sum."
                ),
                "examples": [
                    {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6",
                     "explanation": "The subarray [4,-1,2,1] has the largest sum = 6."},
                    {"input": "nums = [1]", "output": "1", "explanation": ""},
                ],
                "starter_code": (
                    "def max_subarray(nums):\n"
                    "    # Your solution here (Kadane's Algorithm)\n"
                    "    pass\n"
                ),
                "hint": "Kadane's Algorithm: track current sum and reset to 0 when it goes negative.",
                "test_cases": [
                    {"input": ([-2, 1, -3, 4, -1, 2, 1, -5, 4],), "expected": 6},
                    {"input": ([1],), "expected": 1},
                    {"input": ([5, 4, -1, 7, 8],), "expected": 23},
                ],
            },
            {
                "id": 6,
                "title": "Climbing Stairs",
                "difficulty": "Easy",
                "topic": "Dynamic Programming",
                "time": 20,
                "description": (
                    "You are climbing a staircase. It takes `n` steps to reach the top.\n\n"
                    "Each time you can either climb 1 or 2 steps. "
                    "In how many distinct ways can you climb to the top?"
                ),
                "examples": [
                    {"input": "n = 2", "output": "2",
                     "explanation": "Two ways: (1+1) steps or (2) steps."},
                    {"input": "n = 3", "output": "3",
                     "explanation": "Three ways: (1+1+1), (1+2), (2+1)."},
                ],
                "starter_code": (
                    "def climb_stairs(n):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "This follows the Fibonacci sequence pattern. dp[i] = dp[i-1] + dp[i-2].",
                "test_cases": [
                    {"input": (2,), "expected": 2},
                    {"input": (3,), "expected": 3},
                    {"input": (5,), "expected": 8},
                ],
            },
            {
                "id": 7,
                "title": "Binary Search",
                "difficulty": "Easy",
                "topic": "Binary Search",
                "time": 20,
                "description": (
                    "Given an array of integers `nums` sorted in ascending order, "
                    "and an integer `target`, write a function to search `target` in `nums`. "
                    "If `target` exists, return its index. Otherwise, return -1.\n\n"
                    "You must write an algorithm with O(log n) runtime complexity."
                ),
                "examples": [
                    {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4",
                     "explanation": "9 exists in nums and its index is 4."},
                    {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1",
                     "explanation": "2 does not exist in nums so return -1."},
                ],
                "starter_code": (
                    "def search(nums, target):\n"
                    "    # Your solution here\n"
                    "    pass\n"
                ),
                "hint": "Use left and right pointers. Check the mid point each iteration.",
                "test_cases": [
                    {"input": ([-1, 0, 3, 5, 9, 12], 9), "expected": 4},
                    {"input": ([-1, 0, 3, 5, 9, 12], 2), "expected": -1},
                    {"input": ([5], 5), "expected": 0},
                ],
            },
        ]

        # Pick deterministically based on day of year
        day_index = date.today().timetuple().tm_yday % len(challenges)
        challenge = challenges[day_index].copy()
        challenge["completed_today"] = 0
        challenge["streak"] = 0
        challenge["total_solved"] = 0
        return challenge

    # ------------------------------------------------------------------ #
    #  CODE RUNNER                                                         #
    # ------------------------------------------------------------------ #
    def run_code(self, code: str, test_cases: list) -> dict:
        """
        Execute user-submitted code against test_cases in an isolated subprocess.
        Each test_case: {"input": tuple_of_args, "expected": value}
        Returns {"passed": bool, "runtime": int_ms, "error": str}
        """
        # Build a self-contained test harness
        harness = f"""
import time as _time

{code}

_test_cases = {repr(test_cases)}
_start = _time.time()
_passed = 0
_errors = []

# Find the first user-defined function
import types as _types
_fn = None
for _name, _obj in list(globals().items()):
    if isinstance(_obj, _types.FunctionType) and not _name.startswith('_'):
        _fn = _obj
        break

if _fn is None:
    print("ERROR:No function found in your code.")
else:
    for _tc in _test_cases:
        _inp = _tc["input"]
        _exp = _tc["expected"]
        try:
            if isinstance(_inp, tuple):
                _result = _fn(*_inp)
            else:
                _result = _fn(_inp)
            if _result == _exp:
                _passed += 1
            else:
                _errors.append(f"Expected {{_exp}}, got {{_result}}")
        except Exception as _e:
            _errors.append(str(_e))

    _elapsed = int((_time.time() - _start) * 1000)
    _total = len(_test_cases)
    if _passed == _total:
        print(f"PASS:{{_elapsed}}")
    else:
        print(f"FAIL:{{'; '.join(_errors)}}")
"""
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(harness)
                tmp_path = f.name

            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True, text=True, timeout=10
            )
            os.unlink(tmp_path)

            output = result.stdout.strip()
            if output.startswith("PASS:"):
                return {"passed": True, "runtime": int(output.split(":")[1])}
            elif output.startswith("FAIL:"):
                return {"passed": False, "error": output[5:]}
            elif output.startswith("ERROR:"):
                return {"passed": False, "error": output[6:]}
            else:
                stderr = result.stderr.strip()
                return {"passed": False, "error": stderr or "Unknown error"}

        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Time Limit Exceeded (10s)"}
        except Exception as e:
            return {"passed": False, "error": str(e)}

    # ------------------------------------------------------------------ #
    #  SKILL-BASED PROBLEMS                                                #
    # ------------------------------------------------------------------ #
    def get_problems_by_skill(self, skill: str, difficulty: str, platforms: list) -> list:
        """Return curated problem list for a given skill and difficulty."""
        skill_lower = skill.lower()

        problem_bank = {
            "python": {
                "Easy": [
                    {"title": "Fizz Buzz", "difficulty": "Easy", "time": 10,
                     "description": "Print FizzBuzz from 1 to n.", "url": "https://leetcode.com/problems/fizz-buzz/"},
                    {"title": "Reverse String", "difficulty": "Easy", "time": 10,
                     "description": "Reverse an array of characters in-place.", "url": "https://leetcode.com/problems/reverse-string/"},
                ],
                "Medium": [
                    {"title": "Group Anagrams", "difficulty": "Medium", "time": 25,
                     "description": "Group strings that are anagrams of each other.", "url": "https://leetcode.com/problems/group-anagrams/"},
                    {"title": "Spiral Matrix", "difficulty": "Medium", "time": 30,
                     "description": "Return all elements of a matrix in spiral order.", "url": "https://leetcode.com/problems/spiral-matrix/"},
                ],
                "Hard": [
                    {"title": "Median of Two Sorted Arrays", "difficulty": "Hard", "time": 45,
                     "description": "Find the median of two sorted arrays in O(log(m+n)).", "url": "https://leetcode.com/problems/median-of-two-sorted-arrays/"},
                ],
                "Expert": [
                    {"title": "Regular Expression Matching", "difficulty": "Hard", "time": 60,
                     "description": "Implement regex matching with '.' and '*'.", "url": "https://leetcode.com/problems/regular-expression-matching/"},
                ],
            },
            "javascript": {
                "Easy": [
                    {"title": "Create Hello World Function", "difficulty": "Easy", "time": 5,
                     "description": "Return 'Hello World' string.", "url": "https://leetcode.com/problems/create-hello-world-function/"},
                ],
                "Medium": [
                    {"title": "Debounce", "difficulty": "Medium", "time": 30,
                     "description": "Implement a debounce function.", "url": "https://leetcode.com/problems/debounce/"},
                    {"title": "Memoize", "difficulty": "Medium", "time": 25,
                     "description": "Memoize a given function.", "url": "https://leetcode.com/problems/memoize/"},
                ],
                "Hard": [
                    {"title": "Curry", "difficulty": "Hard", "time": 45,
                     "description": "Implement a curry function.", "url": "https://leetcode.com/problems/curry/"},
                ],
                "Expert": [
                    {"title": "Design Cancellable Function", "difficulty": "Hard", "time": 60,
                     "description": "Implement a cancellable async function.", "url": "https://leetcode.com/problems/design-cancellable-function/"},
                ],
            },
            "sql": {
                "Easy": [
                    {"title": "Recyclable and Low Fat Products", "difficulty": "Easy", "time": 10,
                     "description": "Find products that are low fat and recyclable.", "url": "https://leetcode.com/problems/recyclable-and-low-fat-products/"},
                    {"title": "Find Customer Referee", "difficulty": "Easy", "time": 10,
                     "description": "Find customers not referred by customer 2.", "url": "https://leetcode.com/problems/find-customer-referee/"},
                ],
                "Medium": [
                    {"title": "Rising Temperature", "difficulty": "Easy", "time": 20,
                     "description": "Find dates with higher temperature than the previous day.", "url": "https://leetcode.com/problems/rising-temperature/"},
                    {"title": "Department Highest Salary", "difficulty": "Medium", "time": 30,
                     "description": "Find employees with the highest salary in each department.", "url": "https://leetcode.com/problems/department-highest-salary/"},
                ],
                "Hard": [
                    {"title": "Department Top Three Salaries", "difficulty": "Hard", "time": 45,
                     "description": "Find employees who are high earners in each department.", "url": "https://leetcode.com/problems/department-top-three-salaries/"},
                ],
                "Expert": [
                    {"title": "Trips and Users", "difficulty": "Hard", "time": 60,
                     "description": "Compute cancellation rates of unbanned users.", "url": "https://leetcode.com/problems/trips-and-users/"},
                ],
            },
        }

        # Match skill to a key in the bank
        matched_key = None
        for key in problem_bank:
            if key in skill_lower or skill_lower in key:
                matched_key = key
                break

        if matched_key is None:
            # Generic fallback
            return [
                {"title": f"{skill} Practice Problem", "difficulty": difficulty, "time": 30,
                 "description": f"Practice your {skill} skills with this challenge.",
                 "url": f"https://leetcode.com/problemset/?search={skill.replace(' ', '+')}"},
                {"title": f"Advanced {skill} Challenge", "difficulty": difficulty, "time": 45,
                 "description": f"Level up your {skill} knowledge.",
                 "url": f"https://www.hackerrank.com/domains/algorithms"},
            ]

        problems = problem_bank[matched_key].get(difficulty, problem_bank[matched_key].get("Medium", []))
        return problems

    # ------------------------------------------------------------------ #
    #  RECOMMENDATIONS                                                     #
    # ------------------------------------------------------------------ #
    def get_recommendations(self, resume_data: dict) -> list:
        """Return topic recommendations based on resume skills."""
        if not resume_data:
            return []

        skills = [s.lower() for s in resume_data.get("skills", [])]
        recommendations = []

        skill_topic_map = {
            "python": ["Dynamic Programming", "Graph Algorithms", "String Manipulation"],
            "java": ["Object-Oriented Design", "Concurrency", "Binary Trees"],
            "javascript": ["Async Programming", "Closures & Scope", "DOM Algorithms"],
            "sql": ["Query Optimization", "Window Functions", "Joins"],
            "machine learning": ["Statistics Problems", "Matrix Operations", "Probability"],
            "react": ["State Management Patterns", "Component Design", "Hooks"],
            "c++": ["Memory Management", "STL Algorithms", "Bit Manipulation"],
        }

        for skill in skills:
            for key, topics in skill_topic_map.items():
                if key in skill:
                    recommendations.extend(topics)

        # Deduplicate and limit
        seen = set()
        unique = []
        for r in recommendations:
            if r not in seen:
                seen.add(r)
                unique.append(r)

        if not unique:
            unique = ["Arrays & Hashing", "Two Pointers", "Sliding Window", "Binary Search"]

        return unique[:6]

    # ------------------------------------------------------------------ #
    #  LEARNING RESOURCES                                                  #
    # ------------------------------------------------------------------ #
    def get_learning_resources(self, skill: str) -> dict:
        """Return learning resource URLs for a given skill."""
        skill_lower = skill.lower().replace(" ", "-")

        resources = {
            "Documentation": f"https://devdocs.io/",
            "LeetCode": f"https://leetcode.com/problemset/?search={skill.replace(' ', '+')}",
            "HackerRank": f"https://www.hackerrank.com/domains/tutorials/10-days-of-javascript",
            "freeCodeCamp": f"https://www.freecodecamp.org/learn/",
            "YouTube": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial",
            "GeeksforGeeks": f"https://www.geeksforgeeks.org/{skill_lower}/",
        }

        # Override with well-known direct links for common skills
        overrides = {
            "python": {
                "Documentation": "https://docs.python.org/3/",
                "Tutorial": "https://docs.python.org/3/tutorial/",
                "LeetCode": "https://leetcode.com/problemset/?topicSlugs=array",
            },
            "javascript": {
                "Documentation": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                "freeCodeCamp": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            },
            "sql": {
                "Documentation": "https://www.w3schools.com/sql/",
                "Practice": "https://sqlzoo.net/",
                "LeetCode": "https://leetcode.com/problemset/database/",
            },
            "react": {
                "Documentation": "https://react.dev/",
                "Tutorial": "https://react.dev/learn",
            },
            "machine learning": {
                "Coursera": "https://www.coursera.org/learn/machine-learning",
                "Fast.ai": "https://www.fast.ai/",
                "Kaggle": "https://www.kaggle.com/learn",
            },
            "docker": {
                "Documentation": "https://docs.docker.com/",
                "Play with Docker": "https://labs.play-with-docker.com/",
            },
        }

        for key, override in overrides.items():
            if key in skill.lower():
                resources.update(override)
                break

        return resources

    # ------------------------------------------------------------------ #
    #  PROGRESS TRACKING                                                   #
    # ------------------------------------------------------------------ #
    def mark_complete(self, user_id: int, challenge_id: int):
        """Record a completed challenge for the user."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        today = date.today().isoformat()
        # Avoid duplicate entries for same day + challenge
        c.execute(
            "SELECT id FROM coding_progress WHERE user_id=? AND challenge_id=? AND solved_date=?",
            (user_id, challenge_id, today)
        )
        if not c.fetchone():
            c.execute(
                "INSERT INTO coding_progress (user_id, challenge_id, solved_date, passed) VALUES (?,?,?,1)",
                (user_id, challenge_id, today)
            )
            conn.commit()
        conn.close()

    def get_user_progress(self, user_id: int) -> dict:
        """Return aggregate progress stats for the user."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Total solved
        c.execute(
            "SELECT COUNT(*) FROM coding_progress WHERE user_id=? AND passed=1",
            (user_id,)
        )
        total_solved = c.fetchone()[0]

        # Success rate
        c.execute("SELECT COUNT(*) FROM coding_progress WHERE user_id=?", (user_id,))
        total_attempts = c.fetchone()[0]
        success_rate = int((total_solved / total_attempts * 100) if total_attempts else 0)

        # Streak: count consecutive days ending today
        c.execute(
            "SELECT DISTINCT solved_date FROM coding_progress WHERE user_id=? AND passed=1 ORDER BY solved_date DESC",
            (user_id,)
        )
        dates = [row[0] for row in c.fetchall()]
        streak = self._calculate_streak(dates)

        # Rank (by total solved, descending)
        c.execute(
            "SELECT user_id, COUNT(*) as cnt FROM coding_progress WHERE passed=1 GROUP BY user_id ORDER BY cnt DESC"
        )
        rows = c.fetchall()
        rank = next((i + 1 for i, row in enumerate(rows) if row[0] == user_id), len(rows) + 1)

        # History for chart
        c.execute(
            """SELECT solved_date, COUNT(*) as cnt
               FROM coding_progress WHERE user_id=? AND passed=1
               GROUP BY solved_date ORDER BY solved_date""",
            (user_id,)
        )
        history_rows = c.fetchall()
        history = [{"date": row[0], "solved": row[1]} for row in history_rows]

        # Skill breakdown
        c.execute(
            """SELECT skill, COUNT(*) as cnt
               FROM coding_progress WHERE user_id=? AND skill IS NOT NULL
               GROUP BY skill""",
            (user_id,)
        )
        skill_rows = c.fetchall()
        skill_breakdown = [{"skill": row[0], "count": row[1]} for row in skill_rows]

        conn.close()

        return {
            "total_solved": total_solved,
            "success_rate": success_rate,
            "streak": streak,
            "rank": rank,
            "history": history,
            "skill_breakdown": skill_breakdown,
        }

    # ------------------------------------------------------------------ #
    #  HELPERS                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _calculate_streak(dates: list) -> int:
        """Calculate consecutive day streak from a sorted-desc list of date strings."""
        if not dates:
            return 0

        today = date.today()
        streak = 0
        current = today

        for d_str in dates:
            try:
                d = date.fromisoformat(d_str)
            except ValueError:
                continue
            if d == current:
                streak += 1
                from datetime import timedelta
                current -= timedelta(days=1)
            else:
                break

        return streak