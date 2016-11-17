#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, jsonify, request
from flask_user import login_required
from forms import QuestionForm, UploadForm, ProcessSpreadsheetForm, FullTextQueryForm
from models import Question


def init_routes(app, db_session, searcher):
    @app.route('/')
    @login_required
    def home_page():
        return render_template('home.html')

    @app.route('/carga_de_preguntas', methods=['GET', 'POST'])
    @login_required
    def question_upload():
        upload_form = UploadForm()
        return upload_form.handle_request()

    @app.route('/carga_de_preguntas/manual', methods=['GET', 'POST'])
    @login_required
    def single_question():
        single_question_form = QuestionForm()
        return single_question_form.handle_create_request(db_session, searcher)

    @app.route('/carga_de_preguntas/procesar_planilla/<filename>', methods=['GET', 'POST'])
    @login_required
    def process_spreadsheet(filename):
        process_spreadsheet_form = ProcessSpreadsheetForm()
        return process_spreadsheet_form.handle_request(filename, db_session, searcher)

    @app.route('/busqueda_por_similaridad', methods=['GET', 'POST'])
    @login_required
    def full_text_query():
        full_text_query_form = FullTextQueryForm()
        return full_text_query_form.handle_request()

    @app.route('/buscar', methods=['GET', 'POST'])
    @login_required
    def search():
        query = searcher.query_from_url()
        result = searcher.search_from_url()
        other_models = searcher.list_models()
        return render_template('search/results.html', results=result,
                               query=query, url_maker=searcher.url_maker, other_models=other_models)

    @app.route('/buscar', methods=['DELETE'])
    @login_required
    def delete_all():
        searcher.delete_results_from_url(db_session)
        return jsonify({'success': True})

    @app.route('/pregunta/<int:question_id>.json')
    @login_required
    def see_question_json(question_id):
        question = searcher.get_question(question_id)
        return jsonify(question)

    @app.route('/pregunta/<int:question_id>')
    @login_required
    def see_question(question_id):
        question = searcher.get_question(question_id)
        similar_results = searcher.get_similar_to(question_id)
        return render_template('question.html', question=question, similar_results=similar_results,
                               url_maker=searcher.url_maker)

    @app.route('/pregunta/<int:question_id>/editar', methods=['GET', 'POST'])
    @login_required
    def edit_question(question_id):
        single_question_form = QuestionForm()
        return single_question_form.handle_edit_request(request, db_session, searcher, question_id)

    @app.route('/pregunta/<int:question_id>/borrar', methods=['POST'])
    @login_required
    def delete_question(question_id):
        Question.delete(question_id, db_session)
        searcher.restart_text_classifier()
        return jsonify({'success': True})

    @app.route('/pregunta/<int:question_id>/sugerir_tema', methods=['GET'])
    @login_required
    def suggest_topic(question_id):
        tags = searcher.suggest_tags("topics", question_id)
        return jsonify(tags)

    @app.route('/pregunta/<int:question_id>/sugerir_subtema', methods=['GET'])
    @login_required
    def suggest_subtopic(question_id):
        tags = searcher.suggest_tags("subtopics", question_id)
        return jsonify(tags)

    @app.route('/pregunta/<int:question_id>/actualizar', methods=['POST'])
    @login_required
    def update_question(question_id):
        result = Question.update(question_id, db_session, request.values)
        return render_template('/search/result.html', result=result, best_words=False)
