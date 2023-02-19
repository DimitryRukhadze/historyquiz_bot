import random
import os

from environs import Env

import vk_api
import redis

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard

from question_file_utils import get_questions_from_file, question_filepath


def send_message(event, vk_api, text):

    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')
    keyboard.add_line()
    keyboard.add_button('Мой Счёт')

    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        random_id=random.randint(1, 1000),
        keyboard=keyboard.get_keyboard()
    )

def main():
    env = Env()
    env.read_env()

    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')
    redis_username = env('REDIS_USERNAME')
    vk_token = env('VK_API_KEY')

    db_connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_username,
        password=redis_password,
        decode_responses=True
    )
    vk_session = vk_api.VkApi(token=vk_token)
    vk_curr_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    questions_with_answers = get_questions_from_file(question_filepath)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                questions = list(questions_with_answers.keys())
                question_for_user = questions[
                    random.randint(0, len(questions))
                ]
                db_connection.set(event.user_id, question_for_user)
                send_message(event, vk_curr_api, question_for_user)
            else:
                curr_question = db_connection.get(event.user_id)
                if not curr_question:
                    send_message(event, vk_curr_api, 'Нажмите кнопку "Новый вопрос"')
                else:
                    correct_answer = questions_with_answers[curr_question]
                    if event.text == 'Сдаться':
                        send_message(event, vk_curr_api, correct_answer)
                    elif event.text in correct_answer.rstrip('.'):
                        send_message(event, vk_curr_api, 'Верно!')
                    else:
                        send_message(event, vk_curr_api, 'Неверно! Попробуйте ещё')


if __name__ == '__main__':
    main()
