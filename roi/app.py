from flask import Flask 
from flask_login import LoginManager
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

#internal imports
from config import Config
from blueprints.site.routes import site
from blueprints.auth.routes import auth
from blueprints.api.routes import api 
from helpers import JSONENcoder
from models import Users,db



app = Flask(__name__)
app.config.from_object(Config)
app.json_encoder = JSONENcoder  # type: ignore
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please Log In"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(api)


db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

if __name__ == '__main__':
    app.run(host='localhost',port=5000,debug=True)