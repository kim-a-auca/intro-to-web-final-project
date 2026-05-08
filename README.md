# Online Poll System / Quiz App

A modern, interactive web application for creating and taking quizzes with a poll-style interface, similar to Kahoot but simplified and self-hosted.

# Features

# Core Features
- **Create Quizzes**: Easily create new quizzes with custom titles and descriptions
- **Question Management**: Add, edit, and delete questions with multiple answers
- **Mark Correct Answers**: Set which answers are correct when creating questions
- **Poll-Style Interface**: Beautiful poll UI inspired by Kahoot for taking quizzes
- **Real-time Feedback**: Immediate feedback on quiz answers
- **Quiz Results**: Comprehensive results tracking with user performance

# User Features
- **Take Quizzes**: Start a quiz with your name
- **Answer Questions**: Select answers in a poll-style format with visual feedback
- **View Results**: See your score, percentage, and detailed review of answers
- **Answer Review**: Review all questions and correct/incorrect answers after completing

# Admin Features
- **Quiz Editor**: Full-featured quiz editing interface
- **Question Editor**: Manage questions and answers with drag-and-drop (coming soon)
- **Results Dashboard**: View all quiz attempts and statistics
- **Quiz Management**: Create, edit, publish, and delete quizzes
- **Result Analytics**: View scores, percentages, and player performance

# Project Requirements Met

**Backend**: Python + Flask framework
**Database**: SQLite with SQLAlchemy ORM
**Frontend**: HTML5, CSS3, Vanilla JavaScript
**User Interaction**: Complete CRUD operations (Create, Read, Update, Delete)
**Real-time Updates**: Dynamic form submission and instant feedback
**Documentation**: Comprehensive setup and feature documentation
**Code Quality**: Clean, modular, well-organized codebase
**Bonus Features**: Results analytics, poll-style UI, modern gradient design

# Getting Started

# Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning)

# Installation

1. **Clone or navigate to the project directory**
```bash
cd poll-quiz-app
```

2. **Create a virtual environment** (recommended)
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python run.py
```

5. **Access the application**
```   
Open your web browser and navigate to:
http://127.0.0.1:5001
```
# Project Structure

```
poll-quiz-app/
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models
│   ├── views.py              # Routes and API endpoints
│   ├── forms.py              # WTForms validation
│   ├── config.py             # Configuration settings
│   ├── templates/            # HTML templates
│   │   ├── base.html         # Base template
│   │   ├── index.html        # Home page
│   │   ├── create_quiz.html  # Quiz creation
│   │   ├── edit_quiz.html    # Quiz editor
│   │   ├── take_quiz.html    # Quiz taking interface
│   │   ├── results.html      # Results dashboard
│   │   └── attempt_detail.html # Single attempt review
│   └── static/
│       └── css/
│           └── style.css     # Main stylesheet
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

# Database Models

# Quiz
- `id`: Primary key
- `title`: Quiz title
- `description`: Quiz description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `is_published`: Publication status
- Relationships: Questions, Attempts

# Question
- `id`: Primary key
- `quiz_id`: Foreign key to Quiz
- `question_text`: The question
- `question_type`: Type of question (multiple_choice, true_false)
- `order`: Question order in quiz
- Relationships: Answers, Responses

# Answer
- `id`: Primary key
- `question_id`: Foreign key to Question
- `answer_text`: The answer text
- `is_correct`: Boolean flag for correct answer
- `order`: Answer order
- Relationships: Responses

# QuizAttempt
- `id`: Primary key
- `quiz_id`: Foreign key to Quiz
- `user_name`: Name of the quiz taker
- `started_at`: Start timestamp
- `completed_at`: Completion timestamp
- `score`: Number of correct answers
- `total_questions`: Total questions in quiz
- Relationships: Responses

# QuizResponse
- `id`: Primary key
- `attempt_id`: Foreign key to QuizAttempt
- `question_id`: Foreign key to Question
- `answer_id`: Foreign key to Answer
- `is_correct`: Whether the answer was correct
- `answered_at`: Timestamp of response

# API Endpoints

# Web Routes
- `GET /` - Home page (list all quizzes)
- `GET /quiz/new` - Create quiz form
- `POST /quiz/new` - Create new quiz
- `GET /quiz/<id>` - Take quiz
- `GET /quiz/<id>/edit` - Edit quiz
- `GET /quiz/<id>/results` - View results
- `GET /attempt/<id>/result` - View attempt details

# API Endpoints
- `GET /api/quiz/<id>/questions` - Get quiz questions
- `POST /api/quiz/<id>/questions` - Create question
- `GET /api/question/<id>` - Get question details
- `PUT /api/question/<id>` - Update question
- `DELETE /api/question/<id>` - Delete question
- `POST /api/quiz/<id>/start-attempt` - Start quiz attempt
- `POST /api/attempt/<id>/answer` - Submit answer
- `POST /api/attempt/<id>/complete` - Complete attempt
- `GET /api/attempt/<id>` - Get attempt details
- `GET /api/quiz/<id>` - Get quiz details
- `PUT /api/quiz/<id>` - Update quiz
- `DELETE /api/quiz/<id>` - Delete quiz

# UI/UX Features

# Modern Design
- Gradient backgrounds (primary: Purple #667eea → Secondary: Pink #764ba2)
- Smooth animations and transitions
- Responsive grid layouts
- Professional color scheme

# Quiz Taking Experience
- Clean, distraction-free interface
- Large, easy-to-read question text
- Interactive poll-style answer options
- Progress bar showing quiz progress
- Immediate visual feedback on selections

# Results & Analytics
- Score display with percentage
- Detailed answer review
- Correct/incorrect answer highlighting
- Player statistics and leaderboard view
- Performance metrics summary

# Dependencies

```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-WTF==1.1.1
WTForms==3.0.1
Werkzeug==2.3.7
```

# Configuration

The application uses Flask configuration with three environments:

# Development (Default)
- Debug mode: ON
- Database: SQLite local file
- Secret key: Development default

# Production
- Debug mode: OFF
- Session cookies: Secure
- Must set SECRET_KEY environment variable

# Testing
- In-memory database
- Debug mode: ON

Configuration is in `app/config.py`

# Usage Guide

# Creating a Quiz

1. Click "Create Quiz" button
2. Enter quiz title and description
3. Click "Create Quiz"
4. Add questions using "+ Add Question"
5. Enter question text
6. Add multiple answers
7. Check the "Correct" checkbox for right answers
8. Save question
9. Repeat for more questions

# Taking a Quiz

1. Go to home page
2. Click "Take Quiz" on a quiz card
3. Enter your name
4. Click "Start Quiz"
5. Select your answers by clicking on each option
6. Navigate with Previous/Next buttons
7. Click "Submit Quiz" on the last question
8. View your results

# Viewing Results

1. Click "Results" on a quiz card to see all attempts
2. Click on a result card to view detailed feedback
3. See your score, percentage, and answer review

# Testing the Application

# Manual Testing Steps

1. **Create a Sample Quiz**
   - Create a quiz titled "General Knowledge"
   - Add 3 questions with 4 answers each
   - Mark the correct answers

2. **Take the Quiz**
   - Start the quiz as a new player
   - Answer all questions
   - Review results

3. **Test Multiple Attempts**
   - Take the same quiz again with different answers
   - Verify scoring accuracy

4. **Edit and Update**
   - Edit an existing quiz
   - Change question text or answers
   - Verify changes persist

# Database Initialization

The database is automatically created on first run:

```bash
python run.py
```

SQLite database file: `quiz_app.db` (auto-created in working directory)

To reset the database, simply delete `quiz_app.db` and restart the app.

# Troubleshooting

# Database Errors
- Delete `quiz_app.db` and restart the app
- Ensure the app directory is writable

# Template Not Found
Ensure you're running from the correct directory where `app/` folder exists

# Static Files Not Loading
Clear browser cache or do a hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

# Deployment

# Development
```bash
python run.py
```

# Production Deployment
Uses a production WSGI server (Gunicorn recommended):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Set environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY="your-secure-key-here"
```

# Code Quality

# Best Practices Implemented
- **Modular Structure**: Separation of concerns (models, views, forms)
- **Database ORM**: SQLAlchemy for clean database interactions
- **Form Validation**: WTForms for secure form handling
- **RESTful API**: Clean, intuitive API endpoints
- **Error Handling**: Proper HTTP status codes and error responses
- **Code Comments**: Well-documented code sections
- **Naming Conventions**: Clear, descriptive names for functions and variables
- **Security**: CSRF protection, input validation

# File Organization
- `models.py` - Database models and relationships
- `views.py` - Routes and business logic
- `forms.py` - Form definitions and validation
- `templates/` - HTML templates
- `static/css/` - Stylesheets

# Security Features

- CSRF protection on all forms
- Input validation via WTForms
- SQL injection prevention via SQLAlchemy ORM
- Secure session management