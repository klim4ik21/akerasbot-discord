import psycopg2
import random
import datetime

db_uri = "postgresql connection"

class SQLighter:
    def __init__(self, db_uri):
        self.connection = psycopg2.connect(db_uri)
        self.cursor = self.connection.cursor()

    def check_user(self, user_id: int) -> bool:
        # Обратите внимание на использование двойных кавычек вокруг user
        self.cursor.execute('SELECT * FROM users WHERE "user" = %s', (user_id,))
        return self.cursor.fetchone() is not None

    def register(self, user_id: int) -> bool:
        # Make sure user_id is a string representation of the integer ID
        user_id_str = str(user_id)
        if not self.check_user(user_id_str):
            self.cursor.execute('INSERT INTO users ("user", balance, vc_hours, att_count, games_count, is_admin, tg_id, end_premium, marry_id, marry_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (user_id_str, 0, 0, 0, 0, 0, 0, None, None, None))
            self.connection.commit()
            return True
        else:
            return False


    def get_bal(self, user_id: int) -> int:
        # Assuming user_id is passed as an integer, and the "user" column is of type bigint
        self.cursor.execute('SELECT balance FROM users WHERE "user" = %s', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_vc_hours(self, user_id: int) -> int:
        # Ensure that the column name "user" is enclosed in double quotes
        self.cursor.execute('SELECT vc_hours FROM users WHERE "user" = %s', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_vc_hours(self, user_id: int, new_vc_hours: int):
        self.cursor.execute('UPDATE users SET vc_hours = %s WHERE "user" = %s', (new_vc_hours, user_id))
        self.connection.commit()

    def reg_gift(self, user_id: int) -> bool:
        if not self.is_gift(user_id):
            self.cursor.execute("INSERT INTO gifts (user, is_gift, gift_link) VALUES (%s, %s, %s)", (user_id, 0, None))
            self.connection.commit()
            return True
        else:
            return False

    def add_balance(self, user_id: int, sum: int):
        self.cursor.execute('UPDATE users SET balance = balance + %s WHERE "user" = %s', (sum, user_id))
        self.connection.commit()

    def minus_balance(self, user_id: int, sum: int):
        self.cursor.execute('UPDATE users SET balance = balance - %s WHERE "user" = %s', (sum, user_id))
        self.connection.commit()

    def coinflipgame(self, user_id: int):
        self.cursor.execute('UPDATE users SET games_count = games_count + 1 WHERE "user" = %s', (user_id,))
        self.connection.commit()

    def is_gift(self, user_id: int) -> bool:
        self.cursor.execute('SELECT is_gift FROM gifts WHERE "user" = %s', (user_id,))
        result = self.cursor.fetchone()
        return bool(result[0]) if result else False

    def update_gift(self, user_id: int):
        self.cursor.execute('UPDATE gifts SET is_gift = 1 WHERE "user" = %s', (user_id,))
        self.connection.commit()

    def update_gift_link(self, user_id: int, gift_link: str):
        self.cursor.execute('UPDATE gifts SET gift_link = %s WHERE "user" = %s', (gift_link, user_id))
        self.connection.commit()

    def get_random_gift(self):
        self.cursor.execute('SELECT user FROM gifts WHERE is_gift = 0')
        all_users = self.cursor.fetchall()
        return random.choice(all_users)[0] if all_users else None

    def get_gift_link(self, user_id: int) -> str:
        self.cursor.execute('SELECT gift_link FROM gifts WHERE "user" = %s', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def get_top_players(self, limit=3):
        """
        Получение топ игроков по балансу.

        :param limit: Количество пользователей в топе.
        :return: Список словарей с информацией о топ игроках.
        """
        self.cursor.execute('SELECT "user", balance FROM users ORDER BY balance DESC LIMIT %s', (limit,))
        return self.cursor.fetchall()
    
    def get_total_balance(self):
        self.cursor.execute('SELECT SUM(balance) FROM users')
        result = self.cursor.fetchone()
        return result[0] if result else 0
    
    def add_role(self, role_name, role_id, role_owner, role_price, role_expiry):
        query = '''
        INSERT INTO roles (role_name, role_id, role_owner, role_price, role_expiry)
        VALUES (%s, %s, %s, %s, %s)
        '''
        self.cursor.execute(query, (role_name, role_id, role_owner, role_price, role_expiry))
        self.connection.commit()

    def get_all_roles(self):
        query = 'SELECT * FROM roles'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_expired_roles(self):
        query = 'SELECT * FROM roles WHERE role_expiry < NOW()'
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def remove_role(self, role_id):
        query = 'DELETE FROM roles WHERE role_id = %s'
        self.cursor.execute(query, (role_id,))
        self.connection.commit()


    def update_role(self, role_id, new_name=None, new_price=None, new_expiry=None):
        # Обновление информации о роли в соответствии с предоставленными параметрами
        query = 'UPDATE roles SET '
        params = []
        if new_name:
            query += 'role_name = %s,'
            params.append(new_name)
        if new_price:
            query += 'role_price = %s,'
            params.append(new_price)
        if new_expiry:
            query += 'role_expiry = %s,'
            params.append(new_expiry)

        query = query.rstrip(',')  # Удаляем последнюю запятую
        query += ' WHERE role_id = %s'
        params.append(role_id)
        
        self.cursor.execute(query, tuple(params))
        self.connection.commit()

    def update_role_price(self, role_id, new_price):
        query = 'UPDATE roles SET role_price = %s WHERE role_id = %s'
        self.cursor.execute(query, (new_price, role_id))
        self.connection.commit()

    def get_user_roles(self, user_id):
        query = 'SELECT role_name, role_id FROM roles WHERE role_owner = %s'
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()


    def is_tg_id_linked(self, tg_id: str) -> bool:
        self.cursor.execute('SELECT * FROM users WHERE tg_id = %s', (tg_id,))
        return bool(self.cursor.fetchone())

    def link_tg_id(self, user_id: int, tg_id: str):
        self.cursor.execute('UPDATE users SET tg_id = %s WHERE "user" = %s', (tg_id, user_id))
        self.connection.commit()

    def is_admin(self, user_id: int) -> int:
        self.cursor.execute('SELECT is_admin FROM users WHERE "user" = %s', (user_id,))
        return self.cursor.fetchone()[0]
    
    def get_premium_end(self, user_id: int) -> int:
        self.cursor.execute('SELECT end_premium FROM users WHERE "user" = %s', (user_id,))
        return self.cursor.fetchone()[0]
    
    def upd_premium(self, user_id: int) -> int:
        self.cursor.execute('UPDATE users SET end_premium = %s WHERE "user" = %s', (datetime.datetime.now() + datetime.timedelta(weeks=1), user_id))
        self.connection.commit()

    def marry(self, user_id: int, marry_id: int) -> int:
        self.cursor.execute('UPDATE users SET marry_id = %s WHERE "user" = %s', (marry_id, user_id))
        self.connection.commit()

    def marry_time(self, user_id: int, marry_time) -> int:
        self.cursor.execute('UPDATE users SET marry_time = %s WHERE "user" = %s', (marry_time, user_id))
        self.connection.commit()

    def get_marry(self, user_id: int) -> int:
        self.cursor.execute('SELECT marry_id FROM users WHERE "user" = %s', (user_id,))
        return self.cursor.fetchone()[0]

    def close(self):
        self.connection.close()