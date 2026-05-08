from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Account settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    stats = db.relationship('UserStats', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    articles_bookmarked = db.relationship('Article', secondary='user_article_bookmark', backref='bookmarked_by')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Quiz(db.Model):
    """Quiz model representing a quiz/poll"""
    __tablename__ = 'quiz'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    
    # Quiz settings
    time_limit_minutes = db.Column(db.Integer, nullable=True)  # Time limit in minutes, None for unlimited
    enable_music = db.Column(db.Boolean, default=True)  # Enable background music during quiz
    music_url = db.Column(db.String(500), nullable=True)  # URL to background music file
    
    # Status fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time_limit_minutes': self.time_limit_minutes,
            'enable_music': self.enable_music,
            'music_url': self.music_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_published': self.is_published,
            'question_count': len(self.questions)
        }

class Question(db.Model):
    """Question model"""
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false
    order = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), nullable=True)  # URL to question image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('QuizResponse', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_correct=False):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'order': self.order,
            'image_url': self.image_url,
            'answers': [answer.to_dict(include_correct=include_correct) for answer in self.answers]
        }

class Answer(db.Model):
    """Answer model"""
    __tablename__ = 'answer'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500), nullable=True)  # URL to answer image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('QuizResponse', backref='answer', lazy=True)
    
    def to_dict(self, include_correct=False):
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'order': self.order,
            'image_url': self.image_url
        }
        if include_correct:
            data['is_correct'] = self.is_correct
        return data

class QuizAttempt(db.Model):
    """User quiz attempt/session"""
    __tablename__ = 'quiz_attempt'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)  # For time limit feature
    
    # Relationships
    responses = db.relationship('QuizResponse', backref='attempt', lazy=True, cascade='all, delete-orphan')

    @property
    def percentage(self):
        if not self.total_questions:
            return 0.0
        return round(self.score / self.total_questions * 100, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown',
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score,
            'total_questions': self.total_questions,
            'time_spent_seconds': self.time_spent_seconds,
            'percentage': self.percentage
        }

class QuizResponse(db.Model):
    """User response to a specific question"""
    __tablename__ = 'quiz_response'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== RANKING AND STATISTICS ====================

class UserStats(db.Model):
    """User statistics and ranking"""
    __tablename__ = 'user_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True, index=True)
    
    # Points and ranking
    total_points = db.Column(db.Integer, default=0)  # Points from all quizzes
    total_quizzes_taken = db.Column(db.Integer, default=0)
    total_correct_answers = db.Column(db.Integer, default=0)
    total_wrong_answers = db.Column(db.Integer, default=0)
    
    # Rankings
    rank = db.Column(db.Integer, default=0)  # Current rank among all users
    avg_score = db.Column(db.Float, default=0.0)  # Average score across all quizzes
    best_score = db.Column(db.Integer, default=0)  # Highest score achieved
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_points': self.total_points,
            'total_quizzes_taken': self.total_quizzes_taken,
            'total_correct_answers': self.total_correct_answers,
            'total_wrong_answers': self.total_wrong_answers,
            'rank': self.rank,
            'avg_score': round(self.avg_score, 2),
            'best_score': self.best_score
        }


# ==================== EDUCATIONAL ARTICLES ====================

# Association table for user bookmarks
user_article_bookmark = db.Table(
    'user_article_bookmark',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('bookmarked_at', db.DateTime, default=datetime.utcnow)
)


class Article(db.Model):
    """Educational articles for learning"""
    __tablename__ = 'article'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False, index=True)
    slug = db.Column(db.String(300), unique=True, nullable=False)  # URL-friendly slug
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)  # Main article content
    category = db.Column(db.String(100), nullable=True, index=True)  # Article category
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    author = db.Column(db.String(200), nullable=True)
    thumbnail_url = db.Column(db.String(500), nullable=True)
    
    # Reading metadata
    read_time_minutes = db.Column(db.Integer, default=5)  # Estimated read time
    views = db.Column(db.Integer, default=0)
    
    # Status and timestamps
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookmarks_count = db.Column(db.Integer, default=0)  # Number of bookmarks
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'author': self.author,
            'thumbnail_url': self.thumbnail_url,
            'read_time_minutes': self.read_time_minutes,
            'views': self.views,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'bookmarks_count': self.bookmarks_count
        }
        if include_content:
            data['content'] = self.content
        return data
