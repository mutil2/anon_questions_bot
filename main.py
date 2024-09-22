import telebot
import json
import datetime as dt


def read_id_or_api_key(file_path):
    with open(file_path, 'r+') as f:
        key = f.readline().strip()
        assert key
        print(f'Got {file_path.split("/")[-1]}')
    return key


API_KEY = read_id_or_api_key('input/API_KEY')
TEACHER_ID = read_id_or_api_key('input/teacher_id')

BOT = telebot.TeleBot(API_KEY, parse_mode=None)


def read_file():
    with open('output/questions.json', 'r', encoding='utf-8') as f:
        try:
            data = json.loads(f.read())
            print('Content loaded from json')
        except json.JSONDecodeError:
            print('Questions file is empty, filling...')
            write_to_file({"number_of_questions": 0})
            data = read_file()

    return data


def write_to_file(data):
    with open('output/questions.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))
        print(f'Content written in json\n')


@BOT.message_handler(commands=['start', 'help'])
def send_welcome(command):
    text = """Привет, пиши сюда если у тебя появились вопросы ко мне. Не бойся, что я узнаю, кто ты. Ты останешься анонимным пока не скажешь, что это был ты."""

    print(f'Получена команда {command.text}')
    BOT.reply_to(command, text)


@BOT.message_handler(func=lambda message: True)
def get_question(message):
    if len(message.text) > 500:
        BOT.reply_to(message,
                     'Прости, сообщение слишком большое. Попробуй укоротить свой вопрос.')
        return

    answer = f"""Хорошо, твой вопрос: "{message.text}"
Успешно записан. Как смогу, отвечу на него."""

    print(f'\nGot new question: "{message.text}"')

    BOT.send_message(chat_id=TEACHER_ID, text=f'❗Новый вопрос, "{message.text}"')

    try:
        message.text.encode(encoding='utf-8')
    except UnicodeEncodeError:
        print('Сообщение не записано из-за проблем с кодировкой.')
        BOT.reply_to(message, 'Произошла ошибка, попробуй удалить спец. символы и смайлики')
        return

    file_data['number_of_questions'] += 1

    file_data[str(file_data['number_of_questions'])] = {
        'date': str(dt.datetime.now().date()),
        'time': str(dt.datetime.now().time())[:-10],
        'text': message.text
    }

    write_to_file(file_data)
    BOT.reply_to(message, answer)


if __name__ == '__main__':
    file_data = read_file()
    print('Бот начинает работу\n')
    BOT.infinity_polling(timeout=5)
