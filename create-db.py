import sqlite3
import config
import datetime

#Test db, project use POSTGRESQL!

def createdb():
    # Подключаемся к бд
    connection = sqlite3.connect("discord.db")
    cursor = connection.cursor()
    print("пуш тест")


    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        user INT,
        balance BIGINT,
        vc_hours BIGINT,
        att_count INT,
        games_count BIGINT,
        is_admin INT
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS gifts(
        user INT,
        is_gift INT,
        gift_link TEXT
    )""")

    connection.commit()

createdb()
