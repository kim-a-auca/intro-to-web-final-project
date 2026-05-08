#!/usr/bin/env python
"""
Quick start script to populate the database with sample quizzes
Run this after setting up the project to test the application
"""

from app import create_app, db
from app.models import Quiz, Question, Answer

# Create app context
app = create_app()

with app.app_context():
    # Clear existing data
    db.session.query(Answer).delete()
    db.session.query(Question).delete()
    db.session.query(Quiz).delete()
    db.session.commit()
    
    # Create sample quiz 1: General Knowledge
    quiz1 = Quiz(
        title="General Knowledge Quiz",
        description="Test your knowledge with these interesting general knowledge questions",
        is_published=True
    )
    db.session.add(quiz1)
    db.session.flush()
    
    q1 = Question(
        quiz_id=quiz1.id,
        question_text="What is the capital of France?",
        order=0
    )
    db.session.add(q1)
    db.session.flush()
    
    answers_q1 = [
        Answer(question_id=q1.id, answer_text="Paris", is_correct=True, order=0),
        Answer(question_id=q1.id, answer_text="Lyon", is_correct=False, order=1),
        Answer(question_id=q1.id, answer_text="Marseille", is_correct=False, order=2),
        Answer(question_id=q1.id, answer_text="Toulouse", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q1)
    
    q2 = Question(
        quiz_id=quiz1.id,
        question_text="Which planet is known as the Red Planet?",
        order=1
    )
    db.session.add(q2)
    db.session.flush()
    
    answers_q2 = [
        Answer(question_id=q2.id, answer_text="Venus", is_correct=False, order=0),
        Answer(question_id=q2.id, answer_text="Mars", is_correct=True, order=1),
        Answer(question_id=q2.id, answer_text="Jupiter", is_correct=False, order=2),
        Answer(question_id=q2.id, answer_text="Saturn", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q2)
    
    q3 = Question(
        quiz_id=quiz1.id,
        question_text="What is the largest ocean on Earth?",
        order=2
    )
    db.session.add(q3)
    db.session.flush()
    
    answers_q3 = [
        Answer(question_id=q3.id, answer_text="Atlantic Ocean", is_correct=False, order=0),
        Answer(question_id=q3.id, answer_text="Indian Ocean", is_correct=False, order=1),
        Answer(question_id=q3.id, answer_text="Arctic Ocean", is_correct=False, order=2),
        Answer(question_id=q3.id, answer_text="Pacific Ocean", is_correct=True, order=3),
    ]
    db.session.add_all(answers_q3)
    
    # Create sample quiz 2: Python Programming
    quiz2 = Quiz(
        title="Python Programming Basics",
        description="Test your knowledge of Python programming fundamentals",
        is_published=True
    )
    db.session.add(quiz2)
    db.session.flush()
    
    q4 = Question(
        quiz_id=quiz2.id,
        question_text="What does 'pip' stand for in Python?",
        order=0
    )
    db.session.add(q4)
    db.session.flush()
    
    answers_q4 = [
        Answer(question_id=q4.id, answer_text="Python Integrated Package", is_correct=False, order=0),
        Answer(question_id=q4.id, answer_text="Pip Installs Packages", is_correct=True, order=1),
        Answer(question_id=q4.id, answer_text="Python Install Program", is_correct=False, order=2),
        Answer(question_id=q4.id, answer_text="Package Import Protocol", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q4)
    
    q5 = Question(
        quiz_id=quiz2.id,
        question_text="Which of the following is NOT a Python data type?",
        order=1
    )
    db.session.add(q5)
    db.session.flush()
    
    answers_q5 = [
        Answer(question_id=q5.id, answer_text="Dictionary", is_correct=False, order=0),
        Answer(question_id=q5.id, answer_text="List", is_correct=False, order=1),
        Answer(question_id=q5.id, answer_text="Array", is_correct=True, order=2),
        Answer(question_id=q5.id, answer_text="Tuple", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q5)
    
    q6 = Question(
        quiz_id=quiz2.id,
        question_text="What is the correct way to create a function in Python?",
        order=2
    )
    db.session.add(q6)
    db.session.flush()
    
    answers_q6 = [
        Answer(question_id=q6.id, answer_text="func myFunction() {}", is_correct=False, order=0),
        Answer(question_id=q6.id, answer_text="def myFunction():", is_correct=True, order=1),
        Answer(question_id=q6.id, answer_text="function myFunction():", is_correct=False, order=2),
        Answer(question_id=q6.id, answer_text="define myFunction():", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q6)
    
    # Create sample quiz 3: History
    quiz3 = Quiz(
        title="World History",
        description="Questions about important historical events and figures",
        is_published=True
    )
    db.session.add(quiz3)
    db.session.flush()
    
    q7 = Question(
        quiz_id=quiz3.id,
        question_text="In what year did World War II end?",
        order=0
    )
    db.session.add(q7)
    db.session.flush()
    
    answers_q7 = [
        Answer(question_id=q7.id, answer_text="1943", is_correct=False, order=0),
        Answer(question_id=q7.id, answer_text="1944", is_correct=False, order=1),
        Answer(question_id=q7.id, answer_text="1945", is_correct=True, order=2),
        Answer(question_id=q7.id, answer_text="1946", is_correct=False, order=3),
    ]
    db.session.add_all(answers_q7)
    
    # Commit all changes
    db.session.commit()
    
    print("✓ Database populated with sample quizzes!")
    print(f"  - {Quiz.query.count()} quizzes created")
    print(f"  - {Question.query.count()} questions created")
    print(f"  - {Answer.query.count()} answers created")
    print("\nYou can now run: python run.py")
    print("Then visit: http://localhost:5000")
