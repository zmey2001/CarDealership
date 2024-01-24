from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from wtforms import TextAreaField, SelectField

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'


login_manager = LoginManager(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
from flask_login import AnonymousUserMixin

class AnonymousUser(AnonymousUserMixin):
    role = 'anonymous'

login_manager.anonymous_user = AnonymousUser




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Добавлено поле для роли (student или teacher)
    def is_active(self):
        return True


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('assignments', lazy=True))
    response = db.Column(db.Text, nullable=True)  # Новое поле для ответов
    messages = db.relationship('Message', backref='assignment', lazy=True)  # Связь с сообщениями

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    teacher = db.Column(db.String(80), nullable=True)  # Добавлено поле для преподавателя


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddAssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Assignment')

@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/add_assignment', methods=['GET', 'POST'])
@login_required
def add_assignment():
    form = AddAssignmentForm()

    # Заполните поле выбора предмета данными из базы данных
    form.subject_id.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

    if form.validate_on_submit():
        # Получите данные из формы и добавьте задание в базу данных
        title = form.title.data
        content = form.content.data
        subject_id = form.subject_id.data

        assignment = Assignment(title=title, content=content, subject_id=subject_id, deadline=datetime.utcnow())
        db.session.add(assignment)
        db.session.commit()

        # После добавления задания перенаправьте на главную страницу
        return redirect(url_for('dashboard'))

    return render_template('add_assignment.html', form=form)

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    assignments = subject.assignments
    return render_template('subject.html', subject=subject, assignments=assignments)

@app.route('/submit_response/<int:assignment_id>', methods=['POST'])
def submit_response(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)

    # Проверяем, является ли текущий пользователь учителем
    if current_user.role != 'teacher':
        # Если нет, то обрабатываем ответ
        assignment.response = request.form.get('response')
        db.session.commit()
        return redirect(url_for('subject', subject_id=assignment.subject.id))
    else:
        # Если пользователь учитель, перенаправляем обратно на страницу предмета
        return redirect(url_for('subject', subject_id=assignment.subject.id))


@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.utcnow()
    assignments = Assignment.query.filter(Assignment.deadline >= today).order_by(Assignment.deadline).all()
    subjects = Subject.query.all()

    # Добавляем проверку на анонимного пользователя
    user_role = getattr(current_user, 'role', None)

    return render_template('dashboard.html', assignments=assignments, subjects=subjects, user_role=user_role)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        existing_user1 = User.query.filter_by(username='ivan_ivanov').first()
        existing_user2 = User.query.filter_by(username='anna_smirnova').first()

        if not existing_user1:
            user1 = User(username='ivan_ivanov', password='12345', role='student')
            db.session.add(user1)

        if not existing_user2:
            user2 = User(username='anna_smirnova', password='password456', role='teacher')
            db.session.add(user2)

            # Use 'Subject' for services and 'Assignment' for subservices
        car_wash_service = Subject(name='Мойка автомобилей', teacher='Игорь Мойщиков')
        oil_change_service = Subject(name='Замена масла', teacher='Анна Маслообменова')
        tire_rotation_service = Subject(name='Разворот шин', teacher='Дмитрий Шиномонтажный')

        db.session.add_all([car_wash_service, oil_change_service, tire_rotation_service])

        today = datetime.utcnow()

        # Use 'Assignment' for subservices
        car_wash_assignment = Assignment(
            title='Мойка салона',
            content='Осуществить комплексную мойку салона автомобиля.',
            subject=car_wash_service,
            deadline=today + timedelta(days=3)
        )

        oil_change_assignment = Assignment(
            title='Полная замена масла',
            content='Выполнить полную замену масла в двигателе согласно техническим требованиям.',
            subject=oil_change_service,
            deadline=today + timedelta(days=5)
        )

        tire_rotation_assignment = Assignment(
            title='Поворот шин',
            content='Передняя-задняя перестановка колес для равномерного износа.',
            subject=tire_rotation_service,
            deadline=today + timedelta(days=7)
        )

        db.session.add_all([car_wash_assignment, oil_change_assignment, tire_rotation_assignment])

        # Example messages for assignments
        car_wash_message = Message(content='Когда доступен автомобиль для мойки?', assignment=car_wash_assignment)
        oil_change_message = Message(content='Требуется ли масло определенного бренда?', assignment=oil_change_assignment)
        tire_rotation_message = Message(content='Могу ли я использовать текущие шины или нужно купить новые?', assignment=tire_rotation_assignment)

        db.session.add_all([car_wash_message, oil_change_message, tire_rotation_message])


        # Добавление дополнительных пользователей
        existing_student1 = User.query.filter_by(username='olga_nikolaeva').first()
        existing_student2 = User.query.filter_by(username='dmitry_smirnov').first()

        if not existing_student1:
            student1 = User(username='olga_nikolaeva', password='studentpass', role='student')
            db.session.add(student1)

        if not existing_student2:
            student2 = User(username='dmitry_smirnov', password='studentpass123', role='student')
            db.session.add(student2)

        existing_teacher1 = User.query.filter_by(username='alexander_ivanov').first()
        existing_teacher2 = User.query.filter_by(username='irina_sidorova').first()

        if not existing_teacher1:
            teacher1 = User(username='alexander_ivanov', password='teacherpass', role='teacher')
            db.session.add(teacher1)

        if not existing_teacher2:
            teacher2 = User(username='irina_sidorova', password='teacherpass123', role='teacher')
            db.session.add(teacher2)

        db.session.commit()


        

    app.run(debug=True)
