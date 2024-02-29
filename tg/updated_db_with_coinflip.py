import psycopg2

# This actually outdated code, let it be here

class SQLighter:
    def __init__(self, db_uri):
        self.connection = psycopg2.connect(db_uri)
        self.cursor = self.connection.cursor()

    def check_user(self, user_id: int) -> bool:
        self.cursor.execute('SELECT * FROM users WHERE "user" = %s', (user_id,))
        return bool(self.cursor.fetchone())

    def is_tg_id_linked(self, tg_id: str) -> bool:
        self.cursor.execute('SELECT * FROM users WHERE tg_id = %s', (tg_id,))
        return bool(self.cursor.fetchone())

    def link_tg_id(self, user_id: int, tg_id: str):
        self.cursor.execute('UPDATE users SET tg_id = %s WHERE "user" = %s', (tg_id, user_id))
        self.connection.commit()

    def get_discord_id_by_tg_id(self, tg_id: str) -> int:
        self.cursor.execute('SELECT "user" FROM users WHERE tg_id = %s', (tg_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_profile_data(self, user_id: int):
        self.cursor.execute('SELECT balance FROM users WHERE "user" = %s', (user_id,))
        return self.cursor.fetchone()[0]

    def get_bal(self, user_id: int) -> int:
        """Получить баланс пользователя по его Discord ID."""
        self.cursor.execute('SELECT balance FROM users WHERE "user" = %s', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_balance(self, user_id: int, sum: int):
        """Добавить сумму к балансу пользователя."""
        self.cursor.execute('UPDATE users SET balance = balance + %s WHERE "user" = %s', (sum, user_id))
        self.connection.commit()

    def minus_balance(self, user_id: int, sum: int):
        """Вычесть сумму из баланса пользователя."""
        self.cursor.execute('UPDATE users SET balance = balance - %s WHERE "user" = %s', (sum, user_id))
        self.connection.commit()
