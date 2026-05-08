"""
Builders for Chart.js-ready data.

Each method returns a plain Python dict (JSON-serializable) that templates
hand to Chart.js. No image generation here — Chart.js renders crisp,
interactive vector charts in the browser.
"""

PALETTE = {
    'indigo':  '#6366F1',
    'pink':    '#EC4899',
    'emerald': '#10B981',
    'amber':   '#F59E0B',
    'red':     '#EF4444',
    'cyan':    '#06B6D4',
    'violet':  '#8B5CF6',
    'lime':    '#84CC16',
    'rose':    '#F43F5E',
    'teal':    '#14B8A6',
}
SEQUENCE = [
    PALETTE['indigo'], PALETTE['pink'], PALETTE['emerald'], PALETTE['amber'],
    PALETTE['cyan'], PALETTE['violet'], PALETTE['lime'], PALETTE['rose'],
    PALETTE['teal'], PALETTE['red'],
]
# Worst → best
SCORE_BAND = ['#EF4444', '#F59E0B', '#FACC15', '#84CC16', '#10B981']


def _band_color(pct):
    return SCORE_BAND[min(int(pct // 20), 4)]


class GraphGenerator:
    """Build Chart.js data dicts for the various analytics views."""

    @staticmethod
    def generate_attempt_result_graph(attempt):
        """Donut + bar combo data for a single attempt."""
        correct = int(attempt.score or 0)
        total = int(attempt.total_questions or 0)
        wrong = total - correct
        pct = (correct / total * 100) if total else 0
        return {
            'kind': 'attempt_result',
            'quiz_title': attempt.quiz.title if attempt.quiz else 'Quiz',
            'correct': correct,
            'wrong': wrong,
            'total': total,
            'percentage': round(pct, 1),
        }

    @staticmethod
    def generate_user_analysis_graph(user):
        """Performance trend over recent attempts."""
        attempts = sorted(
            [a for a in user.attempts if a.completed_at],
            key=lambda x: x.completed_at,
        )[-12:]
        labels = [a.completed_at.strftime('%b %d') for a in attempts]
        data = [round(a.percentage, 1) for a in attempts]
        point_colors = [_band_color(p) for p in data]
        return {
            'kind': 'performance_trend',
            'labels': labels,
            'data': data,
            'point_colors': point_colors,
        }

    @staticmethod
    def generate_category_performance_graph(user):
        """Average score per quiz."""
        per_quiz = {}
        for a in user.attempts:
            if a.completed_at and a.quiz:
                per_quiz.setdefault(a.quiz.title, []).append(a.percentage)
        items = sorted(
            ((t, sum(v) / len(v)) for t, v in per_quiz.items()),
            key=lambda kv: kv[1],
            reverse=True,
        )[:12]
        labels = [t if len(t) <= 32 else t[:29] + '…' for t, _ in items]
        data = [round(s, 1) for _, s in items]
        bar_colors = [_band_color(s) for s in data]
        return {
            'kind': 'per_quiz',
            'labels': labels,
            'data': data,
            'colors': bar_colors,
        }

    @staticmethod
    def generate_ranking_distribution_graph(top_users):
        """Top users for the leaderboard chart."""
        users = [u for u in top_users[:15] if u.stats]
        users.sort(key=lambda u: u.stats.total_points, reverse=True)
        labels = [u.username for u in users]
        data = [u.stats.total_points for u in users]
        # Hot → cool gradient (top is brightest)
        n = max(len(users), 1)
        warm = ['#F59E0B', '#F97316', '#EF4444', '#EC4899', '#8B5CF6', '#6366F1']
        colors = [warm[min(i, len(warm) - 1)] if i < 6 else PALETTE['indigo'] for i in range(n)]
        return {
            'kind': 'ranking',
            'labels': labels,
            'data': data,
            'colors': colors,
        }

    @staticmethod
    def generate_statistics_summary(user):
        """Key stats + accuracy donut + score-distribution bar + pass/fail pie."""
        if not user.stats:
            return None
        stats = user.stats
        completed = [a for a in user.attempts if a.completed_at]
        bands = [0, 0, 0, 0, 0]
        for a in completed:
            p = a.percentage
            if p < 25: bands[0] += 1
            elif p < 50: bands[1] += 1
            elif p < 75: bands[2] += 1
            elif p < 90: bands[3] += 1
            else: bands[4] += 1
        passed = sum(1 for a in completed if a.percentage >= 70)
        below = len(completed) - passed
        return {
            'kind': 'stats_summary',
            'username': user.username,
            'cards': {
                'quizzes': stats.total_quizzes_taken,
                'points':  stats.total_points,
                'avg':     round(stats.avg_score, 1),
                'rank':    stats.rank or 0,
                'best':    stats.best_score,
            },
            'accuracy': {
                'correct': stats.total_correct_answers or 0,
                'wrong':   stats.total_wrong_answers or 0,
            },
            'distribution': {
                'labels': ['0–25%', '25–50%', '50–75%', '75–90%', '90–100%'],
                'data':   bands,
                'colors': SCORE_BAND,
            },
            'pass_split': {
                'passed': passed,
                'below':  below,
            },
        }
