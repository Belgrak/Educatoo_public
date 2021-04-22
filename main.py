from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from data import db_session
from data.books import Books
from data.users import User
from data.time import Time

from parse import parse_about_skill, parse_citaty, parse_pritchi
from setts import TOKEN, MAIL_PASS

import smtplib
import requests
import random
from google_trans_new import google_translator


# =============================== USING  API =======================================================================


def numbersapi():
    url = "https://numbersapi.p.rapidapi.com/random/" + random.choice(["trivia", "math", "date", "year"])
    querystring = {"json": "true", "fragment": "true", "max": "2021", "min": "1"}
    headers = {
        'x-rapidapi-key': "a1c52d6b67msh815efd661f5d519p15c571jsnadaadcb3d1b2",
        'x-rapidapi-host': "numbersapi.p.rapidapi.com"
    }
    res = requests.request("GET", url, headers=headers, params=querystring).json()
    tr = google_translator()
    return res['number'], tr.translate(res['text'], lang_tgt='ru'), res['text']


def get_fact(update, context):
    try:
        num, fact, fact_orig = numbersapi()
        update.message.reply_text('Вы знали, что... {}\n{}\n{}'.format(num, fact, fact_orig))
    except Exception:
        error_message(update, context)


# =============================== USING  API =======================================================================

# EMAIL ------------------------------------------------------------------------------------------------


def send_mail(theme, msg):
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        smtpObj.login('educatoo@inbox.ru', MAIL_PASS)
        message = """Subject: {}
        \n
        {}""".format(theme, msg)
        smtpObj.sendmail("educatoo@inbox.ru", "educatoo@inbox.ru", message.encode('utf-8'))
        smtpObj.quit()
        return True
    except Exception:
        return False


# EMAIL ------------------------------------------------------------------------------------------------


# All KeyBoards -------------------------------------------------------------------------------------------

main_keyboard = [['Мои книги', 'Получить навык', 'Цитата'], ['Притча', 'Обратная связь', 'Факт о числе'],
                 ['Метод Pomodoro']]
main_markup = ReplyKeyboardMarkup(main_keyboard, one_time_keyboard=False)

library_keyboard = [['Добавить книгу', 'Посмотреть книги', 'Удалить книгу'],
                    ['Меню']]
library_markup = ReplyKeyboardMarkup(library_keyboard, one_time_keyboard=False)

response_keyboard = [['Написать отзыв', 'Написать пожелание', 'Написать жалобу'],
                     ['Меню']]
response_markup = ReplyKeyboardMarkup(response_keyboard, one_time_keyboard=False)

stop_keyboard = [['Остановить', 'Меню']]
stop_markup = ReplyKeyboardMarkup(stop_keyboard, one_time_keyboard=False)

just_menu_keyboard = [['Меню']]
just_menu_markup = ReplyKeyboardMarkup(just_menu_keyboard, one_time_keyboard=False)


# ----------------------------------------------------------------------------------------------------------

# Unknown message -----------------------------------------------------------------------------------------------------


def unknown_message(update, context):
    update.message.reply_text('Извините, я не совсем понял Вас...',
                              reply_markup=main_markup)


# ------------------------------------------------------------------------------------------------------------------

# Error message -----------------------------------------------------------------------------------------------------


def error_message(update, context):
    update.message.reply_text('Упс... Возникла ошибка'
                              '\nПопробуйте позже...',
                              reply_markup=main_markup)


# --------------------------------------------------------------------------------------------------------------------

# Returns user to main menu -----------------------------------------------------------------------------------------


def back_to_menu(update, context):
    update.message.reply_text('Вы вернулись в меню',
                              reply_markup=main_markup)


# --------------------------------------------------------------------------------------------------------------------

# Adding to DataBase


def start(update, context):
    try:
        db_ses = db_session.create_session()
        user = User()
        user.id = update.effective_user.id
        user.username = update.effective_user.username
        user.first_name = update.effective_user.first_name
        if not db_ses.query(User).filter(User.id == user.id).all():
            db_ses.add(user)
        db_ses.commit()
        update.message.reply_text('Приветствую, ' + update.effective_user.first_name + '. Я - бот, который поможет '
                                                                                       'Вам усовершенствоваться в '
                                                                                       'духовном развитии, '
                                                                                       'самоорганизации. Поверьте, '
                                                                                       'это очень сильно поможет '
                                                                                       'в жизни',
                                  reply_markup=main_markup)
    except Exception:
        error_message(update, context)


# Showing All User Books


def library(update, context):
    try:
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
        if db_ses.query(Books).filter(Books.user == user).all():
            update.message.reply_text('Ваши книги:', reply_markup=library_markup)
            for n, i in enumerate(db_ses.query(Books).filter(Books.user == user)):
                update.message.reply_text(str(n + 1) + ' ' + i.title, reply_markup=library_markup)
        else:
            name = user.first_name
            update.message.reply_text(name + ', ' + 'У Вас пока нет книг...', reply_markup=library_markup)
    except Exception:
        error_message(update, context)
        return ConversationHandler.END
    return 1


# Library commands


def library_commands(update, context):
    try:
        if update.message.text == 'Добавить книгу':
            update.message.reply_text('Пожалуйста введите название книги',
                                      reply_markup=just_menu_markup)
            return 2
        elif update.message.text == 'Посмотреть книги':
            db_ses = db_session.create_session()
            user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
            if db_ses.query(Books).filter(Books.user == user).all():
                update.message.reply_text('Ваши книги:', reply_markup=library_markup)
                for n, i in enumerate(db_ses.query(Books).filter(Books.user == user)):
                    update.message.reply_text(str(n + 1) + ' ' + i.title, reply_markup=library_markup)
            else:
                name = user.first_name
                update.message.reply_text(name + ', ' + 'У Вас пока нет книг...', reply_markup=library_markup)
            return 1
        elif update.message.text == 'Удалить книгу':
            db_ses = db_session.create_session()
            user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
            if user.books:
                message = '\n'.join(str(t.id) + ' ' + t.title for t in user.books)
                update.message.reply_text(message,
                                          reply_markup=ReplyKeyboardMarkup(
                                              [[i for i in range(1, len(list(user.books)) // 2 + 1)],
                                               [i for i in
                                                range(len(list(user.books)) // 2 + 1, len(list(user.books)) + 1)],
                                               ['Меню']], one_time_keyboard=False))
                return 3
            else:
                name = user.first_name
                update.message.reply_text(name + ', ' + 'У Вас пока нет книг...', reply_markup=library_markup)
                return 1
        elif update.message.text == 'Меню':
            back_to_menu(update, context)
            return ConversationHandler.END
        else:
            unknown_message(update, context)
            return ConversationHandler.END
    except Exception:
        error_message(update, context)
        return ConversationHandler.END


# Adding books


def add_book(update, context):
    try:
        if update.message.text == 'Меню':
            back_to_menu(update, context)
            return ConversationHandler.END
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
        book = Books()
        book.title = update.message.text
        if book.title not in [i.title for i in user.books]:
            user.books.append(book)
            db_ses.commit()
            update.message.reply_text('Книга успешно добавлена', reply_markup=library_markup)
            return 1
        else:
            update.message.reply_text('У Вас уже есть эта книга', reply_markup=library_markup)
            return 1
    except Exception:
        error_message(update, context)
        return ConversationHandler.END


# Deleting Books


def delete_book(update, context):
    try:
        if update.message.text == 'Меню':
            back_to_menu(update, context)
            return ConversationHandler.END
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == update.effective_user.id).first()
        book = user.books[int(update.message.text) - 1]
        db_ses.delete(book)
        db_ses.commit()
        update.message.reply_text('Книга успешно удалена', reply_markup=library_markup)
        return 1
    except Exception:
        error_message(update, context)
        return ConversationHandler.END


# ====================================================================================================================

# ==================================================GETSKILL===========================================================


def get_skill(update, context):
    message = '\n'.join([''.join(i.strip().split('Источник информации')) for i in parse_about_skill()])
    try:
        update.message.reply_text(message,
                                  reply_markup=main_markup)
    except Exception:
        for i in parse_about_skill():
            update.message.reply_text(''.join(i.strip().split('Источник информации')))
    update.message.reply_text('Навык был взят с ресурса WikiHow',
                              reply_markup=main_markup)


# ====================================================================================================================

# ==================================================GETCITATY==========================================================


def get_citaty(update, context):
    try:
        update.message.reply_text(parse_citaty())
        update.message.reply_text('Цитата была взята с ресурса Citaty.info',
                                  reply_markup=main_markup)
    except Exception:
        error_message(update, context)


# ====================================================================================================================

# ==================================================GETPritcha==========================================================


def get_pritcha(update, context):
    try:
        update.message.reply_text(parse_pritchi())
        update.message.reply_text('Притча была взята с ресурса pritchi.ru',
                                  reply_markup=main_markup)
    except Exception:
        error_message(update, context)


# ====================================================================================================================

# Response and Feedback functions

def response(update, context):
    update.message.reply_text('Мы очень рады, что Вы активно участвуете в развитии проекта.'
                              'Выберите необходимый раздел', reply_markup=response_markup)
    return 1


# Response commands


def response_commands(update, context):
    if update.message.text == 'Написать отзыв':
        update.message.reply_text('Пожалуйста напишите отзыв',
                                  reply_markup=just_menu_markup)
        return 2
    elif update.message.text == 'Написать пожелание':
        update.message.reply_text('Пожалуйста напишите пожелание',
                                  reply_markup=just_menu_markup)
        return 3
    elif update.message.text == 'Написать жалобу':
        update.message.reply_text('Мы будем рады исправить сбой в программе.'
                                  'Пожалуйста опишите Вашу жалобу',
                                  reply_markup=just_menu_markup)
        return 4
    elif update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    else:
        unknown_message(update, context)
        return ConversationHandler.END


# Send Feedback


def feedback(update, context):
    if update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    flag = send_mail('Отзыв', update.message.text)
    if flag:
        update.message.reply_text('Спасибо за отзыв!', reply_markup=main_markup)
    else:
        error_message(update, context)
    return ConversationHandler.END


# Send Wishes


def wishes(update, context):
    if update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    flag = send_mail('Пожелания', update.message.text)
    if flag:
        update.message.reply_text('Спасибо за пожелания!', reply_markup=main_markup)
    else:
        error_message(update, context)
    return ConversationHandler.END


# Send a complaint


def complaint(update, context):
    if update.message.text == 'Меню':
        back_to_menu(update, context)
        return ConversationHandler.END
    flag = send_mail('Жалоба', update.message.text)
    if flag:
        update.message.reply_text('Мы постараемся рассмотреть вашу жалобу в ближайшее время', reply_markup=main_markup)
    else:
        error_message(update, context)
    return ConversationHandler.END


# ==================================== POMODORO =====================================================================
def time_commands(update, context):
    update.message.reply_text('Тайм-менеджмент невероятно помогает человеку в организации своего времени\n'
                              '    В методе Pomodoro устанавливается таймер на 25 минут. Человек в течение времени '
                              'выполняет задачи, а затем отдыхает 5 минут. После 4 задач активируется пауза в '
                              '30 минут\n'
                              'Для завершения остановите таймер')
    update.message.reply_text('Приготовьтесь к выполнению задач',
                              reply_markup=just_menu_markup)
    chat_id = update.message.chat_id
    try:
        db_ses = db_session.create_session()
        time = db_ses.query(Time).filter(Time.chat_id == chat_id).first()
        if time:
            time.count = 0
        db_ses.commit()
    except Exception:
        error_message(update, context)
    pomodoro(chat_id, context)
    return 1


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def pomodoro(chat_id, context, work=True, count=0):
    """Добавляем задачу в очередь"""
    try:
        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        if not current_jobs:
            db_ses = db_session.create_session()
            time = db_ses.query(Time).filter(Time.chat_id == chat_id).first()
            if not time:
                t = Time()
                t.chat_id = chat_id
                t.count = 0
                db_ses.add(t)
                db_ses.commit()
            db_ses = db_session.create_session()
            time = db_ses.query(Time).filter(Time.chat_id == chat_id).first()
            remove_job_if_exists(
                str(chat_id),
                context
            )
            if work:
                time.count += 1
                due = 60 * 25
                context.job_queue.run_once(
                    task_work,
                    due,
                    context=chat_id,
                    name=str(chat_id)
                )
                text = f'Отсчет {due // 60} минут пошел. Продуктивной работы!'
            else:
                due = 60 * 5
                if time.count == 4:
                    due = 30 * 60
                    time.count = 0
                context.job_queue.run_once(
                    task_rest,
                    due,
                    context=chat_id,
                    name=str(chat_id)
                )
                text = f'Отсчет {due // 60} минут пошел. Хорошего отдыха!'
            # Присылаем сообщение о том, что всё получилось.
            context.bot.send_message(chat_id, text, reply_markup=stop_markup)
            db_ses.commit()
        else:
            context.bot.send_message(chat_id, 'Таймер уже запущен', reply_markup=stop_markup)
    except Exception:
        context.bot.send_message(chat_id, 'Упс... Ошибочка', reply_markup=main_markup)
        return ConversationHandler.END


def task_rest(context):
    job = context.job
    context.bot.send_message(job.context, text='Отдых окончен!')
    pomodoro(job.context, context, True)
    return 1


def task_work(context):
    job = context.job
    context.bot.send_message(job.context, text='Поработали и хватит!')
    pomodoro(job.context, context, False)
    return 1


def unset_timer(update, context):
    if update.message.text == 'Остановить':
        chat_id = update.message.chat_id
        remove_job_if_exists(str(chat_id), context)
        text = 'Хорошая работа!'
        update.message.reply_text(text, reply_markup=main_markup)
        return ConversationHandler.END
    elif update.message.text == 'Меню':
        back_to_menu(update, context)
    else:
        if update.message.text == 'Метод Pomodoro':
            fallback_pomodoro(update, context)
        else:
            unknown_message(update, context)


def fallback_pomodoro(update, context):
    update.message.reply_text('Таймер уже запущен', reply_markup=stop_markup)
    return ConversationHandler.END


# ==================================== POMODORO =====================================================================


def main():
    db_session.global_init('db/main.db')
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.text('Получить навык'), get_skill))
    dp.add_handler(MessageHandler(Filters.text('Цитата'), get_citaty))
    dp.add_handler(MessageHandler(Filters.text('Притча'), get_pritcha))
    dp.add_handler(MessageHandler(Filters.text('Факт о числе'), get_fact))
    books_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Мои книги'), library)],
        states={
            1: [MessageHandler(Filters.text, library_commands)],
            2: [MessageHandler(Filters.text, add_book)],
            3: [MessageHandler(Filters.text, delete_book)]
        },

        fallbacks=[MessageHandler(Filters.text, unknown_message)]
    )
    dp.add_handler(books_handler)
    response_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Обратная связь'), response)],
        states={
            1: [MessageHandler(Filters.text, response_commands)],
            2: [MessageHandler(Filters.text, feedback)],
            3: [MessageHandler(Filters.text, wishes)],
            4: [MessageHandler(Filters.text, complaint)]
        },

        fallbacks=[MessageHandler(Filters.text, unknown_message)]
    )
    dp.add_handler(response_handler)
    timer_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Метод Pomodoro'), time_commands,
                                     pass_job_queue=True, pass_chat_data=True)],
        states={
            1: [MessageHandler(Filters.text, unset_timer, pass_job_queue=True, pass_chat_data=True)]
        },

        fallbacks=[MessageHandler(Filters.text, fallback_pomodoro)]
    )
    dp.add_handler(timer_handler)
    dp.add_handler(MessageHandler(Filters.text, unknown_message))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
