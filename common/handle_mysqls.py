"""项目中存在多个数据库时使用"""
import pymysql


class HandleDB:
    def __init__(self,host,port,user,password):
        self.con = pymysql.connect(host=host,
                                   port=port,
                                   user=user,
                                   password=password,
                                   charset='utf8',
                                   # cursorclass=pymysql.cursors.DictCursor
                                   )

    def find_one(self, sql):
        """查询一条数据"""
        with self.con.cursor() as cur:
            cur.execute(sql)
            self.con.commit()
        res = cur.fetchone()
        cur.close()
        return res

    def find_count(self, sql):
        """sql执行完之后，返回的数据条数"""
        with self.con.cursor() as cur:
            res = cur.execute(sql)
            self.con.commit()
        cur.close()
        return res

    def find_all(self, sql):
        """查询到的所有数据"""
        with self.con.cursor() as cur:
            cur.execute(sql)
            self.con.commit()
        res = cur.fetchall()
        cur.close()
        return res

    def __del__(self):
        self.con.cursor().close()


# 调试代码
if __name__ == '__main__':
    from common.handle_conf import conf
    sql = 'SELECT * FROM futureloan.member LIMIT 5;'
    db = HandleDB(
        host=conf.get('mysql','host'),
        port=conf.getint('mysql','port'),
        user=conf.get('mysql','user'),
        password=conf.get('mysql','password')
    )
    res = db.find_count(sql)
    print(res)
