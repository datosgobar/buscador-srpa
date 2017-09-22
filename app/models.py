from . import db, SRPAException
from flask_user import UserMixin
from datetime import datetime


# TODO: chequear longitudes de los campos de texto
MAX_TEXT_LENGTH = 20000
MAX_NAME_LENGTH = 512


def get_or_create(session, model, **kwargs):
    """ Imita el get_or_create de django
        URL: http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance.id
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    password = db.Column(db.String(255), nullable=False)
    reset_password_token = db.Column(db.String(100))
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    def __init__(self, **kwargs):
        self.active = kwargs.get('active', False)
        self.password = kwargs.get('password', None)
        self.email = kwargs.get('email', None)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)


class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))


class Question(db.Model):
    __table_args__ = (db.UniqueConstraint('report_id', 'number', name='_report_question_number_uc'),)

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)

    question_type = db.Column(db.Text(MAX_TEXT_LENGTH))
    number = db.Column(db.Integer)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    context = db.Column(db.Text(MAX_TEXT_LENGTH))
    body = db.Column(db.Text(MAX_TEXT_LENGTH))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    question_date = db.Column(db.DateTime)

    answer = db.Column(db.Text(MAX_TEXT_LENGTH))
    answer_author_id = db.Column(db.Integer, db.ForeignKey('answer_author.id'))
    answer_date = db.Column(db.DateTime)

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    subtopic_id = db.Column(db.Integer, db.ForeignKey('subtopic.id'))

    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, **kwargs):
        self.question_type = kwargs.get('question_type', None)
        self.report_id = kwargs.get('report_id', None)
        self.number = kwargs.get('number', None)
        if not isinstance(self.number, int):
            try:
                self.number = int(self.number)
            except ValueError:
                message = 'Error al interpretar la columna "Numero"'
                description = '{number} no es un numero'.format(number=str(self.number))
                raise SRPAException(message=message, description=description)

        self.context = kwargs.get('context', '')
        self.body = kwargs.get('body', '')
        self.author_id = kwargs.get('author_id', None)
        self.question_date = kwargs.get('question_date', None)

        self.answer = kwargs.get('answer', '')
        self.answer_author_id = kwargs.get('answer_author_id', None)
        self.answer_date = kwargs.get('answer_date', None)

        self.keywords = kwargs.get('keywords', [])
        self.topic_id = kwargs.get('topic_id', None)
        self.subtopic_id = kwargs.get('subtopic_id', None)

    @classmethod
    def delete(cls, question_id, db_session):
        question = cls.query.get(question_id)
        db_session.delete(question)
        db_session.commit()

    @classmethod
    def update(cls, question_id, db_session, new_attrs):
        question = cls.query.get(question_id)
        if 'topic' in new_attrs:
            question.topic_id = get_or_create(db_session, Topic, name=new_attrs['topic'])
        if 'subtopic' in new_attrs:
            question.subtopic_id = get_or_create(db_session, SubTopic, name=new_attrs['subtopic'])
        db_session.commit()
        return question


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)
    date = db.Column(db.Date())
    questions = db.relationship('Question', backref='report')
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

association_table = db.Table(
    'association',
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id')),
    db.Column('subtopic_id', db.Integer, db.ForeignKey('subtopic.id'))
)


class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)
    questions = db.relationship('Question', backref='topic')
    subtopics = db.relationship("SubTopic",
                                secondary=association_table,
                                backref=db.backref('topics', lazy='dynamic'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class SubTopic(db.Model):
    __tablename__ = 'subtopic'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)
    questions = db.relationship('Question', backref='subtopic')
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)
    questions = db.relationship('Question', backref='author')
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # TODO: agregar origen del autor (prov, ciudad, etc)
    # y bloque al cual pertenece (ver excel)


class AnswerAuthor(db.Model):
    __tablename__ = 'answer_author'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(MAX_NAME_LENGTH), unique=True)
    questions = db.relationship('Question', backref='answer_author')
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
