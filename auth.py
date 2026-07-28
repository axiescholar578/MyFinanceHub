from flask_login import LoginManager, UserMixin


login_manager = LoginManager()
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, user_id, email):

        self.id = user_id
        self.email = email


@login_manager.user_loader
def load_user(user_id):

    return None
    