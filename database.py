import sqlite3
import hashlib
import json
import os
from datetime import datetime, date
from pathlib import Path


DB_PATH = "dossierai.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class DatabaseManager:
    def __init__(self):
        self._init_db()

    # ------------------------------------------------------------------ #
    #  SCHEMA                                                              #
    # ------------------------------------------------------------------ #
    def _init_db(self):
        with get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT    UNIQUE NOT NULL,
                    email    TEXT    UNIQUE NOT NULL,
                    password TEXT    NOT NULL,
                    name     TEXT    DEFAULT '',
                    phone    TEXT    DEFAULT '',
                    linkedin TEXT    DEFAULT '',
                    github   TEXT    DEFAULT '',
                    created_at TEXT  DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS resume_analyses (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    filename   TEXT    NOT NULL,
                    score      REAL    NOT NULL,
                    resume_data TEXT   DEFAULT '{}',
                    date       TEXT    DEFAULT (datetime('now')),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS coding_progress (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id      INTEGER NOT NULL,
                    challenge_id INTEGER NOT NULL,
                    solved_at    TEXT    DEFAULT (date('now')),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS daily_streaks (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER UNIQUE NOT NULL,
                    streak     INTEGER DEFAULT 0,
                    last_date  TEXT    DEFAULT '',
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
            """)
            conn.commit()

    # ------------------------------------------------------------------ #
    #  HELPERS                                                             #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # ------------------------------------------------------------------ #
    #  AUTH                                                                #
    # ------------------------------------------------------------------ #
    def create_user(self, username: str, email: str, password: str) -> bool:
        try:
            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username.strip(), email.strip().lower(), self._hash(password))
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username: str, password: str):
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username.strip(), self._hash(password))
            ).fetchone()
        return dict(row) if row else None

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE id=? AND password=?",
                (user_id, self._hash(current_password))
            ).fetchone()
            if not row:
                return False
            conn.execute(
                "UPDATE users SET password=? WHERE id=?",
                (self._hash(new_password), user_id)
            )
            conn.commit()
        return True

    # ------------------------------------------------------------------ #
    #  PROFILE                                                             #
    # ------------------------------------------------------------------ #
    def get_user_data(self, user_id: int) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else {}

    def update_profile(self, user_id: int, data: dict):
        with get_connection() as conn:
            conn.execute(
                """UPDATE users
                   SET name=?, email=?, phone=?, linkedin=?, github=?
                   WHERE id=?""",
                (data.get('name', ''), data.get('email', ''),
                 data.get('phone', ''), data.get('linkedin', ''),
                 data.get('github', ''), user_id)
            )
            conn.commit()

    # ------------------------------------------------------------------ #
    #  ANALYSES                                                            #
    # ------------------------------------------------------------------ #
    def save_analysis(self, user_id: int, filename: str, score: float, resume_data: dict):
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO resume_analyses (user_id, filename, score, resume_data) VALUES (?,?,?,?)",
                (user_id, filename, score, json.dumps(resume_data, default=str))
            )
            conn.commit()

    def get_user_history(self, user_id: int) -> list:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM resume_analyses WHERE user_id=? ORDER BY date DESC LIMIT 50",
                (user_id,)
            ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                rd = json.loads(d.get('resume_data', '{}'))
                d['skills'] = rd.get('skills', [])
            except Exception:
                d['skills'] = []
            result.append(d)
        return result

    def get_user_stats(self, user_id: int) -> dict:
        with get_connection() as conn:
            row = conn.execute(
                """SELECT COUNT(*) as total_analyses,
                          COALESCE(AVG(score), 0) as avg_score
                   FROM resume_analyses WHERE user_id=?""",
                (user_id,)
            ).fetchone()
            lb = self.get_leaderboard()
        rank = next((i + 1 for i, u in enumerate(lb) if u.get('user_id') == user_id), 'N/A')
        return {
            'total_analyses': row['total_analyses'],
            'avg_score': round(row['avg_score'], 1),
            'rank': rank
        }

    # ------------------------------------------------------------------ #
    #  LEADERBOARD                                                         #
    # ------------------------------------------------------------------ #
    def get_leaderboard(self) -> list:
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT u.id as user_id, u.username,
                          COUNT(a.id) as total_analyses,
                          COALESCE(AVG(a.score), 0) as avg_score
                   FROM users u
                   LEFT JOIN resume_analyses a ON u.id = a.user_id
                   GROUP BY u.id
                   HAVING total_analyses > 0
                   ORDER BY avg_score DESC
                   LIMIT 20"""
            ).fetchall()
        result = []
        for i, r in enumerate(rows):
            d = dict(r)
            d['rank'] = i + 1
            d['avg_score'] = round(d['avg_score'], 1)
            result.append(d)
        return result

    # ------------------------------------------------------------------ #
    #  CODING PROGRESS                                                     #
    # ------------------------------------------------------------------ #
    def mark_challenge_complete(self, user_id: int, challenge_id: int):
        today = date.today().isoformat()
        with get_connection() as conn:
            # Avoid duplicate for same day
            exists = conn.execute(
                "SELECT id FROM coding_progress WHERE user_id=? AND challenge_id=? AND solved_at=?",
                (user_id, challenge_id, today)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO coding_progress (user_id, challenge_id, solved_at) VALUES (?,?,?)",
                    (user_id, challenge_id, today)
                )
                conn.commit()
            # Update streak
            streak_row = conn.execute(
                "SELECT streak, last_date FROM daily_streaks WHERE user_id=?", (user_id,)
            ).fetchone()
            if streak_row:
                last = streak_row['last_date']
                streak = streak_row['streak']
                if last == today:
                    pass  # already updated today
                elif (datetime.strptime(today, '%Y-%m-%d') -
                      datetime.strptime(last, '%Y-%m-%d')).days == 1:
                    streak += 1
                    conn.execute(
                        "UPDATE daily_streaks SET streak=?, last_date=? WHERE user_id=?",
                        (streak, today, user_id)
                    )
                else:
                    conn.execute(
                        "UPDATE daily_streaks SET streak=1, last_date=? WHERE user_id=?",
                        (today, user_id)
                    )
            else:
                conn.execute(
                    "INSERT INTO daily_streaks (user_id, streak, last_date) VALUES (?,1,?)",
                    (user_id, today)
                )
            conn.commit()

    def get_coding_progress(self, user_id: int) -> dict:
        with get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(*) as c FROM coding_progress WHERE user_id=?", (user_id,)
            ).fetchone()['c']
            streak_row = conn.execute(
                "SELECT streak FROM daily_streaks WHERE user_id=?", (user_id,)
            ).fetchone()
            history_rows = conn.execute(
                """SELECT solved_at as date, COUNT(*) as solved
                   FROM coding_progress WHERE user_id=?
                   GROUP BY solved_at ORDER BY solved_at""",
                (user_id,)
            ).fetchall()
            lb = self.get_leaderboard()
        rank = next((i + 1 for i, u in enumerate(lb) if u.get('user_id') == user_id), 0)
        solved_today = 0
        today = date.today().isoformat()
        history = [dict(r) for r in history_rows]
        for h in history:
            if h['date'] == today:
                solved_today = h['solved']
        return {
            'total_solved': total,
            'streak': streak_row['streak'] if streak_row else 0,
            'success_rate': min(100, total * 5),
            'rank': rank,
            'history': history,
            'solved_today': solved_today,
            'skill_breakdown': []
        }

    # ------------------------------------------------------------------ #
    #  DATA EXPORT / DELETE                                                #
    # ------------------------------------------------------------------ #
    def export_user_data(self, user_id: int) -> dict:
        user = self.get_user_data(user_id)
        history = self.get_user_history(user_id)
        progress = self.get_coding_progress(user_id)
        # Remove password from export
        user.pop('password', None)
        return {
            'profile': user,
            'resume_history': history,
            'coding_progress': progress,
            'exported_at': datetime.now().isoformat()
        }

    def clear_history(self, user_id: int):
        with get_connection() as conn:
            conn.execute("DELETE FROM resume_analyses WHERE user_id=?", (user_id,))
            conn.execute("DELETE FROM coding_progress WHERE user_id=?", (user_id,))
            conn.execute("DELETE FROM daily_streaks WHERE user_id=?", (user_id,))
            conn.commit()

    def delete_account(self, user_id: int):
        self.clear_history(user_id)
        with get_connection() as conn:
            conn.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()