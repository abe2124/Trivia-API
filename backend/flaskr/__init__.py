
from http import client
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db
from extra import get_questions, random_question, QUESTIONS_PER_PAGE


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):

    # create and configure the app

    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)

    # CORS Headers

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE')
        return response

    # endpoint to handle GET requests for all available categories.
    @app.route('/categories')
    def get_categories():
        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {
                category.id: category.type for category in categories
            }
        })

     # endpoint to handle GET requests for questions, including pagination

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        page = paginate_questions(request, questions)

        categories = Category.query.order_by(Category.type).all()

        if len( page) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions':  page,
            'total_questions': len(questions),
            'categories': {
                category.id: category.type for category in categories
            },
            'current_category': None
        })
     # endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if not question:
                abort(422)
            question.delete()

            return jsonify({'success': True, 'deleted': question_id})
        except BaseException:
            abort(422)

        # endpoint to POST a new question

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        client_data = request.get_json()

        if not ('question' in client_data and 'answer' in client_data
                and 'difficulty' in client_data and 'category'
                in client_data):
            abort(422)

        question = client_data.get('question')
        answer = client_data.get('answer')
        difficulty = client_data.get('difficulty')
        category = client_data.get('category')

        try:
            question = Question(question=question, answer=answer,
                                difficulty=difficulty,
                                category=category)
            question.insert()

            return jsonify({'success': True, 'created': question.id})
        except BaseException:
            abort(422)

     # endpoint to get questions based on a search term

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        client_data = request.get_json()
        search_term = client_data.get('searchTerm', None)

        if search_term:
            search_results = \
                Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search_term))).all()
            questions = paginate_questions(request, search_results)

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(search_results),
                'current_category': None,
                })
        else:

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(current_questions),
                'current_category': None,
                })
        abort(404)

 # GET endpoint to get questions based on category

    @app.route('/categories/<int:category_id>/questions')
    def question_categories(category_id):
        try:

            questions = Question.query.filter(Question.category
                    == category_id).all()
            if len(questions) == 0:
                abort(404)
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category_id,
                })
        except BaseException:
            abort(404)

# POST endpoint to get questions to play the quiz

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        client_data = request.get_json()
        previous_questions = client_data.get('previous_questions')
        category = client_data.get('quiz_category')

        try:
            if category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category
                        == category['id']).all()

            len_questions = len(questions)

            random_question = random.choice(questions)

            if len(previous_questions) == len_questions:
                return jsonify({'success': True})
            else:

                return jsonify({'success': True,
                               'question': random_question.format()})
        except:
            abort(400)

    # Create error handlers for all expected errors

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': 'resource not found'}), 404)

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unprocessable'}), 422)

    @app.errorhandler(400)
    def bad_request(error):
        return (jsonify({'success': False, 'error': 400,
                'message': 'bad request'}), 400)

    @app.errorhandler(405)
    def not_allowed(error):
        return (jsonify({'success': False, 'error': 405,
                'message': 'method not allowed'}), 405)

    return app
