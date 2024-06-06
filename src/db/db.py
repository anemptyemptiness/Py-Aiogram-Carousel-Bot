import pprint

from src.config import Settings
import psycopg2
import logging


class DataBase:
    def __init__(self, settings: Settings) -> None:
        self._user = settings.DB_USER
        self._password = settings.DB_PASS
        self._database = settings.DB_NAME
        self._host = settings.DB_HOST
        self._port = settings.DB_PORT
        self._logger = logging.getLogger(__name__)

    def _connect_to_db(self):
        connect = psycopg2.connect(
            dbname=self._database,
            user=self._user,
            password=self._password,
            host=self._host,
            port=self._port
        )

        return connect

    def get_admins_user_ids(self):
        connect = self._connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(
                """
                SELECT e.user_id
                FROM employees AS e
                WHERE e.role = 'admin';
                """
            )
            return [int(x[0]) for x in cursor.fetchall()]
        except Exception as e:
            self._logger.exception("Ошибка в get_admins_user_ids()")
        finally:
            cursor.close()
            connect.close()

    def get_employees_user_ids(self):
        connect = self._connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(
                """
                SELECT e.user_id 
                FROM employees AS e 
                WHERE e.role = 'employee';
                """
            )
            return [int(x[0]) for x in cursor.fetchall()]
        except Exception as e:
            self._logger.exception("Ошибка в get_employees_user_ids()")
        finally:
            cursor.close()
            connect.close()

    def get_places(self):
        connect = self._connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(
                """
                SELECT p.title, p.chat_id 
                FROM places AS p;
                """
            )
            return [(x[0], x[1]) for x in cursor.fetchall()]
        except Exception as e:
            self._logger.exception("Ошибка в get_places()")
        finally:
            cursor.close()
            connect.close()

    def get_chat_ids(self):
        connect = self._connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(
                """
                SELECT p.chat_id 
                FROM places AS p;
                """
            )
            return [x[0] for x in cursor.fetchall()]
        except Exception as e:
            self._logger.exception("Ошибка в get_chat_ids()")
        finally:
            cursor.close()
            connect.close()

    def get_employees_fullname_and_id(self, role: str):
        connect = self._connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(
                f"""
                SELECT e.fullname, e.user_id 
                FROM employees AS e 
                WHERE role = '{role}';
                """
            )
            return [(x[0], x[1]) for x in cursor.fetchall()]
        except Exception as e:
            self._logger.exception("Ошибка в get_employees_fullname_and_id()")
        finally:
            cursor.close()
            connect.close()

    def my_script(self):
        connect = self._connect_to_db()
        cursor = connect.cursor()
        places = {
            "Новая Рига": 1,
            "Белая Дача": 2,
            "Внуково": 3,
            "Саларис": 4,
        }

        places_ids = {
            "Новая Рига": [1, -430076961],
            "Белая Дача": [2, -986892845],
            "Внуково": [3, -645118561],
            "Саларис": [4, -1001866626436],
        }
        users = {}
        result_users = []
        result_reports = []
        result_places = []

        cursor.execute(
            """
            select * from users;
            """
        )

        i = 1
        for user_id, fullname in cursor.fetchall():
            username: str = ''
            role: str = 'employee'

            if i == 1:
                username = '@cryslarecrill'
                role = 'admin'
            if i == 2:
                username = '+79197708567'
            if i == 3:
                username = '+79034971387'
            if i == 4:
                username = '@Grei1975'
            if i == 5:
                username = 'нет инфо'
            if i == 6:
                username = '@kaskat02'
                role = 'admin'
            if i == 7:
                username = '+79779071964'
            if i == 8:
                username = '+79259576380'
            if i == 9:
                username = 'нет инфо'

            users[user_id] = i
            result_users.append((i, user_id, f'{fullname}', f'{username}', f'{role}'))

            i += 1

        for title, lst in places_ids.items():
            result_places.append((lst[0], lst[1], title))

        cursor.execute(
            """
            select * from money;
            """
        )
        # pprint.pprint(result_users)

        for user_id, date, place, cash in cursor.fetchall():
            cash = cash[1:]
            cash = cash.replace(',', '')
            cash = int(cash[:-3])
            result_reports.append((f'{date}', 0, cash, places[place], users[user_id]))

        pprint.pprint(result_places)
        # pprint.pprint(result_users)
        # pprint.pprint(result_reports)
