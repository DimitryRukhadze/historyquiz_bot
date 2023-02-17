import os
import json
import codecs

from environs import Env


question_filepath = os.path.join(os.getcwd(),'questions.json')

def parse_questions_file(question_dir, question_filename):
    question_filenames = os.listdir(question_dir)
    all_questions = []
    for filename in question_filenames:
        with open(
                os.path.join(question_dir, filename),
                'r',
                encoding='koi8-r'
        ) as file:
            questions = file.read()

        all_questions += (questions.split('\n\n'))

    questions_with_answers = {
        all_questions[i]:all_questions[i+1]
        for i in range(0, len(all_questions))
        if 'Вопрос' in all_questions[i]
    }
    with codecs.open(question_filename, 'w', 'utf-8') as file:
        questions_json = json.dumps(questions_with_answers, ensure_ascii=False)
        file.write(questions_json)

def get_questions_from_file(question_filepath):
    with open(question_filepath, 'r', encoding='utf-8') as file:
        questions_answers = file.read()
    questions_answers = json.loads(questions_answers)
    return questions_answers

def get_correct_answer(user_id, connection):
    curr_question = connection.get(user_id)
    questions_with_answers = get_questions_from_file(question_filepath)
    return questions_with_answers[curr_question]


if __name__ == '__main__':
    env = Env()
    env.read_env()

    questions_dir = env('QUESTIONS_DIR')
    questions_filename = env('QUESTION_FILE')
    questions_raw = parse_questions_file(questions_dir, questions_filename)
