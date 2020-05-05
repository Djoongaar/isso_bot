from vedis import Vedis

import config


class States:
    """
    Мы используем БД Vedis, в которой хранимые значения всегда строки,
    поэтому и тут будем использовать тоже строки (str)
    """

    @staticmethod
    def add_state(chat_id, state):
        with Vedis(config.DB_VEDIS) as db:
            if state != "/back":
                db.sadd(chat_id, state)
            print(db.smembers(chat_id))

    @staticmethod
    def get_state(chat_id):
        with Vedis(config.DB_VEDIS) as db:
            try:
                db.spop(chat_id)
                last_state = db.speek(chat_id)
                print(last_state.decode())
                return last_state.decode()
            except:
                print('Exception in State.pop_state()')

    @staticmethod
    def add_customers(chat_id, customers):
        with Vedis(config.DB_VEDIS) as db:
            s = db.List(chat_id)
            for i in range(len(s)):
                s.pop()
            s.extend(customers)

    @staticmethod
    def get_customers(chat_id):
        with Vedis(config.DB_VEDIS) as db:
            try:
                s = db.List(chat_id)
                last_state = s.pop()
                return last_state.decode(), db.llen(chat_id)
            except:
                print('Exception in State.pop_customers()')
                return None
