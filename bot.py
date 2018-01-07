# -*- coding: utf-8 -*-
import telebot,constants
bot = telebot.TeleBot(constants.token)
#######################################

config = {
    'user': 'gb_x_testbe2a',
    'password': 'd4ea3f6zaui',
    'host': 'mysql93.1gb.ru',
    'database': 'gb_x_testbe2a',
    'raise_on_warnings': True,
}

def readdb(table,column,compare,param,mode):
    try:
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        cur.execute("SELECT {} FROM {} WHERE {}= %s".format(column,table,compare), (param,))
        result = cur.fetchall()
        conn.close()
        if result == [] and mode == 'check':
            return (False)
        elif result and mode == '':
            return result[0][0]
        elif result and mode == 'pure': #to make endless amount of buttons with products
            return result
        elif result and mode == 'check':
            bot.send_message(param, 'Мы не намерены вас дальше обслуживать')
            print('Banned user {} tried to use this bot.\n'.format(param))
            # id = 123
            # print(readdb('bans',0,'id',message.from_user.id,'check')) - for checking
            # ind = 'W0102'
            # print(readdb('main','sdesc','Name',ind,'')) - for reading
    except:
        print('Error on reading from database.')
    pass

def writedb(event,client,id,mode):
    try:
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        if mode == 'log':
            cur.execute("INSERT INTO logs (time,event) VALUES(%s,%s)", (constants.time,event))
        elif mode == 'writeorder':
            cur.execute("INSERT INTO orders (client,id) VALUES(%s,%s)", (client, id))
        elif mode == 'wrsucor':
            cur.execute("UPDATE orders SET completed = 1 WHERE client = %s", (client,))
        elif mode == 'completed':
            cur.execute("UPDATE {} SET bought= 1 WHERE name = %s".format(id), (client,))
        conn.commit()
        conn.close()
    except:
        print('Error on writing to database.')
    pass

def back(call, id, message):
    try:
        bot.delete_message(id, message)
        bot.delete_message(id, message - 1)
    except:
        pass
    finally:
        start_handler(call)

def getprodid(x,mode):
    try:
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cur = conn.cursor()
        if mode == 'id':
            cur.execute("SELECT id FROM orders WHERE client=%s AND completed =%s", (x, 0))
        else:
            cur.execute("SELECT ind FROM orders WHERE client=%s AND completed =%s", (x, 0))
        result = cur.fetchall()
        id = str(result[0][0])
        conn.close()
        return id
    except:
        print('Can not check id.')

#######################################

@bot.message_handler(commands=['start'])
def start_handler(message):
    if (readdb('bans',0,'id',message.from_user.id,'check')) == False:
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton(text="Выбор товара", callback_data="choice"))
        kb.add(telebot.types.InlineKeyboardButton(text="Поддержка", callback_data="help"))
        bot.send_message(message.from_user.id, 'Добро пожаловать в магазин '+ constants.shopname + '!', reply_markup=kb)
        writedb('Starting bot for {}.\n'.format(str(message.from_user.id)),0,0,'log')

#######################################

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):

    if call.data == "choice":
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton(text="Кофе", callback_data="weed"))
        kb.add(telebot.types.InlineKeyboardButton(text="Чай", callback_data="plan"))
        kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))

        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                              text='Выберите продукт:', reply_markup=kb)

    elif call.data == "weed":
        kb = telebot.types.InlineKeyboardMarkup()
        sdesc = readdb(call.data, 'sdesc', 'bought', 0, 'pure')
        name = readdb(call.data, 'name', 'bought', 0, 'pure')
        x = 0
        try:
            for i in sdesc:
                kb.add(telebot.types.InlineKeyboardButton(text=str(i)[2:-3], callback_data=str(name[x])))
                x += 1
            kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='Выберите понравившееся место:', reply_markup=kb)
        except TypeError:
            kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='К сожалению, сейчас ничего нет в наличии.', reply_markup=kb)

    elif call.data == "plan":
        kb = telebot.types.InlineKeyboardMarkup()
        sdesc = readdb(call.data, 'sdesc','bought',0, 'pure')
        name = readdb(call.data,'name','bought',0,'pure')
        x = 0
        try:
            for i in sdesc:
                    kb.add(telebot.types.InlineKeyboardButton(text=str(i)[2:-3], callback_data=str(name[x])))
                    x+=1
            kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,text='Выберите понравившееся место:', reply_markup=kb)
        except TypeError:
            kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='К сожалению, сейчас ничего нет в наличии.', reply_markup=kb)

    elif call.data[2:4] == 'W0' or call.data[2:4] == 'P0':
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton(text="Оплатил", callback_data="payed"))
        kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
        text = call.data[2:-3]
        price = ''
        if call.data[2:4] == 'W0':
            price = readdb('weed','price','Name',text,'')
        elif call.data[2:4] == 'P0':
            price = readdb('plan', 'price', 'Name', text, '')
        admin = 88636100
        number = 738912
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,text='Оплатите {} рублей на кошелек киви: {} с обязательным примечанием {} .'.format(price,number,str(call.from_user.id)+text), reply_markup=kb)
        writedb(0,call.from_user.id,text,'writeorder')
        ind = getprodid(call.from_user.id,'')
        writedb('Order {} received and forwarded to: {}.\n'.format(ind, admin), 0, 0, 'log')

    elif call.data == 'payed':
        bot.delete_message(call.from_user.id,call.message.message_id)
        admin = 88636100
        number = 738912
        id = getprodid(call.from_user.id ,'id')
        price = ''
        if 'W' in id:
            price = readdb('weed', 'price', 'Name', id, '')
        elif 'P' in id:
            price = readdb('plan', 'price', 'Name', id, '')
        kb = telebot.types.InlineKeyboardMarkup()
        ind = str(readdb('orders','ind','id', id,''))
        while len(ind) < 4:
            ind = '0'+ ind
        data = '#CLA'+str(ind)+str(call.from_user.id)
        kb.add(telebot.types.InlineKeyboardButton(text="Проверил", callback_data=data))
        bot.send_message(admin, 'Поступил запрос на проверку оплаты товара {} в размере {} рублей на кошелек {} с примечанием {}'.format(id,price,number,str(call.from_user.id)+str(id)), reply_markup=kb)

    elif '#CLA' in call.data:
        client = call.data[8:]
        ind = call.data[4:8]
        for i in ind:
            if i != 0:
                break
            elif i == '0':
                ind = ind.replace(i, '')
        writedb(0, client, 0, 'wrsucor')
        bot.delete_message(call.from_user.id, call.message.message_id)
        id = readdb('orders', 'id', 'ind', ind, '')
        writedb('Accepting payment for client {}, order {} by admin {}.'.format(client, ind, call.from_user.id), 0, 0,'log')
        if 'W0' in id:
            x = 'weed'
        else:
            x = 'plan'
        description = readdb(x, 'description', 'name', id, '')
        coord = readdb(x, 'coord', 'name', id, '')
        phlink = readdb(x, 'phlink', 'name', id, '')
        kb = telebot.types.InlineKeyboardMarkup()
        kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
        bot.send_message(client, 'Ваш товар: \n {} \n Координаты: \n {}'.format(description, coord))
        bot.send_photo(client, phlink, reply_markup=kb)
        writedb(0, id, x, 'completed')

    elif call.data == "help":
        kb = telebot.types.InlineKeyboardMarkup()
        admin = 'sp812bro'
        kb.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="return"))
        bot.send_message(call.from_user.id,'Напишите @{} для получения помощи.'.format(admin),reply_markup=kb)

    elif call.data == 'return':
        back(call,call.from_user.id,call.message.message_id)

#######################################

if __name__ == '__main__':
    bot.polling(none_stop=True)