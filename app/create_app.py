from flask_mail import Mail
from flask_user import SQLAlchemyAdapter, UserManager
from flask.ext.babel import Babel
from . import app, db, models
from .routes import init_routes
from .helpers import Searcher
import getpass
import os
import pprint
from .templates import init_template_filters


def create_db():
    app.config.from_object('app.config.Config')
    db.create_all()


def create_app():
    create_db()
    Babel(app)
    Mail(app)
    db_adapter = SQLAlchemyAdapter(db, models.User)
    UserManager(db_adapter, app)
    searcher = Searcher()
    init_routes(app, db.session, searcher)
    init_template_filters(app)
    return app


def _init_users_manager():
    os.environ['SMTP_PASS'] = os.environ.get('SMTP_PASS', '')
    app.config.from_object('app.config.Config')
    db_adapter = SQLAlchemyAdapter(db, models.User)
    return UserManager(db_adapter, app)


def create_user():
    user_manager = _init_users_manager()
    email = input("User email: ")
    if not models.User.query.filter(models.User.email == email).first():
        password = getpass.getpass('User password: ')
        password2 = getpass.getpass('Confirm user password: ')
        if password == password2:
            admin_user = models.User(
                email=email,
                active=True,
                password=user_manager.hash_password(password)
            )
            db.session.add(admin_user)
            db.session.commit()
            print('User created successfully')
        else:
            print("The passwords don't match")
    else:
        print('The user already exists')
    return


def list_users():
    _init_users_manager()
    for user in models.User.query.all():
        pprint.pprint({
            'id': user.id,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        })


def _get_user():
    email = input("User email: ")
    return models.User.query.filter(models.User.email == email).first()


def add_user_role():
    _init_users_manager()
    user = _get_user()
    if not user:
        print("User doesn't exist!")
        return
    current_roles = [role.name for role in user.roles]
    print('Current user roles: ' + str(current_roles))
    new_role_name = input("New role name: ")
    role_id = models.get_or_create(db.session, models.Role, name=new_role_name)
    role = models.Role.query.get(role_id)
    if role.name not in current_roles:
        user.roles.append(role)
    db.session.commit()


def remove_user_role():
    _init_users_manager()
    user = _get_user()
    if not user:
        print("User doesn't exist!")
        return
    role_to_remove = input("Role to remove: ")
    current_roles = [role.name for role in user.roles]
    if role_to_remove in current_roles:
        role_index = current_roles.index(role_to_remove)
        del user.roles[role_index]
        db.session.commit()
