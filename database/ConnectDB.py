import psycopg2


# mqtt.eclipseprojects.io
class ConnectDB:
    """create connection with database"""
    conn = None
    cur = None

    # database information
    db_name = 'postgres'
    db_user = 'postgres'
    db_pass = 'sps-postgres'
    db_host = 'localhost'
    db_port = '5432:5432'

    def __init__(self):
        """only initializes object of ConnectDB.
         do not create a connection with database"""
        pass

    def connect(self):
        """create a connection with database"""
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
        #finally:
            #return self.conn

    def close(self):
        """close a connection with database"""
        try:
            self.conn.close()
            if self.cur is not None:
                self.cur.close()
            print("Connection is closed")
        except:
            print("Closing is failed")

    def get_cursor(self):
        """get cursor to execute sql-query
         for example: cursor.execute("select * from table_name")"""
        if self.conn is None:
            return None
        else:
            return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
