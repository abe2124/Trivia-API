
from flask import jsonify

QUESTIONS_PER_PAGE = 10


# get questions format

def get_questions(question):
    question_list = []
    for questions in question:
        question_list.append({
            'id': questions.id,
            'question': questions.question,
            'answer': questions.answer,
            'difficulty': questions.difficulty,
            'category': questions.category,
            })
    return question_list


# selects one random question

def random_question(question_array, view_questions, questions_count):
    for new_questions in question_array:
        if str(new_questions.id) not in view_questions:
            id = (new_questions.id, )
            question = (new_questions.question, )
            answer = (new_questions.answer, )
            difficulty = (new_questions.difficulty, )
            category = new_questions.category
            return jsonify({'question': {
                'id': str(id[0]),
                'question': question[0],
                'answer': answer[0],
                'difficulty': difficulty[0],
                'category': category,
                }, 'total_questions': questions_count})
    return jsonify({'no_value': True})
