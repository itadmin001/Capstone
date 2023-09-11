from flask import Flask 
from flask_migrate import Migrate 
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt


#internal imports
from config import Config
from .blueprints.site.routes import site
from .blueprints.auth.routes import auth
from .blueprints.api.routes import api 
from .models import login_manager, db
from .helpers import JSONENcoder



app = Flask(__name__)
app.config.from_object(Config)
app.json_encoder = JSONENcoder 
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

login_manager.init_app(app)
login_manager.login_view = 'auth.sign_in'
login_manager.login_message = "Please Log In"
login_manager.login_message_category = "warning"



app.register_blueprint(site)
app.register_blueprint(auth)
app.register_blueprint(api)


db.init_app(app)
migrate = Migrate(app, db)
CORS(app)