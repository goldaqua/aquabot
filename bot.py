import configure
import telebot
from telebot import types # кнопки
from string import Template

bot = telebot.TeleBot(configure.config['token'])

user_dict = {}

tovary = {
    "Вода в баллоне 36 грн": 36,
    'Баллон с водой 170 грн': 170,
    'Трубочка для помпы (1 часть) 15 грн': 15,
    'Носик для помпы 25 грн': 25,
    'Помпа економ 80 грн': 80,
    'Помпа улучшенная 100 грн': 100,
    'Баллон + помпа економ + вода 230 грн': 230,
    'Баллон + помпа улучшенная + вода 250 грн': 250
}


class User:
    def __init__(self, city):
        self.city = city
        self.adres = None
        self.tovar = {}
        self.phone = None
        self.prim = None

    @property
    def summa(self):
        output = 0
        for k, v in self.tovar.items():
            output += tovary[k] * v
        return output


def kbs(buttons, one_time_keyboard=True, row_width=None):
    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=one_time_keyboard,
        row_width=row_width or len(buttons)//2
    )
    kb.add(*[types.KeyboardButton(i) for i in buttons])
    return kb


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup_menu = kbs(['О нас 🏢', 'Заказать 📝', 'Как стать клиентом Аквасвит 🙋‍♂️', 'Обратная связь 📞', 'График работы ⏰'])
    bot.send_message(message.chat.id, "Вас приветствует компания \"Аквасвит\"" + " 👋" + " "
    + message.from_user.first_name
    + ", выберите интересующий раздел.", reply_markup=markup_menu)


@bot.message_handler(content_types=["text"])
def user_reg(message):
    if message.text == 'Заказать 📝':
        markup = kbs(['Бахмут', 'Часов ЯР', 'Константиновка', 'Торецк (Дзержинск)'])
        msg = bot.send_message(message.chat.id, 'Выбирете город:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_city_step)
    elif message.text == 'О нас 🏢':
        bot.send_message(message.chat.id, "Наша компания \"Аквасвит\" уже 15 лет работает для своих клиентов. С каждым годом мы усовершенствоваемся и делаем все возможное для того," 
        + " чтобы каждому клиенту было удобно и приятно с нами работать.")
        bot.send_message(message.chat.id," Наша вода, прежде чем попоасть к вам в дом/офис проходит сложные этапы отчистки:" 
        	+"\n1. ✅ Механическая очистка пятью видами фильтров."
        	+"\n2. ✅Мультимедийная угольная колонна."
        	+"\n3. ✅Мультимедийная колонна."
        	+"\n4. ✅Фильтрация через мембраны с отверстиями в одну десятитысячную микрона."
        	+"\n5. ✅Минерализация с помощью электронных дозаторов."
        	+"\n6. ✅Постфильтры с углями из скорлупы кокосового ореха и цеолитого-шунгитовый с углем и серебром."
        	+"\n7. ✅Обработка ультрафиолетом.")
        bot.send_message(message.chat.id,"❗️ Поставщик воды по просьбе клиента обязан предоставить обязательный ежемесячный бактерицидный анализ воды.")
    elif message.text == 'Обратная связь 📞':
        bot.send_message(message.chat.id, "Мы находимся по адресу: Донецкая обл, г. Бахмут, ул. Юбилейная, 50 магазин \"Аквасвит\""
        + "\nНомера телефона Диспетчера: \n050-537-82-49 \n066-420-94-50 \n050-041-28-29 \n066-226-91-00 \n067-745-27-28 \n093-165-02-06")
    elif message.text == 'Как стать клиентом Аквасвит 🙋‍♂️':
        markup = kbs(['Заказать 📝', 'Вернутся в главное меню'])
        msg = bot.send_message(message.chat.id, 'Для того, чтобы стать клиентом компании Аквасвит, нужно приобрести комплект:'
        	+ '\nБаллон + помпа економ + вода 230 грн \nили \nБаллон + помпа улучшенная + вода 250 грн', reply_markup=markup)
    elif message.text == 'Вернутся в главное меню':
        send_welcome(message)
    elif message.text == 'Заказать 📝':
        user_reg(message)
    elif message.text == 'График работы ⏰':
        bot.send_message(message.chat.id, "График работы доставки: 🚚"
        	+"\n ПН-ПТ: 8:00-17:00"
        	+"\n СБ: 8:00-16:00"
        	+"\n ВС: Выходной")
def process_city_step(message):
    try:
        chat_id = message.chat.id
        user_dict[chat_id] = User(message.text)

        # удалить старую клавиатуру
        markup = types.ReplyKeyboardRemove(selective=False)

        msg = bot.send_message(chat_id, 'Введите адрес:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_adres)

    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def process_adres(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.adres = message.text

        return process_tovar(message)
    except Exception as e:
        bot.reply_to(message, 'ooops!!')


def process_tovar(message):
    user = user_dict[message.chat.id]
    available_items = list(tovary) + ['Оформить заказ ✅', 'Очистить корзину 🗑']
    chosen_items = []

    def inner(message):
        nonlocal chosen_items, available_items
        try:
            if message.text == 'Оформить заказ ✅':
                bot.send_message(message.chat.id, "Ваши вы выбрали:\n" + get_items_string(user.tovar, '\n'))
                msg = bot.send_message(message.chat.id, 'Введите ваш номер телефона в формате: 0ХХYYYYYYY')
                return bot.register_next_step_handler(msg, process_phone)
            elif message.text == 'Очистить корзину 🗑':
                bot.send_message(message.chat.id, 'Корзина очищена')
                return process_tovar(message)
            elif message.text in available_items:
                available_items.remove(message.text)
                chosen_items.append(message.text)
                bot.send_message(message.chat.id, 'Выберите кол-во товара', reply_markup=kbs(['1', '2', '3', '4']))
                return bot.register_next_step_handler(message, ask_number, message.text)
            else:
                raise ValueError
        except ValueError: # if item not in available items
            bot.send_message(message.chat.id, "Вводите только доступные товары")
            return bot.register_next_step_handler(message, inner)
        else:
            bot.register_next_step_handler(message, inner)

    def ask_number(message, item):
        nonlocal user
        try:
            amount = int(message.text)
        except ValueError:
            bot.send_message(message.text, 'Вводите только целые числа')
            return bot.register_next_step_handler(message, ask_number, item)
        else:
            user.tovar[item] = amount
            bot.send_message(message.chat.id, 'Выберите ещё товары', reply_markup=kbs(available_items, row_width=1))
            return bot.register_next_step_handler(message, inner)

    bot.send_message(
        message.chat.id,
        "Выберите покупки среди предложеных",
        reply_markup=kbs(available_items, row_width=1)
    )
    bot.register_next_step_handler(message, inner)


def process_phone(message):
    try:
        int(message.text)

        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.phone = message.text

        msg = bot.send_message(chat_id, 'Ведите примечание, если нет примечание напишите "нет"')
        bot.register_next_step_handler(msg, process_prim)
    except Exception as e:
        msg = bot.reply_to(message, 'Вы ввели что то другое. Пожалуйста введите номер телефона.')
        bot.register_next_step_handler(msg, process_phone)


def process_prim(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.prim = message.text

        if user.city == "Торецк (Дзержинск)" or user.city == "Константиновка":
        	bot.send_message(chat_id, getRegData(user, 'Ваша заявка', message.from_user.first_name), parse_mode="Markdown")
        	bot.send_message(message.chat.id, "Ваш заказ принят, ожидайте пожалуйста заказ будет выполнен в тичении 2-3 часов." + "\n По  г. Часов ЯР доставка осуществляется только по средам, во второй половине дня."
            	+ "\n В случии отмены или редактирование заказа просим вас обратится к диспетчеру тел. 050-537-82-49 \nC Ув. Аквасвит")
        	send_welcome(message)
        	# отправить в группу
        	bot.send_message(735422335, getRegData(user, 'Заявка от бота', bot.get_me().username), parse_mode="Markdown")        	
        else:
        # ваша заявка "Имя пользователя"
        	bot.send_message(chat_id, getRegData(user, 'Ваша заявка', message.from_user.first_name), parse_mode="Markdown")
        	bot.send_message(message.chat.id, "Ваш заказ принят, ожидайте пожалуйста заказ будет выполнен в тичении 2-3 часов." + "\n По  г. Часов ЯР доставка осуществляется только по средам, во второй половине дня."
            	+"\nПо г. Дзержинск (Торецк) доставка осуществляется по средам и субботам." 
            	+"\n В случии отмены или редактирование заказа просим вас обратится к диспетчеру тел. 050-537-82-49 \nC Ув. Аквасвит")
        	send_welcome(message)
        	# отправить в группу
        	bot.send_message(1413116688, getRegData(user, 'Заявка от бота', bot.get_me().username), parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, 'Что то пошло не так!')


def get_items_string(dct:dict, sep:str=', '):
    return sep.join([f"{k} ({v} шт.)" for k, v in dct.items()])


# формирует вид заявки регистрации
# нельзя делать перенос строки Template
# в send_message должно стоять parse_mode="Markdown"
def getRegData(user, title, name):
    t = Template('$title *$name* \n Город: *$userCity* \n Адресс: *$adres* \n Товар: *$tovar* \n Телефон: *$phone* \n Примечание: *$prim* \n К оплате курьеру: *$summa* грн.')

    return t.substitute({
        'title': title,
        'name': name,
        'userCity': user.city,
        'adres': user.adres,
        'tovar': get_items_string(user.tovar),
        'phone': user.phone,
        'prim': user.prim,
        'summa': user.summa,
    })

@bot.message_handler(content_types=["text"])   
def mine1(message):
    if message.text == 'Главное меню':
        bot.send_welcome(message)

@bot.message_handler(content_types=["text"])
def send_help(message):
    bot.send_message(message.chat.id, '/start')   
# произвольное фото
@bot.message_handler(content_types=["photo"])
def send_help_text(message):
    bot.send_message(message.chat.id, '/start')


bot.polling(none_stop=True)