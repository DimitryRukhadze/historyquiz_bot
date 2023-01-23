import os
import json


def parse_questions_file():
    question_dir = 'questions'
    question_files = os.listdir(question_dir)

    with open(os.path.join(question_dir, question_files[0]), 'r', encoding='koi8-r') as file:
        questions = file.read()

    quest = questions.split('\n\n')

    questions_with_answers = {
        quest[i]:quest[i+1]
        for i in range(0, len(quest))
        if 'Вопрос' in quest[i]
    }

    return questions_with_answers

def make_questions_json():

    questions = parse_questions_file()
    with open('questions.json', 'w') as file:
        questions_json = json.dumps(questions, ensure_ascii=False)
        file.write(questions_json)


if __name__ == '__main__':
    make_questions_json()
