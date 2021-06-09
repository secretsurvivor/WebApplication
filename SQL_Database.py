import mysql.connector


class SQLDatabase:
    def __init__(self):
        self.db = mysql.connector.connect(user='secret', password='dkibkhnc98cx',
                                          host='127.0.0.1', database='webdev',
                                          auth_plugin='mysql_native_password')
        self.cursor = self.db.cursor()

    def table_exists(self, table_name) -> bool:
        self.cursor.execute("SHOW TABLES")
        exist = False
        for table in self.cursor:
            if table[0] == table_name:
                exist = True
        return exist

    def execute(self, query, val=""):
        self.cursor.execute(query, val)
        return self.cursor

    def select(self, query, val=""):
        self.cursor.execute(query, val)
        results = self.cursor.fetchall()
        if len(results) == 0:
            return None
        else:
            return results

    def commit(self, query, val=""):
        self.cursor.execute(query, val)
        self.db.commit()
        return self.cursor.lastrowid

    def close(self):
        self.db.close()
