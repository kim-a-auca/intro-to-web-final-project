from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Quiz, Question, Answer, QuizAttempt, QuizResponse, User, UserStats, Article, user_article_bookmark
from app.file_handler import handle_quiz_upload, save_image_file
from app.graph_service import GraphGenerator
from datetime import datetime
import json
import re

quiz_bp = Blueprint('quiz', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================== AUTHENTICATION VIEWS ====================

@quiz_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('quiz.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        password_confirm = data.get('password_confirm', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        if password != password_confirm:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        
        # Create user statistics
        stats = UserStats(user_id=user.id)
        db.session.add(stats)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Registration successful! Please log in.'}), 201
    
    return render_template('register.html')

@quiz_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('quiz.index'))
    
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account is disabled'}), 403
        
        login_user(user, remember=data.get('remember', False))
        return jsonify({'success': True, 'message': 'Login successful!'}), 200
    
    return render_template('login.html')

@quiz_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('quiz.index'))

@quiz_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.completed_at.desc()).all()
    total_quizzes_taken = len(user_attempts)
    avg_score = 0
    if user_attempts:
        avg_score = sum([a.percentage for a in user_attempts]) / len(user_attempts)
    
    return render_template('profile.html', 
                          user_attempts=user_attempts,
                          total_quizzes_taken=total_quizzes_taken,
                          avg_score=round(avg_score, 2))

# ==================== WEB VIEWS ====================

@quiz_bp.route('/')
def index():
    """Home page - list all quizzes"""
    quizzes = Quiz.query.all()
    return render_template('index.html', quizzes=quizzes)

@quiz_bp.route('/quiz/new', methods=['GET', 'POST'])
@login_required
def create_quiz():
    """Create a new quiz"""
    if request.method == 'POST':
        data = request.get_json()
        time_limit = data.get('time_limit_minutes')
        if time_limit in ('', 0):
            time_limit = None
        quiz = Quiz(
            title=data.get('title'),
            description=data.get('description', ''),
            time_limit_minutes=time_limit
        )
        db.session.add(quiz)
        db.session.commit()
        return jsonify({'success': True, 'quiz_id': quiz.id})

    return render_template('create_quiz.html')

@quiz_bp.route('/quiz/upload', methods=['GET', 'POST'])
@login_required
def upload_quiz():
    """Upload quiz from file (CSV, JSON, or TXT)"""
    if request.method == 'POST':
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'})
        
        file = request.files['file']
        quiz_title = request.form.get('title', 'Imported Quiz')
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        # Handle the upload
        success, message = handle_quiz_upload(file, quiz_title)
        
        if success:
            # Get the last created quiz
            quiz = Quiz.query.order_by(Quiz.id.desc()).first()
            return jsonify({'success': True, 'quiz_id': quiz.id, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
    
    return render_template('upload_quiz.html')

@quiz_bp.route('/image/upload', methods=['POST'])
def upload_image():
    """Upload image file and return URL"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image provided'})
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'})
    
    success, result = save_image_file(file)
    
    if success:
        return jsonify({'success': True, 'url': result})
    else:
        return jsonify({'success': False, 'message': result})

@quiz_bp.route('/quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    """View quiz for taking the quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    return render_template('take_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/quiz/<int:quiz_id>/edit')
def edit_quiz(quiz_id):
    """Edit quiz questions"""
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
    return render_template('edit_quiz.html', quiz=quiz, questions=questions)

@quiz_bp.route('/quiz/<int:quiz_id>/results')
def quiz_results(quiz_id):
    """View quiz results"""
    quiz = Quiz.query.get_or_404(quiz_id)
    attempts = QuizAttempt.query.filter_by(quiz_id=quiz_id).order_by(QuizAttempt.started_at.desc()).all()
    return render_template('results.html', quiz=quiz, attempts=attempts)

@quiz_bp.route('/attempt/<int:attempt_id>/result')
def attempt_result(attempt_id):
    """View specific attempt result"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    quiz = attempt.quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).order_by(Question.order).all()
    return render_template('attempt_detail.html', attempt=attempt, quiz=quiz, questions=questions)

# ==================== API ENDPOINTS ====================

@api_bp.route('/quiz/<int:quiz_id>/questions', methods=['GET', 'POST'])
def manage_questions(quiz_id):
    """Get or create questions for a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'GET':
        questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order).all()
        return jsonify([q.to_dict() for q in questions])
    
    # POST - Create new question
    data = request.get_json()
    question = Question(
        quiz_id=quiz_id,
        question_text=data.get('question_text'),
        question_type=data.get('question_type', 'multiple_choice'),
        image_url=data.get('image_url'),
        order=Question.query.filter_by(quiz_id=quiz_id).count()
    )
    db.session.add(question)
    db.session.flush()
    
    # Add answers
    for i, answer_data in enumerate(data.get('answers', [])):
        answer = Answer(
            question_id=question.id,
            answer_text=answer_data.get('answer_text'),
            image_url=answer_data.get('image_url'),
            is_correct=answer_data.get('is_correct', False),
            order=i
        )
        db.session.add(answer)
    
    db.session.commit()
    return jsonify({'success': True, 'question_id': question.id})

@api_bp.route('/question/<int:question_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_question(question_id):
    """Get, update, or delete a specific question"""
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'GET':
        include_correct = request.args.get('include_correct', 'false').lower() == 'true'
        return jsonify(question.to_dict(include_correct=include_correct))
    
    if request.method == 'PUT':
        data = request.get_json()
        question.question_text = data.get('question_text', question.question_text)
        question.question_type = data.get('question_type', question.question_type)
        question.image_url = data.get('image_url', question.image_url)
        
        # Update answers
        if 'answers' in data:
            Answer.query.filter_by(question_id=question_id).delete()
            for i, answer_data in enumerate(data.get('answers')):
                answer = Answer(
                    question_id=question_id,
                    answer_text=answer_data.get('answer_text'),
                    image_url=answer_data.get('image_url'),
                    is_correct=answer_data.get('is_correct', False),
                    order=i
                )
                db.session.add(answer)
        
        db.session.commit()
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        db.session.delete(question)
        db.session.commit()
        return jsonify({'success': True})

@api_bp.route('/quiz/<int:quiz_id>/start-attempt', methods=['POST'])
@login_required
def start_attempt(quiz_id):
    """Start a new quiz attempt"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_questions=Question.query.filter_by(quiz_id=quiz_id).count()
    )
    db.session.add(attempt)
    db.session.commit()
    
    return jsonify({'success': True, 'attempt_id': attempt.id})

@api_bp.route('/attempt/<int:attempt_id>/answer', methods=['POST'])
@login_required
def submit_answer(attempt_id):
    """Submit an answer to a question"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify user owns this attempt
    if attempt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    question_id = data.get('question_id')
    answer_id = data.get('answer_id')
    
    question = Question.query.get_or_404(question_id)
    answer = Answer.query.get_or_404(answer_id)
    
    # Check if answer is already submitted
    existing = QuizResponse.query.filter_by(
        attempt_id=attempt_id,
        question_id=question_id
    ).first()
    
    if existing:
        db.session.delete(existing)
    
    is_correct = answer.is_correct
    response = QuizResponse(
        attempt_id=attempt_id,
        question_id=question_id,
        answer_id=answer_id,
        is_correct=is_correct
    )
    db.session.add(response)
    db.session.commit()
    
    return jsonify({'success': True, 'is_correct': is_correct})

@api_bp.route('/attempt/<int:attempt_id>/complete', methods=['POST'])
@login_required
def complete_attempt(attempt_id):
    """Complete a quiz attempt and calculate score"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify user owns this attempt
    if attempt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    attempt.completed_at = datetime.utcnow()
    
    # Calculate score
    responses = QuizResponse.query.filter_by(attempt_id=attempt_id).all()
    correct_count = sum(1 for r in responses if r.is_correct)
    attempt.score = correct_count
    
    db.session.commit()
    
    # Update user stats
    update_user_stats(current_user.id, attempt)
    
    return jsonify({
        'success': True,
        'score': attempt.score,
        'total': attempt.total_questions,
        'percentage': round((attempt.score / attempt.total_questions * 100) if attempt.total_questions > 0 else 0, 2)
    })

@api_bp.route('/attempt/<int:attempt_id>', methods=['GET'])
def get_attempt(attempt_id):
    """Get attempt details"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    responses = QuizResponse.query.filter_by(attempt_id=attempt_id).all()
    
    response_data = {}
    for r in responses:
        response_data[r.question_id] = {
            'answer_id': r.answer_id,
            'is_correct': r.is_correct
        }
    
    return jsonify({
        'attempt': attempt.to_dict(),
        'responses': response_data
    })

@api_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_quiz(quiz_id):
    """Manage quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'GET':
        return jsonify(quiz.to_dict())
    
    if request.method == 'PUT':
        data = request.get_json()
        quiz.title = data.get('title', quiz.title)
        quiz.description = data.get('description', quiz.description)
        quiz.is_published = data.get('is_published', quiz.is_published)
        if 'time_limit_minutes' in data:
            tl = data.get('time_limit_minutes')
            quiz.time_limit_minutes = tl if tl not in ('', 0) else None
        quiz.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'success': True})


# ==================== TIME LIMIT & QUIZ SETTINGS ====================

@api_bp.route('/quiz/<int:quiz_id>/settings', methods=['PUT'])
@login_required
def update_quiz_settings(quiz_id):
    """Update quiz settings including time limit and music"""
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    quiz.time_limit_minutes = data.get('time_limit_minutes', quiz.time_limit_minutes)
    quiz.enable_music = data.get('enable_music', quiz.enable_music)
    quiz.music_url = data.get('music_url', quiz.music_url)
    quiz.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'quiz': quiz.to_dict()})


@api_bp.route('/attempt/<int:attempt_id>/time', methods=['POST'])
@login_required
def update_attempt_time(attempt_id):
    """Update time spent on quiz attempt"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    attempt.time_spent_seconds = data.get('time_spent_seconds', attempt.time_spent_seconds)
    db.session.commit()
    
    return jsonify({'success': True})


# ==================== RANKING & USER STATS ====================

@quiz_bp.route('/leaderboard')
def leaderboard():
    """View global leaderboard"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get top users by points
    top_users = db.session.query(User).outerjoin(UserStats).order_by(
        UserStats.total_points.desc()
    ).paginate(page=page, per_page=per_page)
    
    # Generate leaderboard graph
    top_10 = db.session.query(User).outerjoin(UserStats).order_by(
        UserStats.total_points.desc()
    ).limit(15).all()
    
    leaderboard_graph = GraphGenerator.generate_ranking_distribution_graph(top_10)
    
    return render_template('leaderboard.html', 
                          users=top_users.items,
                          pagination=top_users,
                          leaderboard_graph=leaderboard_graph)


@api_bp.route('/user/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics"""
    user = User.query.get_or_404(user_id)
    
    if not user.stats:
        # Create stats if they don't exist
        stats = UserStats(user_id=user_id)
        db.session.add(stats)
        db.session.commit()
    
    return jsonify(user.stats.to_dict())


def update_user_stats(user_id, quiz_attempt):
    """Update user stats after quiz completion"""
    user = User.query.get_or_404(user_id)
    
    if not user.stats:
        user.stats = UserStats(user_id=user_id)
    
    stats = user.stats
    
    # Update statistics
    stats.total_quizzes_taken += 1
    correct_count = quiz_attempt.score
    wrong_count = quiz_attempt.total_questions - quiz_attempt.score
    
    stats.total_correct_answers += correct_count
    stats.total_wrong_answers += wrong_count
    
    # Points system: 10 points per correct answer
    points_earned = correct_count * 10
    stats.total_points += points_earned
    
    # Update best score
    if quiz_attempt.score > stats.best_score:
        stats.best_score = quiz_attempt.score
    
    # Calculate average score
    if stats.total_quizzes_taken > 0:
        all_attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
        total_percentage = sum(a.percentage for a in all_attempts if a.completed_at)
        stats.avg_score = total_percentage / len([a for a in all_attempts if a.completed_at])
    
    # Update rank
    update_all_ranks()
    
    db.session.commit()


def update_all_ranks():
    """Recalculate all user ranks based on total points"""
    all_stats = UserStats.query.order_by(UserStats.total_points.desc()).all()
    for rank, stat in enumerate(all_stats, 1):
        stat.rank = rank
    db.session.commit()


@api_bp.route('/user/<int:user_id>/rank', methods=['GET'])
def get_user_rank(user_id):
    """Get user's current rank"""
    user = User.query.get_or_404(user_id)
    
    if not user.stats:
        return jsonify({'rank': 0, 'total_users': 0}), 404
    
    total_users = db.session.query(UserStats).count()
    
    return jsonify({
        'rank': user.stats.rank,
        'total_users': total_users,
        'total_points': user.stats.total_points
    })


# ==================== EDUCATIONAL ARTICLES ====================

@quiz_bp.route('/articles')
def articles_list():
    """List all published articles"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    
    query = Article.query.filter_by(is_published=True)
    
    if search:
        query = query.filter(
            (Article.title.ilike(f'%{search}%')) |
            (Article.description.ilike(f'%{search}%')) |
            (Article.content.ilike(f'%{search}%'))
        )
    
    if category:
        query = query.filter_by(category=category)
    
    articles = query.order_by(Article.created_at.desc()).paginate(page=page, per_page=12)
    
    # Get all unique categories
    categories = db.session.query(Article.category).filter_by(is_published=True).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('articles.html',
                          articles=articles.items,
                          pagination=articles,
                          search=search,
                          categories=categories,
                          current_category=category)


def _slugify(text):
    """Generate a URL-friendly slug from arbitrary text."""
    text = (text or '').strip().lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text or 'article'


def _unique_slug(base):
    """Return a slug that does not collide with an existing article."""
    candidate = base
    suffix = 2
    while Article.query.filter_by(slug=candidate).first() is not None:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


@quiz_bp.route('/article/new', methods=['GET', 'POST'])
@login_required
def submit_article():
    """Form for any logged-in user to submit a scientific article."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()

        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        if not title or not content:
            error = 'Title and content are required.'
            if request.is_json:
                return jsonify({'success': False, 'message': error}), 400
            flash(error, 'error')
            return render_template('submit_article.html', form_data=data), 400

        try:
            read_time = int(data.get('read_time_minutes') or 5)
        except (TypeError, ValueError):
            read_time = 5

        article = Article(
            title=title,
            slug=_unique_slug(_slugify(title)),
            description=(data.get('description') or '').strip() or None,
            content=content,
            category=(data.get('category') or '').strip() or None,
            tags=(data.get('tags') or '').strip() or None,
            author=current_user.username,
            thumbnail_url=(data.get('thumbnail_url') or '').strip() or None,
            read_time_minutes=read_time,
            is_published=True,
        )
        db.session.add(article)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'slug': article.slug, 'article_id': article.id}), 201
        flash('Article submitted! It is now visible to everyone.', 'success')
        return redirect(url_for('quiz.view_article', slug=article.slug))

    return render_template('submit_article.html', form_data={})


@quiz_bp.route('/article/<slug>')
def view_article(slug):
    """View specific article"""
    article = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Increment view count
    article.views += 1
    db.session.commit()
    
    # Check if bookmarked by current user
    is_bookmarked = False
    if current_user.is_authenticated:
        is_bookmarked = article in current_user.articles_bookmarked
    
    # Get related articles
    related_articles = Article.query.filter_by(
        category=article.category,
        is_published=True
    ).filter(Article.id != article.id).limit(4).all()
    
    return render_template('article_detail.html',
                          article=article,
                          is_bookmarked=is_bookmarked,
                          related_articles=related_articles)


@api_bp.route('/article', methods=['POST'])
@login_required
def create_article():
    """Create new article (admin only)"""
    # Add admin check in production
    data = request.get_json()
    
    article = Article(
        title=data.get('title'),
        slug=data.get('slug'),
        description=data.get('description'),
        content=data.get('content'),
        category=data.get('category'),
        tags=data.get('tags'),
        author=current_user.username,
        thumbnail_url=data.get('thumbnail_url'),
        read_time_minutes=data.get('read_time_minutes', 5),
        is_published=data.get('is_published', False)
    )
    
    db.session.add(article)
    db.session.commit()
    
    return jsonify({'success': True, 'article_id': article.id}), 201


@api_bp.route('/article/<int:article_id>', methods=['PUT', 'DELETE'])
@login_required
def manage_article(article_id):
    """Update or delete article"""
    article = Article.query.get_or_404(article_id)
    
    if request.method == 'PUT':
        data = request.get_json()
        article.title = data.get('title', article.title)
        article.description = data.get('description', article.description)
        article.content = data.get('content', article.content)
        article.category = data.get('category', article.category)
        article.tags = data.get('tags', article.tags)
        article.thumbnail_url = data.get('thumbnail_url', article.thumbnail_url)
        article.read_time_minutes = data.get('read_time_minutes', article.read_time_minutes)
        article.is_published = data.get('is_published', article.is_published)
        article.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True})
    
    if request.method == 'DELETE':
        db.session.delete(article)
        db.session.commit()
        return jsonify({'success': True})


@api_bp.route('/article/<int:article_id>/bookmark', methods=['POST'])
@login_required
def bookmark_article(article_id):
    """Bookmark or unbookmark an article"""
    article = Article.query.get_or_404(article_id)
    
    is_bookmarked = article in current_user.articles_bookmarked
    
    if is_bookmarked:
        current_user.articles_bookmarked.remove(article)
        article.bookmarks_count -= 1
    else:
        current_user.articles_bookmarked.append(article)
        article.bookmarks_count += 1
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'bookmarked': not is_bookmarked,
        'bookmarks_count': article.bookmarks_count
    })


@quiz_bp.route('/my-bookmarks')
@login_required
def my_bookmarks():
    """View user's bookmarked articles"""
    page = request.args.get('page', 1, type=int)
    
    bookmarked_articles = current_user.articles_bookmarked
    
    # Manual pagination since we're using relationship
    per_page = 12
    start = (page - 1) * per_page
    end = start + per_page
    
    articles_page = bookmarked_articles[start:end]
    total = len(bookmarked_articles)
    
    return render_template('my_bookmarks.html',
                          articles=articles_page,
                          total=total,
                          page=page,
                          per_page=per_page)


# ==================== GRAPH & ANALYTICS ====================

@api_bp.route('/attempt/<int:attempt_id>/graph', methods=['GET'])
def get_attempt_graph(attempt_id):
    """Get result graph for specific attempt"""
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    
    # Verify user owns this attempt or is admin
    if attempt.user_id != current_user.id and not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    graph = GraphGenerator.generate_attempt_result_graph(attempt)
    
    return jsonify({
        'success': True,
        'graph': graph,
        'attempt': attempt.to_dict()
    })


@quiz_bp.route('/my-results')
@login_required
def my_results():
    """View user's quiz results with graphs"""
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).filter(
        QuizAttempt.completed_at.isnot(None)
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    # Generate graphs
    performance_graph = GraphGenerator.generate_user_analysis_graph(current_user)
    category_graph = GraphGenerator.generate_category_performance_graph(current_user)
    stats_graph = GraphGenerator.generate_statistics_summary(current_user)
    
    return render_template('my_results.html',
                          attempts=attempts,
                          performance_graph=performance_graph,
                          category_graph=category_graph,
                          stats_graph=stats_graph)


@api_bp.route('/user/<int:user_id>/analytics', methods=['GET'])
def get_user_analytics(user_id):
    """Get comprehensive user analytics"""
    user = User.query.get_or_404(user_id)
    
    # Check permissions
    if user_id != current_user.id and not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    stats = user.stats.to_dict() if user.stats else {}
    attempts = [a.to_dict() for a in user.attempts if a.completed_at]
    
    return jsonify({
        'user': user.to_dict(),
        'stats': stats,
        'attempts': attempts
    })
