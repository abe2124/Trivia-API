import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

class TriviaTestCase(unittest.TestCase):

    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = \
            'postgresql://postgres:123456@{}/{}'.format('localhost:5432'
                , self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context

        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)

            # create all tableswithout_results

            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""

        pass

    def test_get_valid_page(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertEqual(data['success'], True)

    def test_404_valid_page_failure(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_404_categories_resource_not_found(self):
        res = self.client().get('/categories/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_get_questions_failure(self):
        res = self.client().get('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_delete_question(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_delete_questions_failure(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_add_new_question(self):
        res = self.client().post('/questions', json={
            'question': 'test',
            'answer': 'test',
            'difficulty': 3,
            'category': 2,
            })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'], True)

    def test_405_add_new_question_not_allowed(self):
        res = self.client().post('/questions/50', json={
            'question': 'test',
            'answer': 'test',
            'difficulty': 4,
            'category': 3,
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_question_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data), 4)

    def test_search_questions_by_category_not_found(self):
        res = self.client().get('categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_search_questions(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'searchTerm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data), 4)

    def test_search_question_failure(self):
        res = self.client().post('/questions',
                                 json={'searchTerm': 'wwwwww'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_play_quizzes(self):
        res = self.client().post('/quizzes',
                                 json={'previous_questions': [1, 3],
                                 'quiz_category': {'type': 'Science',
                                 'id': '1'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 1)
        self.assertNotEqual(data['question']['id'], 3)

    def test_if_play_quiz_failure(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable

if __name__ == '__main__':
    unittest.main()
