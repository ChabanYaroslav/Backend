import psycopg2

class ConnectDB:
    """create connection with DB"""
    conn = None
    cur = None

    # Database information
    db_name = 'postgres'
    db_user = 'postgres'
    db_pass = 'sps-postgres'
    db_host = 'localhost'
    db_port = '5432:5432'

    def __init__(self):
        """only initializes object of ConnectDB.
         do not create a connection with DB"""
        pass

    def connect(self):
        """create a connection with DB"""
        try:
            self.conn = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass,
                host=self.db_host
            )
            print("Connection is successful")
        except:
            print("Connection is failed")
        finally:
            return self.conn

    def close(self):
        """close a connection with DB"""
        try:
            self.conn.close()
            print("Connection is closed")
        except:
            print("Closing is failed")

    def get_cursor(self):
        """get cursor to execute sql-query
         for example: cursor.execute("select * from table_name")"""
        return self.conn.cursor()
