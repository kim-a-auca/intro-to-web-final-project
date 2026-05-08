import os
import json
import csv
import uuid
from werkzeug.utils import secure_filename
from app import db
from app.models import Quiz, Question, Answer

ALLOWED_EXTENSIONS = {'csv', 'json', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'images')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_csv_quiz(file_content, quiz_title):
    """
    Parse CSV file format:
    Question,QuestionImage,Answer1,Answer1Image,Answer2,Answer2Image,Answer3,Answer3Image,Answer4,Answer4Image,CorrectAnswer
    
    QuestionImage and AnswerImage are optional URLs
    """
    try:
        lines = file_content.decode('utf-8').split('\n')
        reader = csv.DictReader(lines)
        
        quiz = Quiz(title=quiz_title, description="Imported from CSV")
        db.session.add(quiz)
        db.session.flush()
        
        for row_idx, row in enumerate(reader):
            if not row.get('Question'):
                continue
            
            question = Question(
                quiz_id=quiz.id,
                question_text=row['Question'],
                image_url=row.get('QuestionImage', '').strip() or None,
                order=row_idx
            )
            db.session.add(question)
            db.session.flush()
            
            # Add answers
            correct_answer = row.get('CorrectAnswer', '').strip()
            for ans_idx in range(1, 5):
                ans_key = f'Answer{ans_idx}'
                img_key = f'Answer{ans_idx}Image'
                if ans_key in row and row[ans_key]:
                    answer = Answer(
                        question_id=question.id,
                        answer_text=row[ans_key],
                        image_url=row.get(img_key, '').strip() or None,
                        is_correct=(row[ans_key] == correct_answer),
                        order=ans_idx - 1
                    )
                    db.session.add(answer)
        
        db.session.commit()
        return True, "CSV quiz imported successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"CSV parsing error: {str(e)}"

def parse_json_quiz(file_content, quiz_title):
    """
    Parse JSON file format:
    {
        "title": "Quiz Title",
        "description": "Description",
        "questions": [
            {
                "text": "Question?",
                "imageUrl": "https://example.com/image.jpg",
                "answers": [
                    {"text": "Answer 1", "imageUrl": "https://...", "correct": true},
                    {"text": "Answer 2", "imageUrl": "https://...", "correct": false}
                ]
            }
        ]
    }
    """
    try:
        data = json.loads(file_content.decode('utf-8'))
        
        quiz = Quiz(
            title=data.get('title', quiz_title),
            description=data.get('description', 'Imported from JSON')
        )
        db.session.add(quiz)
        db.session.flush()
        
        for q_idx, q_data in enumerate(data.get('questions', [])):
            question = Question(
                quiz_id=quiz.id,
                question_text=q_data['text'],
                image_url=q_data.get('imageUrl'),
                order=q_idx
            )
            db.session.add(question)
            db.session.flush()
            
            for a_idx, answer_data in enumerate(q_data.get('answers', [])):
                answer = Answer(
                    question_id=question.id,
                    answer_text=answer_data['text'],
                    image_url=answer_data.get('imageUrl'),
                    is_correct=answer_data.get('correct', False),
                    order=a_idx
                )
                db.session.add(answer)
        
        db.session.commit()
        return True, "JSON quiz imported successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"JSON parsing error: {str(e)}"

def parse_text_quiz(file_content, quiz_title):
    """
    Parse text file format:
    Question: What is X?
    QuestionImage: https://example.com/image.jpg
    A) Answer 1
    B) Answer 2*
    AnswerBImage: https://example.com/answer2.jpg
    C) Answer 3
    D) Answer 4
    (Asterisk * marks correct answer)
    (Images are optional URLs)
    """
    try:
        content = file_content.decode('utf-8')
        quiz = Quiz(title=quiz_title, description="Imported from text file")
        db.session.add(quiz)
        db.session.flush()
        
        lines = content.split('\n')
        current_question = None
        current_question_image = None
        answer_images = {}
        q_order = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('Question:'):
                current_question = Question(
                    quiz_id=quiz.id,
                    question_text=line.replace('Question:', '').strip(),
                    image_url=current_question_image or None,
                    order=q_order
                )
                db.session.add(current_question)
                db.session.flush()
                q_order += 1
                current_question_image = None
                answer_images = {}
            
            elif line.startswith('QuestionImage:'):
                current_question_image = line.replace('QuestionImage:', '').strip()
            
            elif line.startswith('Answer') and 'Image:' in line:
                # e.g., "AnswerAImage: https://..."
                parts = line.split(':', 1)
                if len(parts) == 2:
                    image_key = parts[0].strip().replace('Answer', '').replace('Image', '')
                    answer_images[image_key] = parts[1].strip()
            
            elif current_question and line and line[0] in ['A', 'B', 'C', 'D', 'E', 'F']:
                is_correct = line.endswith('*')
                answer_text = line[3:].replace('*', '').strip()
                letter = line[0]
                
                if answer_text:
                    answer = Answer(
                        question_id=current_question.id,
                        answer_text=answer_text,
                        image_url=answer_images.get(letter),
                        is_correct=is_correct,
                        order=ord(letter) - ord('A')
                    )
                    db.session.add(answer)
        
        db.session.commit()
        return True, "Text quiz imported successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Text parsing error: {str(e)}"

def handle_quiz_upload(file, quiz_title='Imported Quiz'):
    """
    Main handler for quiz file uploads.
    Supports CSV, JSON, TXT formats.
    """
    if not file or not allowed_file(file.filename):
        return False, "Invalid file type. Allowed: CSV, JSON, TXT"
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return False, "File too large. Maximum size: 5MB"
    
    try:
        file_content = file.read()
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        if ext == 'csv':
            return parse_csv_quiz(file_content, quiz_title)
        elif ext == 'json':
            return parse_json_quiz(file_content, quiz_title)
        elif ext == 'txt':
            return parse_text_quiz(file_content, quiz_title)
        else:
            return False, "Unsupported file format"
    
    except Exception as e:
        return False, f"Upload error: {str(e)}"

def is_allowed_image(filename):
    """Check if file is an allowed image type"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def save_image_file(file):
    """
    Save uploaded image file and return the URL path.
    
    Returns:
        tuple: (success: bool, url_or_error: str)
    """
    if not file or not file.filename:
        return False, "No file provided"
    
    if not is_allowed_image(file.filename):
        return False, f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    if file.content_length and file.content_length > MAX_IMAGE_SIZE:
        return False, f"Image too large. Maximum size: 2MB"
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Return URL path (relative to static folder)
        url_path = f"/static/uploads/images/{unique_filename}"
        return True, url_path
        
    except Exception as e:
        return False, f"Error saving image: {str(e)}"

