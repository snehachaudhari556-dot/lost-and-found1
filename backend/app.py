from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os


load_dotenv()


db = SQLAlchemy()
jwt = JWTManager()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')
app.config['UPLOAD_FOLDER'] = 'uploads'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


db.init_app(app)
jwt.init_app(app)


from routes.auth import auth_bp
from routes.reports import report_bp


app.register_blueprint(auth_bp)
app.register_blueprint(report_bp)


with app.app_context():
db.create_all()


if __name__ == '__main__':
app.run(debug=True)