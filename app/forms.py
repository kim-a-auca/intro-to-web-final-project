from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Optional

class AnswerForm(FlaskForm):
    """Form for individual answer"""
    answer_text = StringField('Answer', validators=[DataRequired(), Length(min=1, max=500)])
    is_correct = BooleanField('Mark as Correct')

class QuestionForm(FlaskForm):
    """Form for creating/editing questions"""
    question_text = StringField('Question', validators=[DataRequired(), Length(min=5, max=500)])
    answers = FieldList(FormField(AnswerForm), min_entries=2, max_entries=10)
    submit = SubmitField('Save Question')

class QuizForm(FlaskForm):
    """Form for creating/editing quizzes"""
    title = StringField('Quiz Title', validators=[DataRequired(), Length(min=3, max=200)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Create Quiz')

class QuizAttemptForm(FlaskForm):
    """Form for starting a quiz attempt"""
    user_name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Start Quiz')
