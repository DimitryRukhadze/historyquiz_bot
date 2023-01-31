import os
import json

from environs import Env


def parse_questions_file(question_dir):
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
    return questions_with_answers

def make_questions_json(questions):

    with open('questions.json', 'w') as file:
        questions_json = json.dumps(questions, ensure_ascii=False)
        file.write(questions_json)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    questions_dir = env('QUESTIONS_DIR')
    questions_raw = parse_questions_file(questions_dir)
    make_questions_json(questions_raw)
