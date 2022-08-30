
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

            # create all tables

            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""

        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_405_delete_categories_not_allowed(self):
        res = self.client().delete('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'The requested Method is not allowed')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

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
        self.assertEqual(data['message'], 'New question added')

    def test_405_if_add_new_question_not_allowed(self):
        res = self.client().post('/questions/55', json={
            'question': 'test',
            'answer': 'test',
            'difficulty': 4,
            'category': 3,
            })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'The requested Method is not allowed')

    def test_get_question_by_category(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data), 4)

    def test_get_question_by_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data), 4)

    def test_search_questions_by_category_not_found(self):
        res = self.client().get('categories/first/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],
                         'The requested resource is not found in this server'
                         )

    def test_405_if_questions_does_not_exist(self):
        res = self.client().delete('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        res = self.client().post('/questions/search',
                                 json={'searchTerm': 'searchTerm'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data), 4)


# Make the tests conveniently executable

if __name__ == '__main__':
    unittest.main()
