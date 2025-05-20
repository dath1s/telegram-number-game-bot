import telebot as tb
from db_funcs import *
import random
from math import ceil

bot = tb.TeleBot('token')

action_keyboard = tb.types.ReplyKeyboardMarkup()
action_keyboard.row(tb.types.KeyboardButton("Готов"))


@bot.message_handler(commands=['start', 'restart'])
def welcome(message):
    create_database()
    bot.send_message(
        message.from_user.id,
        'Здаравствуй, игрок!\n\nПредлагаю сыграть тебе в интереснейшую игру с неменее интереснейшим призом.\n\n<b>Правила игры:</b>\n\t1) Игра начинается с 0 очков\n\t2) На каждом ходу, мы по очереди выбираем числа от 1 до 10 и прибавляем к итоговому счету\n\t3) Первый кто доберется к счету больше либо равному 100 побеждает.\n\n<b>Готов?</b>',
        parse_mode='html',
        reply_markup=action_keyboard
    )
    bot.register_next_step_handler(message, start_game)


def start_game(mes):
    user_id = int(mes.chat.id)
    reset_or_create_user(user_id)

    x = random.randint(1, 10)

    bot.send_message(
        user_id,
        f'Я начну\n\n<b>{x}</b>',
        parse_mode='html'
    )
    update_total_score(user_id, x)
    bot.register_next_step_handler(mes, mid_part)


def mid_part(mes):
    user_id = int(mes.chat.id)

    try:
        user_input = mes.text.strip()
        if not user_input.isdigit():
            raise ValueError("Введено не число")

        num = int(user_input)
        if not (1 <= num <= 10):
            bot.send_message(user_id, "Число должно быть от 1 до 10.")
            bot.register_next_step_handler(mes, mid_part)
            return

        update_total_score(user_id, num)
        current_score = get_current_score(user_id)

        bot.send_message(
            user_id,
            f"Текущий итоговый счет: <b>{current_score}</b>",
            parse_mode='html'
        )

        if current_score >= 100:
            bot.send_message(user_id, "🎉 Ты победил!")
            reset_or_create_user(user_id)
            return

        if current_score > 60:
            x = min(ceil(current_score / 11) * 11 + 1 - current_score, 10)
            if x < 1 or x > 10:
                x = random.randint(1, 10)
        else:
            x = random.randint(1, 10)

        update_total_score(user_id, x)
        current_score = get_current_score(user_id)

        bot.send_message(user_id, f"Мой ход: <b>{x}</b>", parse_mode='html')
        bot.send_message(
            user_id,
            f"Текущий итоговый счет: <b>{current_score}</b>",
            parse_mode='html'
        )

        # Проверка на победу бота
        if current_score >= 100:
            bot.send_message(
                user_id,
                "😢 К сожалению, ты проиграл. Бот выиграл!\n"
                "Чтобы сыграть снова, напиши /start"
            )
            reset_or_create_user(user_id)
            return

        # Продолжаем игру
        bot.register_next_step_handler(mes, mid_part)

    except Exception as e:
        bot.send_message(
            user_id,
            "Скорее всего ты отправил что-то не то. Я принимаю только числа от 1 до 10!"
        )
        bot.register_next_step_handler(mes, mid_part)


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
    bot.polling(skip_pending=True)
