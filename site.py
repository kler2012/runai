import io
import os
import tempfile
from tkinter import Image
from flask import Flask, jsonify, render_template, request, redirect, send_file, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import base64
from moviepy.editor import VideoFileClip
from PIL import Image
from datetime import datetime




app = Flask(__name__)
            

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'run.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kekw'
db = SQLAlchemy(app)



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Clients(UserMixin, db.Model):
    ID_Client = db.Column(db.Integer, primary_key=True)
 
 
 
    Login = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Reason = db.Column(db.Text)
    Quantity = db.Column(db.Text)
    Points = db.Column(db.Integer, default=1)

    def get_id(self):
        return str(self.ID_Client)

class Analysis(db.Model):
    ID_Analysis = db.Column(db.Integer, primary_key=True)
    Video = db.Column(db.BLOB)
    ProcessedVideo = db.Column(db.BLOB)
    FootAnalysis = db.Column(db.Float)
    LegAnalysis =  db.Column(db.Float)
    ArmAnalysis = db.Column(db.Float)
    Thumbnail = db.Column(db.BLOB)
    Status = db.Column(db.String(20), default='pending')
    Client_id = db.Column(db.Integer, db.ForeignKey('clients.ID_Client'), nullable=False)
    UploadDate = db.Column(db.Date, default=datetime.utcnow)
    client = db.relationship('Clients', backref=db.backref('analyses', lazy=True))


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    criteria = db.Column(db.String(50), nullable=False)  
    min_rating = db.Column(db.Float, nullable=False)     
    max_rating = db.Column(db.Float, nullable=False)     
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_path = db.Column(db.String(200), nullable=False) 

def add_exercises_to_db():
    exercises = [
        Exercise(criteria="Стопы", min_rating=2.5, max_rating=3.0, name="Ходьба на пятках", description="Укрепляет мышцы голени и лодыжки, что помогает улучшить стабильность и баланс во время бега. Делайте 3-4 серии по 20-30 шагов.", video_path="static/videos/exercise1.mp4"),
        Exercise(criteria="Стопы", min_rating=2.5, max_rating=3.0, name="Ходьба на носках в полуприседе", description="Усиливает мышцы бедер, ягодиц и голени, что помогает улучшить выносливость и мощность во время бега. Делайте 3-4 серии по 20-30 шагов.", video_path="static/videos/exercise2.mp4"),
        Exercise(criteria="Стопы", min_rating=1.5, max_rating=2.5, name="Прыжки в приседе с продвижением вперед", description="Усиливает мышцы бедер, ягодиц и голени, повышает сердечно-сосудистую выносливость, что помогает улучшить скорость и выносливость во время бега. Делайте 3-4 серии по 10-15 прыжков.", video_path="static/videos/exercise3.mp4"),
        Exercise(criteria="Стопы", min_rating=1.5, max_rating=2.5, name="Бег высоко поднимая колени с последующим выпрямлением ног («колесо»)", description="Улучшает координацию и баланс, усиливает мышцы бедер, ягодиц и голени, что помогает улучшить технику бега и выносливость.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise4.mp4"),
        Exercise(criteria="Стопы", min_rating=0.0, max_rating=1.5, name="Многократные прыжки на одной или двух ногах на месте и с продвижением вперед.", description="Улучшает выносливость и скорость, усиливает мышцы бедер, ягодиц и голени, что помогает улучшить мощность и скорость во время бега. Делайте 3-4 серии по 10-15 прыжков.", video_path="static/videos/exercise5.mp4"),
        Exercise(criteria="Стопы", min_rating=0.0, max_rating=1.5, name="Прыжки на прямых ногах.", description="Улучшает мощность и скорость, усиливает мышцы бедер, ягодиц и голени, что помогает улучшить мощность и скорость во время бега. Делайте 3-4 серии по 10-15 прыжков.", video_path="static/videos/exercise6.mp4"),
        Exercise(criteria="Руки", min_rating=2.5, max_rating=3.0, name="Сгибание-разгибание рук в упоре лежа", description="Укрепляет мышцы рук, плеч и груди, способствует повышению выносливости и мощности. Выполняйте 2-3 серии по 10-15 повторений.", video_path="static/videos/exercise7.mp4"),
        Exercise(criteria="Руки", min_rating=2.5, max_rating=3.0, name="Подтягивания с собственным весом.", description="Укрепляет мышцы рук, спины, плеч и груди, способствует повышению выносливости и мощности. Выполняйте 3-4 серии по 10-15 повторений.", video_path="static/videos/exercise8.mp4"),
        Exercise(criteria="Руки", min_rating=1.5, max_rating=2.5, name="Вращение палки", description="Улучшает координацию и баланс, укрепляет мышцы рук, плеч и груди. Выполняйте 3-4 серии по 20-30 вращений.", video_path="static/videos/exercise9.mp4"),
        Exercise(criteria="Руки", min_rating=1.5, max_rating=2.5, name="Работа рук на месте быстро", description="Улучшает скорость и выносливость рук, укрепляет мышцы рук, плеч и груди. Выполняйте 3-4 серии по 20-30 повторений.", video_path="static/videos/exercise10.mp4"),
        Exercise(criteria="Руки", min_rating=0.0, max_rating=1.5, name="Работа рук на месте с остановкой", description="Улучшает контроль и выносливость рук, укрепляет мышцы рук, плеч и груди. Выполняйте 3-4 серии по 20-30 повторений.", video_path="static/videos/exercise11.mp4"),
        Exercise(criteria="Руки", min_rating=0.0, max_rating=1.5, name="Беговые махи", description="Улучшает координацию и выносливость рук, укрепляет мышцы рук, плеч и груди, способствует улучшению техники бега. Выполняйте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise12.mp4"),
        Exercise(criteria="Колени", min_rating=2.5, max_rating=3.0, name="Бег прыжками", description="Повышает мощность и выносливость ног, укрепляет мышцы бедер, ягодиц и голени, улучшает координацию.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise13.mp4"),
        Exercise(criteria="Колени", min_rating=2.5, max_rating=3.0, name="Семенящий бег", description="Улучшает скорость и реакцию ног, усиливает мышцы бедер, ягодиц и голени, развивает гибкость.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise14.mp4"),
        Exercise(criteria="Колени", min_rating=1.5, max_rating=2.5, name="Выпрыгивание из приседа", description="Увеличивает мощность и выносливость ног, укрепляет мышцы бедер, ягодиц и голени, помогает сжигать калории, улучшает баланс.  Делайте 3-4 серии по 10-15 повторений.", video_path="static/videos/exercise3.mp4"),
        Exercise(criteria="Колени", min_rating=1.5, max_rating=2.5, name="Бег в упоре", description="Повышает выносливость и мощность ног, усиливает мышцы бедер, ягодиц и голени, улучшает технику бега, развивает мышцы корпуса.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise16.mp4"),
        Exercise(criteria="Колени", min_rating=0.0, max_rating=1.5, name="Бег с захлестыванием голени", description="Улучшает скорость и координацию ног, усиливает мышцы бедер, ягодиц и голени, развивает гибкость, улучшает технику бега.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise17.mp4"),
        Exercise(criteria="Колени", min_rating=0.0, max_rating=1.5, name="Бег на прямых ногах", description="Увеличивает мощность и скорость ног, усиливает мышцы бедер, ягодиц и голени, улучшает технику бега, развивает мышцы корпуса.  Делайте 3-4 серии по 20-30 метров.", video_path="static/videos/exercise18.mp4"),
    ]

    db.session.add_all(exercises)
    db.session.commit()



@login_manager.user_loader
def load_user(user_id):
    return Clients.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html', user=current_user)


@app.route('/instructions')
def instructions():
    return render_template('instructions.html', user=current_user)


@app.route('/feedback')
def feedback():
    return render_template('feedback.html', user=current_user)


@app.route('/price')
def price():
    return render_template('price.html', user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        name = request.form['name']

        existing_client = Clients.query.filter_by(Login=login).first()
        if existing_client:
            flash("Логин уже используется")
        else:
            session['registration'] = {
                'login': login,
                'password': generate_password_hash(password, method='pbkdf2:sha256', salt_length=16),
                'name': name
            }
            return redirect(url_for('additional_info'))
    return render_template('register.html')



@app.route('/additional_info', methods=['GET', 'POST'])
def additional_info():
    if 'registration' not in session:
        return redirect(url_for('register'))

    if request.method == 'POST':
        try:
            registration_data = session['registration']
            login = registration_data['login']
            password = registration_data['password']
            name = registration_data['name']
            reason = request.form['reason']
            quantity = request.form['quantity']

            new_client = Clients(Login=login, Password=password, Name=name, Reason=reason, Quantity=quantity, Points=1)
            db.session.add(new_client)
            db.session.commit()
            login_user(new_client)
            flash('Регистрация успешна!')
            return jsonify({'status': 'success', 'message': 'Регистрация успешна!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Ошибка при завершении регистрации: {e}'})
    return render_template('additional_info.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = Clients.query.filter_by(Login=login).first()
        if user and check_password_hash(user.Password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неправильный логин или пароль')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('Нет выбранного файла')
        else:
            video = request.files['video']
            if video.filename == '':
                flash('Нет выбранного файла')
            elif video and video.filename.endswith('.mp4'):
                if current_user.Points > 0:
                    video_data = video.read()

                    temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    temp_video_file.write(video_data)
                    temp_video_file.close()

                    try:
                        with VideoFileClip(temp_video_file.name) as clip:
                            frame = clip.get_frame(1)
                            thumbnail = Image.fromarray(frame)
                            img_byte_arr = BytesIO()
                            thumbnail.save(img_byte_arr, format='JPEG')
                            thumbnail_data = img_byte_arr.getvalue()

                        foot_analysis, legs_analysis, arms_analysis, processed_video_path = analyze_video(temp_video_file.name)

                        with open(processed_video_path, 'rb') as f:
                            processed_video_data = f.read()

                        new_analysis = Analysis(
                            Video=video_data,
                            ProcessedVideo=processed_video_data,
                            Thumbnail=thumbnail_data,
                            Client_id=current_user.ID_Client,
                            FootAnalysis=foot_analysis,
                            LegAnalysis=legs_analysis,
                            ArmAnalysis=arms_analysis,
                            UploadDate=datetime.utcnow().date(),
                            Status='completed'
                        )
                        db.session.add(new_analysis)
                        current_user.Points -= 1
                        db.session.commit()
                        flash('Видео успешно загружено и проанализировано')
                    finally:
                        os.remove(temp_video_file.name)
                        os.remove(processed_video_path)
                else:
                    flash('Недостаточно очков для загрузки видео')
            else:
                flash('Файл должен быть в формате MP4')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=current_user)




@app.route('/buy_analysis', methods=['POST'])
@login_required
def buy_analysis():
    current_user.Points += 1
    db.session.commit()
    flash('Анализ успешно куплен')
    return redirect(url_for('profile'))


@app.route('/processed_video/<int:analysis_id>')
@login_required
def processed_video(analysis_id):
    analysis = Analysis.query.get(analysis_id)
    if analysis and analysis.client == current_user:
        return send_file(BytesIO(analysis.ProcessedVideo), mimetype='video/mp4')
    return 'Forbidden', 403

@app.route('/video/<int:analysis_id>')
@login_required
def video(analysis_id):
    analysis = Analysis.query.get(analysis_id)
    if analysis and analysis.client == current_user:
        return send_file(BytesIO(analysis.Video), mimetype='video/mp4')
    return 'Forbidden', 403

@app.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    analysis = Analysis.query.get(analysis_id)
    if analysis and analysis.client == current_user:
        
        foot_score_percent = int((analysis.FootAnalysis - 1) / 2 * 100)
        leg_score_percent = int((analysis.LegAnalysis - 1) / 2 * 100)
        arm_score_percent = int((analysis.ArmAnalysis - 1) / 2 * 100)

        
        def get_comment(criteria, score):
            if score >= 66:
                return "Хорошо"
            elif score >= 33:
                return "Нормально"
            else:
                return "Плохо"

        foot_comment = get_comment("Стопы", foot_score_percent)
        leg_comment = get_comment("Колени", leg_score_percent)
        arm_comment = get_comment("Руки", arm_score_percent)

        assessments = {
            "Стопы": {
                "Хорошо": "Ваши стопы работают хорошо. Вы приземляетесь и отталкиваетесь правильно, что позволяет вам бежать быстрее и эффективнее.",
                "Нормально": "Ваши стопы работают нормально, но есть небольшие недостатки, которые могут быть улучшены. Вы можете чувствовать некоторую усталость или дискомфорт, но риск травм минимален.",
                "Плохо": "Ваши стопы работают неправильно. Данная техника может привести к травмам и болям в суставах, также замедлить ваш бег."
            },
            "Руки": {
                "Хорошо": "Ваши руки работают хорошо. Вы держите их правильно и используете для баланса и увеличения скорости.",
                "Нормально": "Ваши руки работают нормально, но есть небольшие недостатки, которые могут быть улучшены. Вы можете чувствовать некоторую усталость или дискомфорт в руках и плечах после, но риск травм минимален.",
                "Плохо": "Ваши руки работают неправильно. Вы не используете их для баланса и увеличения скорости. Данная техника может привести к травмам и болям в руках, плечах и шее."
            },
            "Колени": {
                "Хорошо": "Ваши колени работают хорошо. Они согнутые правильно и используются для амортизации и увеличения скорости.",
                "Нормально": "Ваши колени работают нормально, но есть небольшие недостатки, которые могут быть улучшены. Вы можете чувствовать некоторую усталость или дискомфорт в коленях после бега.",
                "Плохо": "Ваши колени работают неправильно. Они согнуты неправильно и не используются для амортизации и увеличения скорости. Данная техника может привести к травмам и болям в коленях, бедрах и пояснице."
            }
        }

        exercises = Exercise.query.filter(
            ((Exercise.criteria == 'Стопы') & (Exercise.min_rating <= analysis.FootAnalysis) & (Exercise.max_rating >= analysis.FootAnalysis)) |
            ((Exercise.criteria == 'Руки') & (Exercise.min_rating <= analysis.ArmAnalysis) & (Exercise.max_rating >= analysis.ArmAnalysis)) |
            ((Exercise.criteria == 'Колени') & (Exercise.min_rating <= analysis.LegAnalysis) & (Exercise.max_rating >= analysis.LegAnalysis))
        ).all()

        return render_template('view_analysis.html', analysis=analysis, assessments=assessments, exercises=exercises, foot_comment=foot_comment, leg_comment=leg_comment, arm_comment=arm_comment, foot_score_percent=foot_score_percent, leg_score_percent=leg_score_percent, arm_score_percent=arm_score_percent)
    return 'Forbidden', 403



@app.route('/video_thumbnail/<int:analysis_id>')
@login_required
def video_thumbnail(analysis_id):
    analysis = Analysis.query.get(analysis_id)
    if analysis and analysis.Thumbnail:
        return send_file(io.BytesIO(analysis.Thumbnail), mimetype='image/jpeg')
    else:
        return send_file('static/img/thumbnail.jpeg', mimetype='image/jpeg')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
       # add_exercises_to_db()
    app.run(host='0.0.0.0')
 # type: ignore