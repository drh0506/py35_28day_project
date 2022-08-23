"""项目中只有一个数据库时使用"""
import pymysql
from common.handle_conf import conf


class HandleDB:
    def __init__(self):
        self.con = pymysql.connect(host=conf.get('mysql', 'host'),
                                   port=conf.getint('mysql', 'port'),
                                   user=conf.get('mysql', 'user'),
                                   password=conf.get('mysql', 'password'),
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
    parame = {"member_id":"#member_id#","title":"新增项目成功-借款期限1个月","amount":100,"loan_rate":1.2,"loan_term":1,"loan_date_type":1,"bidding_days":5}
    sql = 'SELECT * FROM futureloan.loan WHERE title = "{}";'.format(parame['title'])
    db = HandleDB()
    res = db.find_count(sql)
    print(res,type(res))
