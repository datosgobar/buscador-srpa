from flask.ext.wtf import Form
from wtforms import validators, IntegerField, TextAreaField, BooleanField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_user.translations import lazy_gettext as _
from .models import MAX_TEXT_LENGTH, Question, Report, Topic, SubTopic, Author, AnswerAuthor, get_or_create
import time
from .helpers import SpreadSheetReader
from flask import render_template, redirect, url_for
from datetime import datetime
from sqlalchemy import func


class QuestionForm(Form):
    number = IntegerField(
        _('Question number'),
        [validators.NumberRange(min=1, message=_('Question number must be a \
                                                  positive integer'))]
    )
    body = TextAreaField(
        _('Question body'),
        [validators.Length(min=1, max=MAX_TEXT_LENGTH)]
    )
    context = TextAreaField(
        _('Question context (optional)'),
        [validators.Length(min=0, max=MAX_TEXT_LENGTH)]
    )
    report = SelectField(_('Report number'), default="")
    author = SelectField(_('Question author'), default="")
    topic = SelectField(_('Question topic'), default="")
    subtopic = SelectField(_('Question subtopic'), default="")
    answer = TextAreaField(
        _('Question answer'),
        [validators.Length(min=0, max=MAX_TEXT_LENGTH)]
    )

    def update_choices(self, db_session, searcher):
        other_models = searcher.list_models(db_session)
        attributes = [
            (u'informe', 'report'),
            (u'autor', 'author'),
            (u'ministerio', 'topic'),
            (u'área de gestión', 'subtopic')
        ]
        for attribute_pair in attributes:
            spanish_name = attribute_pair[0]
            english_name = attribute_pair[1]
            if spanish_name in other_models:
                instances = other_models[spanish_name]
                form_attribute = self.__getattribute__(english_name)
                form_attribute.choices = [(instance.name, instance.name) for instance in instances]
                if form_attribute.data is not None and (form_attribute.data, form_attribute.data) not in form_attribute.choices:
                    form_attribute.choices.append((form_attribute.data, form_attribute.data))

    def populate_question(self, question):
        self.number.data = question.number
        self.body.data = question.body
        self.context.data = question.context
        self.answer.data = question.answer
        if question.report:
            self.report.data = question.report.name
        if question.author:
            self.author.data = question.author.name
        if question.topic:
            self.topic.data = question.topic.name
        if question.subtopic:
            self.subtopic.data = question.subtopic.name

    def save_question(self, db_session):
        report_id = get_or_create(
            db_session, Report, name=self.report.data.strip().lower())
        author_id = get_or_create(
            db_session, Author, name=self.author.data.strip().lower())
        topic_id = get_or_create(
            db_session, Topic, name=self.topic.data.strip().lower())
        subtopic_id = get_or_create(
            db_session, SubTopic, name=self.subtopic.data.strip().lower())
        mytopic = Topic.query.get(topic_id)
        mysubtopic = SubTopic.query.get(subtopic_id)
        mytopic.subtopics.append(mysubtopic)

        question = Question(
            number=self.number.data,
            body=self.body.data.strip(),
            context=self.context.data.strip(),
            answer=self.answer.data.strip(),
            report_id=report_id,
            author_id=author_id,
            topic_id=topic_id,
            subtopic_id=subtopic_id
        )
        db_session.add(question)
        db_session.commit()
        return question

    def update_question(self, question, db_session):
        question.number = self.number.data
        question.body = self.body.data.strip()
        question.context = self.context.data.strip()
        question.answer = self.answer.data.strip()
        question.report_id = get_or_create(db_session, Report, name=self.report.data.strip().lower())
        question.author_id = get_or_create(db_session, Author, name=self.author.data.strip().lower())
        question.topic_id = get_or_create(db_session, Topic, name=self.topic.data.strip().lower())
        question.subtopic_id = get_or_create(db_session, SubTopic, name=self.subtopic.data.strip().lower())
        db_session.add(question)
        db_session.commit()

    def handle_create_request(self, db_session, searcher):
        self.update_choices(db_session, searcher)
        if self.validate_on_submit():
            question = self.save_question(db_session)
            searcher.restart_text_classifier()
            return redirect(url_for('see_question', question_id=question.id))
        return render_template('forms/single_question_form.html', form=self)

    def handle_edit_request(self, request, db_session, searcher, question_id):
        self.update_choices(db_session, searcher)
        question = searcher.get_question(question_id)
        if self.validate_on_submit():
            self.update_question(question, db_session)
            searcher.restart_text_classifier()
            return redirect(url_for('see_question', question_id=question.id))
        self.populate_question(question)
        standalone = request.args.get('standalone', False)
        return render_template('forms/single_question_form.html',
                               form=self, question=question, standalone=standalone)


class UploadForm(Form):
    spreadsheet = FileField(
        'spreadsheet',
        validators=[FileRequired(), FileAllowed(['xls', 'xlsx', 'csv'], 'Spreadsheets only (.xsl, .xslx, .csv)')]
    )
    question_type = SelectField(_('Question type'), choices=[
        ('informes', 'Informes'),
        ('taquigraficas', 'Taquigraficas')
    ])

    def save_spreadsheet(self):
        original_filename = self.spreadsheet.data.filename
        new_filename = str(int(time.time())) + '.' + original_filename.split('.')[-1]
        self.spreadsheet.data.save('app/uploads/' + new_filename)
        return new_filename

    def handle_request(self):
        if self.validate_on_submit():
            filename = self.save_spreadsheet()
            if self.data['question_type'] == 'informes':
                return redirect(url_for('process_spreadsheet', filename=filename))
            return redirect(url_for('process_spreadsheet_taquigraficas', filename=filename))
        return render_template('forms/question_upload_form.html', form=self)


class ProcessSpreadsheetForm(Form):
    type = 'informes'
    discard_first_row = BooleanField(_('First row is header'), default=True)
    number = SelectField(_('Question number'), [validators.DataRequired("Requerido")])
    body = SelectField(_('Question body'), [validators.DataRequired("Requerido")])
    question_date = SelectField(_('Question date'))
    answer = SelectField(_('Question answer'))
    answer_date = SelectField(_('Answer date'))
    context = SelectField(_('Question context'))
    report = SelectField(_('Report number'))
    author = SelectField(_('Question author'))
    topic = SelectField(_('Question topic'))
    subtopic = SelectField(_('Question subtopic'))

    form_template = 'forms/process_spreadsheet.html'

    def handle_request(self, filename, db_session, searcher):
        spreadsheet_summary = SpreadSheetReader.first_read(filename)
        self.update_choices(spreadsheet_summary['first_row'])
        if self.validate_on_submit():
            created_at = self.save_models(filename, db_session)
            searcher.restart_text_classifier()
            kwargs = {'creado-en': str(created_at)}
            return redirect(url_for('search', **kwargs))
        else:
            print(self.errors)
        return render_template(
            self.form_template,
            filename=filename,
            spreadsheet_summary=spreadsheet_summary,
            form=self
        )

    def update_choices(self, first_row):
        choices = [(str(i), first_row[i]) for i in range(len(first_row))]
        choices = [('', _('None'))] + choices
        self.number.choices = choices
        self.body.choices = choices
        self.answer.choices = choices
        self.context.choices = choices
        self.report.choices = choices
        self.author.choices = choices
        self.topic.choices = choices
        self.subtopic.choices = choices
        self.question_date.choices = choices
        self.answer_date.choices = choices

        return choices

    def save_models(self, filename, db_session):
        columns = self._collect_columns()
        extension = filename.split('.')[-1]
        file_path = 'app/uploads/' + filename

        if extension == 'csv':
            spreadsheet = SpreadSheetReader.read_csv(file_path)
        elif extension == 'xlsx':
            spreadsheet = SpreadSheetReader.read_xlsx(file_path)
        else:
            raise Exception('Formato no soportado')

        created_at = datetime.now().replace(microsecond=0)

        for i, row in spreadsheet:
            if i == 0 and self.discard_first_row.data:
                continue
            self.save_model(row, columns, db_session, created_at)
        db_session.commit()
        return created_at

    def save_model(self, row, columns, db_session, created_at):
        args = self.collect_args(row, columns)
        if len(args['report']) == 0:
            return
        args = self._get_ids(args, db_session)
        question = Question(**args)
        question.created_at = created_at
        db_session.add(question)

    def _collect_columns(self):
        columns = [
            (self.number.data, 'number'),
            (self.body.data, 'body'),
            (self.question_date.data, 'question_date'),
            (self.answer.data, 'answer'),
            (self.answer_date.data, 'answer_date'),
            (self.context.data, 'context'),
            (self.report.data, 'report'),
            (self.author.data, 'author'),
            (self.topic.data, 'topic'),
            (self.subtopic.data, 'subtopic')
        ]
        return [(int(tuple[0]), tuple[1]) for tuple in columns
                if len(tuple[0]) > 0]

    @staticmethod
    def _get_ids(question_args, db_session):
        if 'report' in question_args.keys():
            question_args['report_id'] = get_or_create(
                db_session, Report, name=question_args['report'])
        if 'author' in question_args.keys():
            question_args['author_id'] = get_or_create(
                db_session, Author, name=question_args['author'])
        if 'topic' in question_args.keys():
            question_args['topic_id'] = get_or_create(
                db_session, Topic, name=question_args['topic'])
        if 'subtopic' in question_args.keys():
            question_args['subtopic_id'] = get_or_create(
                db_session, SubTopic, name=question_args['subtopic'])
            mytopic = Topic.query.get(question_args['topic_id'])
            mysubtopic = SubTopic.query.get(question_args['subtopic_id'])
            mytopic.subtopics.append(mysubtopic)
            db_session.commit()
        if 'answer_author' in question_args.keys():
            question_args['answer_author_id'] = get_or_create(
                db_session, AnswerAuthor, name=question_args['author'])
        return question_args

    @staticmethod
    def collect_args(row, columns):
        d = {}
        for col in columns:
            position = col[0]
            if 0 <= position < len(row):
                value = row[col[0]].strip()
                if col[1] in ['author', 'report', 'topic', 'subtopic', 'answer_author']:
                    value = value.lower()
                if col[1] in ['question_date', 'answer_date']:
                    value = value.replace('-', '/')
                    value = value.replace(':', '/')
                    value = datetime.strptime(value, '%d/%m/%Y')
            else:
                value = ''
            d[col[1]] = value
        return d


class ProcessSpreadsheetTaquigraficasForm(ProcessSpreadsheetForm):
    type = 'taquigraficas'
    report = SelectField(_('Nombre de la comisión'))
    form_template = 'forms/process_spreadsheet_taquigraficas.html'
    answer_author = SelectField(_('Autor de la respuesta'))
    number = SelectField(_('Question number'), [validators.Optional()])
    topic = SelectField(_('Question topic'), [validators.Optional()])
    subtopic = SelectField(_('Question subtopic'), [validators.Optional()])

    def update_choices(self, first_row):
        choices = super(ProcessSpreadsheetTaquigraficasForm, self).update_choices(first_row)
        self.answer_author.choices = choices

    def _collect_columns(self):
        columns = [
            (self.report.data, 'report'),
            (self.context.data, 'context'),
            (self.body.data, 'body'),
            (self.question_date.data, 'question_date'),
            (self.answer.data, 'answer'),
            (self.answer_date.data, 'answer_date'),
            (self.author.data, 'author'),
            (self.answer_author.data, 'answer_author')
        ]
        return [(int(tuple[0]), tuple[1]) for tuple in columns
                if len(tuple[0]) > 0]

    def save_model(self, row, columns, db_session, created_at):
        args = self.collect_args(row, columns)
        if len(args['report']) == 0:
            return
        args = self._get_ids(args, db_session)
        max_number_for_that_comission = db_session.query(
            func.max(Question.number).label('max_number')
        ).filter_by(report_id=args['report_id']).one().max_number
        if max_number_for_that_comission is None:
            args['number'] = 1
        else:
            args['number'] = max_number_for_that_comission + 1
        question = Question(**args)
        question.created_at = created_at
        db_session.add(question)


class FullTextQueryForm(Form):
    main_text = TextAreaField(
        _('Base text to query'),
        [validators.Length(min=1, max=2000)]
    )

    def handle_request(self):
        if self.validate_on_submit():
            return redirect(url_for('search', q=self.main_text.data))
        return render_template('forms/full_text_query.html', form=self)
