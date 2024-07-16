import os
from flask import Flask, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from io import BytesIO

app = Flask(__name__)

# Настройки базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'run.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'kekw'

db = SQLAlchemy(app)

class Clients(UserMixin, db.Model):
    ID_Client = db.Column(db.Integer, primary_key=True)
    Login = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    Name = db.Column(db.String(50), nullable=False)
    Age = db.Column(db.Integer, nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Height = db.Column(db.Integer, nullable=False)
    Weight = db.Column(db.Integer, nullable=False)
    Reason = db.Column(db.Text)
    Quantity = db.Column(db.Text)
    Points = db.Column(db.Integer, default=0)

    def get_id(self):
        return str(self.ID_Client)

class Analysis(db.Model):
    ID_Analysis = db.Column(db.Integer, primary_key=True)
    Video = db.Column(db.BLOB)
    ProcessedVideo = db.Column(db.BLOB)
    FootAnalysis = db.Column(db.Text)
    LegAnalysis = db.Column(db.Text)
    ArmAnalysis = db.Column(db.Text)
    Thumbnail = db.Column(db.BLOB)
    Status = db.Column(db.String(20), default='pending')
    Client_id = db.Column(db.Integer, db.ForeignKey('clients.ID_Client'), nullable=False)
    UploadDate = db.Column(db.Date, default=datetime.utcnow)
    client = db.relationship('Clients', backref=db.backref('analyses', lazy=True))

@app.route('/')
def home():
    records = Analysis.query.with_entities(Analysis.ID_Analysis).all()
    return render_template('index.html', records=records)

@app.route('/video/<int:id>')
def get_video(id):
    record = Analysis.query.get_or_404(id)
    video_data = record.Video
    return send_file(BytesIO(video_data), download_name='video.mp4', mimetype='video/mp4')

@app.route('/processed_video/<int:id>')
def get_processed_video(id):
    record = Analysis.query.get_or_404(id)
    processed_video_data = record.ProcessedVideo
    return send_file(BytesIO(processed_video_data), download_name='processed_video.mp4', mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)
