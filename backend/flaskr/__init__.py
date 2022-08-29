import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random
from models import setup_db, Question, Category, db
from extra import get_questions, random_question, QUESTIONS_PER_PAGE


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

    @app.route('/categories', methods=['GET'])
    def get_category():
        all_category = Category.query.all()
        category_array = {}
        for category in all_category:
            category_array[category.id] = category.type
        return jsonify({'categories': category_array})

    # endpoint to handle GET requests for questions, including pagination

    @app.route('/questions', methods=['GET'])
    def questions():
        page = request.args.get('page', 1, type=int)
        category_array = {}
        current_category_name = ''
        start = (page - 1) * 10
        end = start + 10
        questions = Question.query.all()
        all_category = Category.query.all()
        questions_count = Question.query.count()
        currant_category = \
            db.session.query(Question).order_by(Question.id.desc()).first()
        current_category_id = currant_category.category
        for category in all_category:
            category_array[category.id] = category.type
            if current_category_id == category.id:
                current_category_name = category.type
        return jsonify({
            'questions': get_questions(questions)[start:end],
            'total_questions': questions_count,
            'categories': category_array,
            'current_category': current_category_name,
            })

        # endpoint to POST a new question

    @app.route('/questions', methods=['POST'])
    def add_new_question():
        client_data = request.get_json()
        question = client_data['question']
        answer = client_data['answer']
        difficulty = client_data['difficulty']
        category = client_data['category']
        question_data = Question(question=question, answer=answer,
                                 difficulty=difficulty,
                                 category=category)
        db.session.add(question_data)
        db.session.commit()

        return jsonify({'success': True, 'message': 'New question added'
                       })

     # endpoint to get questions based on a search term

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json()
        search_term = data['searchTerm']
        category_array = []
        current_category_name = ''
        search_condition = '%{0}%'.format(search_term)
        search_question = \
            Question.query.filter(Question.question.ilike(search_condition)).all()
        category_list = Category.query.all()
        questions_count = \
            Question.query.filter(Question.question.ilike(search_condition)).count()
        currant_category = \
            db.session.query(Question).order_by(Question.id.desc()).first()
        current_cat_id = currant_category.category
        for x in category_list:
            category_array.append(x.type)
            if x.id == current_cat_id:
                current_category_name = x.type
        return jsonify({
            'questions': get_questions(search_question),
            'total_questions': questions_count,
            'categories': category_array,
            'current_category': current_category_name,
            })

    # GET endpoint to get questions based on category

    @app.route('/categories/<int:category_id>/questions', methods=['GET'
               ])
    def question_categories(category_id):

        category_array = {}
        current_category_name = ''
        questions = Question.query.filter(Question.category
                == category_id).all()
        all_category = Category.query.filter(Category.id
                == category_id).all()
        questions_count = Question.query.filter(Question.category
                == category_id).count()
        currant_category = \
            db.session.query(Question).order_by(Question.id.desc()).first()
        current_category_id = currant_category.category
        for category in all_category:
            category_array[category.id] = category.type
            if current_category_id == category.id:
                current_category_name = category.type
        return jsonify({'questions': get_questions(questions),
                       'total_questions': questions_count,
                       'current_category': current_category_name})

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

    # POST endpoint to get questions to play the quiz

    @app.route('/quizzes', methods=['POST'])
    def question_quiz():
        data = request.get_json()
        previous_questions = data['previous_questions']
        category = data['quiz_category']['id']
        if category == 0:
            question_data = Question.query.order_by(func.random()).all()
        else:
            question_data = Question.query.filter(Question.category
                    == category).order_by(func.random()).all()
        questions_count = Question.query.filter(Question.category
                == category).count()
        new_question = random_question(question_data,
                previous_questions, questions_count)

        return new_question

    # Error handler for 422

    @app.errorhandler(422)
    def unprocessable(error):
        return (jsonify({'success': False, 'error': 422,
                'message': 'unable to process the request'}), 422)

    # Errorhandler for 404

    @app.errorhandler(404)
    def not_found(error):
        return (jsonify({'success': False, 'error': 404,
                'message': 'The requested resource is not found in this server'
                }), 404)

    # Errorhandler for 405

    @app.errorhandler(405)
    def not_found(error):
        return (jsonify({'success': False, 'error': 405,
                'message': 'The requested Method is not allowed'}), 405)

    # Errorhandler for 400

    @app.errorhandler(400)
    def not_found(error):
        return (jsonify({'success': False, 'error': 400,
                'message': 'Bad input detected'}), 400)
    return app
