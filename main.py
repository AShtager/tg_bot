import telebot
import random
import os
from telebot import types
from func import added_user, word_ru, translator, random_words, added_word, delete_word
from dotenv import load_dotenv
load_dotenv()

tg_token = os.getenv("TOKEN")
bot = telebot.TeleBot(tg_token)


class Command:
    ADD_WORD = "Добавить слово ➕"
    DELETE_WORD = "Удалить слово 🔙"
    NEXT = "Дальше ⏭"
    GO = "Let's GO!!!"


def guess_word(message):
        user_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        global word
        word = word_ru(user_id=user_id) 
        word_en = translator(word)
        button_word_en = types.KeyboardButton(word_en)
        msg = f"Выберите перевод слова {word}"
        random_word = [types.KeyboardButton(word) for word in random_words()]
        buttons = [button_word_en] + random_word
        random.shuffle(buttons)
        button_next = types.KeyboardButton(Command.NEXT)
        button_add = types.KeyboardButton(Command.ADD_WORD)
        button_del = types.KeyboardButton(Command.DELETE_WORD)
        markup.add(*buttons, button_next, button_add, button_del)
        bot.send_message(message.chat.id, msg, reply_markup=markup)
        return word_en

@bot.message_handler(commands=["start"])
def greeting(message):
    msg = (
    f"Привет!👋Давай попрактикуемся в английском языке.\n"
    f"Тренировки можешь проходить в удобном для себя темпе. У\n"
    f"тебя есть возможность использовать тренажёр, как\n"
    f"конструктор, и собирать свою собственную базу для обучения.\n"
    f"Для этого воспрользуйся инструментами:\n"
    f"• {Command.ADD_WORD}\n"
    f"• {Command.DELETE_WORD}\n"
    f"Уже нетерпится? Жми {Command.GO}"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_add = types.KeyboardButton(Command.ADD_WORD)
    button_del = types.KeyboardButton(Command.DELETE_WORD)
    button_go = types.KeyboardButton(Command.GO)
    markup.add(button_go, button_add, button_del)
    bot.send_message(message.chat.id, msg, reply_markup=markup)
    added_user(message.chat.id)

@bot.message_handler(func=lambda message: message.text == Command.GO or message.text == Command.NEXT)
def pick_word(message):
    global word_en
    word_en = guess_word(message)
    bot.register_next_step_handler(message, callback_user)

@bot.callback_query_handler(func=lambda message: True)
def callback_user(message):
    if message.text == word_en:
        bot.send_message(message.chat.id, "Верно!")
    elif message.text == Command.NEXT:
         pick_word(message)
    elif message.text == Command.ADD_WORD:
        request_word_add(message)
    elif message.text == Command.DELETE_WORD:
        request_word_del(message)
    else:
        bot.send_message(message.chat.id, f"Не верно! Попробуйте еще! Выберите перевод слова {word}")
        bot.register_next_step_handler(message, callback_user)
    
@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def request_word_add(message):
    bot.send_message(message.chat.id, f"Введите слово")
    bot.register_next_step_handler(message, added_user_word)
    
@bot.callback_query_handler(func=lambda message: True)
def added_user_word(message):
    added_word(id_user=message.chat.id, word=message.text)
    bot.send_message(message.chat.id, f"Слово {message.text} успешно добавлено")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_add = types.KeyboardButton(Command.ADD_WORD)
    button_del = types.KeyboardButton(Command.DELETE_WORD)
    button_go = types.KeyboardButton(Command.GO)
    markup.add(button_go, button_add, button_del)

@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def request_word_del(message):
    bot.send_message(message.chat.id, f"Введите слово которое хотите удалить")
    bot.register_next_step_handler(message,del_user_word)

@bot.callback_query_handler(func=lambda message: True)
def del_user_word(message):
    delete_word(id_user=message.chat.id, word=message.text)
    bot.send_message(message.chat.id, f"Слово {message.text} успешно удалено")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_add = types.KeyboardButton(Command.ADD_WORD)
    button_del = types.KeyboardButton(Command.DELETE_WORD)
    button_go = types.KeyboardButton(Command.GO)
    markup.add(button_go, button_add, button_del)


if __name__ == "__main__":
    print("Бот работает!")
    bot.polling(non_stop=True)