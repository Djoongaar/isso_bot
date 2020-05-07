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
                print('Exception in State.get_state()')

    @staticmethod
    def add_customers(chat_id, customers):
        with Vedis(config.DB_VEDIS) as db:
            s = db.List(f"{chat_id}_customers")
            for i in range(len(s)):
                s.pop()
            s.extend(customers)

    @staticmethod
    def get_customers(chat_id):
        with Vedis(config.DB_VEDIS) as db:
            try:
                s = db.List(f"{chat_id}_customers")
                last_state = s.pop()
                return last_state.decode(), db.llen(f"{chat_id}_customers")
            except:
                print('Exception in State.pop_customers()')
                return None

    @staticmethod
    def add_regions(chat_id, regions):
        with Vedis(config.DB_VEDIS) as db:
            s = db.List(f"{chat_id}_regions")
            for i in range(len(s)):
                s.pop()
            s.extend(regions)

    @staticmethod
    def get_regions(chat_id):
        with Vedis(config.DB_VEDIS) as db:
            try:
                s = db.List(f"{chat_id}_regions")
                last_state = s.pop()
                return last_state.decode(), db.llen(f"{chat_id}_regions")
            except:
                print('Exception in State.get_regions()')
                return None

    @staticmethod
    def set_inn(chat_id, inn):
        with Vedis(config.DB_VEDIS) as db:
            s = db.List(f"{chat_id}_inn")
            s.append(inn)

    @staticmethod
    def get_inn(chat_id):
        with Vedis(config.DB_VEDIS) as db:
            try:
                s = db.List(f"{chat_id}_inn")
                return s[-1].decode()
            except:
                print('Exception in State.get_inn()')
                return None
