from config.config import Config
import psycopg2


class DataBase:
    def __init__(self, config: Config) -> None:
        self.user = config.user_db
        self.password = config.password_db
        self.database = config.database
        self.host = config.host_db
        self.port = config.port_db

    def connect_to_db(self):
        connect = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

        return connect

    def get_users(self):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT user_id FROM users;")
            user_ids = cursor.fetchall()
            return user_ids
        except Exception as e:
            print("Error with SELECT:", e)
        finally:
            cursor.close()
            connect.close()

    def add_users(self, user_id: int, fullname: str) -> None:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"INSERT INTO users (user_id, fullname) VALUES ({user_id}, '{fullname}');")
            connect.commit()
        except Exception as e:
            print("Error with INSERT:", e)
        finally:
            cursor.close()
            connect.close()

    def user_exists(self, user_id) -> bool:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id};")
            user_id = cursor.fetchone()
            return True if user_id else False
        except Exception as e:
            print("Error with CHECK EXISTS:", e)
        finally:
            cursor.close()
            connect.close()

    def get_current_name(self, user_id: int):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT u.fullname "
                           "FROM users AS u "
                           f"WHERE u.user_id = {user_id};")
            name = cursor.fetchone()
            return name[0]
        except Exception as e:
            print("Error with get_current_name():", e)
        finally:
            cursor.close()
            connect.close()

    def set_data(self, user_id: int, date: str, place: str, cash) -> None:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("INSERT INTO money (user_id, date, place, cash) "
                           f"VALUES ({user_id}, '{date}', '{place}', {cash});")
            connect.commit()
        except Exception as e:
            print("Error with INSERT:", e)
        finally:
            cursor.close()
            connect.close()

    def get_statistics_money(self, date_from: str, date_to: str):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT m.place, u.fullname, m.user_id, concat(SUM(m.cash::numeric)) "
                           "FROM money AS m, users AS u "
                           f"WHERE m.date BETWEEN '{date_from}' AND '{date_to}' "
                           "AND u.user_id = m.user_id "
                           "GROUP BY m.user_id, m.place, u.fullname "
                           "ORDER BY 1;")
            rows = cursor.fetchall()
            return rows
        except Exception as e:
            print("Error with money statistics:", e)
            return ["----"]
        finally:
            cursor.close()
            connect.close()

    def get_total_money(self, date_from: str, date_to: str):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT concat(SUM(m.cash::numeric)) "
                           "FROM money AS m "
                           f"WHERE m.date BETWEEN '{date_from}' AND '{date_to}';")
            money = cursor.fetchone()
            return money[0]
        except Exception as e:
            print("Error with total money statistics:", e)
            return ["-"]
        finally:
            cursor.close()
            connect.close()