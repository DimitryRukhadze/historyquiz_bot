import random
import functools

from environs import Env
from enum import Enum, auto

import redis

from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    RegexHandler,
    Filters
)

from question_file_utils import get_questions_from_file, question_filepath


class States(Enum):
    NEW_QUESTION = auto()
    ATTEMPT_INPUT = auto()
    NEW_CYCLE = auto()


def start(bot, update):
    buttons = ['Начнём!']
    reply_keyboard = [buttons]
    keyboard_markup = ReplyKeyboardMarkup(reply_keyboard)
    bot.send_message(chat_id=update.effective_chat.id, text=question_filepath, reply_markup=keyboard_markup)

    return States.NEW_QUESTION

def new_question_request(bot, update, connection='', questions_from_file=''):
    curr_user_id = update.effective_chat.id
    buttons = ['Новый вопрос', 'Мой Счёт']
    reply_keyboard = [buttons]
    keyboard_markup = ReplyKeyboardMarkup(reply_keyboard)
    questions = list(questions_from_file.keys())
    question_for_user = questions[random.randint(0, len(questions))]
    connection.set(curr_user_id, question_for_user)
    bot.send_message(chat_id=curr_user_id, text=question_for_user)
    bot.send_message(
        chat_id=curr_user_id,
        text='Напиши ответ или выбери вариант на клавиатуре',
        reply_markup=keyboard_markup
    )

    return States.ATTEMPT_INPUT

def handle_input_attempt(bot, update, connection='', questions_from_file=''):
    curr_user_id = update.effective_chat.id
    buttons = ['Новый вопрос', 'Сдаться', 'Мой Счёт']
    reply_keyboard = [buttons[0:2], buttons[-1:]]
    keyboard_markup = ReplyKeyboardMarkup(reply_keyboard)
    bot.send_message(chat_id=curr_user_id, text='Выбери вариант', reply_markup=keyboard_markup)
    curr_question = connection.get(curr_user_id)
    correct_answer = questions_from_file[curr_question]

    if update.message.text not in correct_answer.rstrip('.'):
        bot.send_message(chat_id=curr_user_id, text='Это не верно! Попробуйте ещё.')
        return States.ATTEMPT_INPUT
    bot.send_message(chat_id=curr_user_id, text='Это верно!')
    return States.NEW_QUESTION

def give_up(bot, update, connection='', questions_from_file=''):
    curr_user_id = update.effective_chat.id
    curr_question = connection.get(curr_user_id)
    correct_answer = questions_from_file[curr_question]
    bot.send_message(chat_id=curr_user_id, text=f'Вот правильный ответ:\n{correct_answer}')
    buttons = ['Новый вопрос', 'Мой Счёт']
    reply_keyboard = [buttons]
    keyboard_markup = ReplyKeyboardMarkup(reply_keyboard)
    bot.send_message(chat_id=curr_user_id, text='Выбери вариант', reply_markup=keyboard_markup)

def main():
    env = Env()
    env.read_env()
    redis_host = env('REDIS_HOST')
    redis_port = env('REDIS_PORT')
    redis_password = env('REDIS_PASSWORD')
    redis_username = env('REDIS_USERNAME')
    db_connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        username=redis_username,
        password=redis_password,
        decode_responses=True
    )

    questions_from_file = get_questions_from_file(question_filepath)

    new_question_request_with_connection = functools.partial(
        new_question_request,
        connection=db_connection,
        questions_from_file=questions_from_file
    )
    handle_input_attempt_with_connection = functools.partial(
        handle_input_attempt,
        connection=db_connection,
        questions_from_file=questions_from_file
    )
    give_up_with_connection = functools.partial(
        give_up,
        connection=db_connection,
        questions_from_file=questions_from_file
    )

    updater = Updater(env('TELEGA_TOKEN'))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            States.NEW_QUESTION: [
                RegexHandler('^Начнём|Новый вопрос$', new_question_request_with_connection),
            ],
            States.ATTEMPT_INPUT: [
                RegexHandler('^Новый вопрос$', new_question_request_with_connection),
                RegexHandler('^Сдаться$', give_up_with_connection),
                MessageHandler(Filters.text, handle_input_attempt_with_connection)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
