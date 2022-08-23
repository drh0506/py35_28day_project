"""
用例前置操作的封装优化：
    1.把多个用例要使用的一些前置步骤封装到一个类中
    2.需要使用这个前置步骤的测试类，直接去继承（多继承）咱们封装好的前置步骤方法
    3.在类级别的前置和用例级别的前置中，调用对应的前置方法即可

用例方法：
    1.准备数据
    2.发送请求
    3.断言
        数据校验
            用户表：用户的余额投资前后会变化
                投资前 - 投资后 == 投资的金额

            流水记录表：投资成功会新增一条流水记录
                投资后用户流水记录数量 - 投资前用户流水记录数量 == 1

            投资表：投资成功会新增一条投资记录
                投资后用户的记录数量 - 投资前用户的记录数量 == 1
"""

import unittest
import os
import requests
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_data import replace_data
from common.handle_mysql import HandleDB
from common.handler_log import log
from testcases.basetest import BaseTest


@ddt
class TestInvest(unittest.TestCase, BaseTest):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'invest')
    cases = excel.read_data()
    db = HandleDB()
    n = 1

    @classmethod
    def setUpClass(cls):
        # 管理员登录
        cls.admin_login()

        # 普通用户登录
        cls.login()

        # 投资者登录
        cls.invest_login()

    def setUp(self):
        # 添加项目
        self.add_loan()

        # 审核项目
        if self.n < 9:
            self.true_audit()
            TestInvest.n = self.n + 1
        else:
            self.false_audit()

    @list_data(cases)
    def test_invest(self, item):
        url = conf.get('env', 'base_url') + item['url']
        method = item['method'].lower()
        item['data'] = replace_data(item['data'], TestInvest)
        params = eval(item['data'])
        expected = eval(item['expected'])
        row = item['case_id'] + 1

        # 查用户表的sql
        sql1 = 'SELECT leave_amount FROM futureloan.member WHERE id = "{}";'.format(self.invest_member_id)
        # 查投资表的sql
        sql2 = "SELECT * FROM futureloan.invest WHERE member_id = '{}';".format(self.invest_member_id)
        # 查流水记录表的sql
        sql3 = "SELECT * FROM futureloan.financelog WHERE pay_member_id = '{}';".format(self.invest_member_id)

        # 投资前查询数据库
        if item['check_sql']:
            start_amount = self.db.find_one(sql1)[0]
            start_invest = self.db.find_count(sql2)
            start_financelog = self.db.find_count(sql3)

        response = requests.request(method=method, url=url, json=params, headers=self.invest_headers)
        res = response.json()
        # print("预期结果：", expected)
        # print("实际结果：", res)

        try:
            self.assertEqual(expected['code'], res['code'])
            # 断言实际结果中的msg是否包含预期结果msg中的内容
            self.assertIn(expected['msg'], res['msg'])
            if item['check_sql']:
                end_amount = self.db.find_one(sql1)[0]
                end_invest = self.db.find_count(sql2)
                end_financelog = self.db.find_count(sql3)
                self.assertEqual(float(start_amount - end_amount), float(params['amount']))
                self.assertEqual(end_invest - start_invest, 1)
                self.assertEqual(end_financelog - start_financelog, 1)
        except AssertionError as e:
            log.error("用例--【{}】--执行失败。".format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='未通过')
            raise e
        else:
            log.info("用例--【{}】--执行成功。".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')

# self：是实例方法的第一个参数，代表的是实例对象本身
# cls：是类方法的第一个参数，代表的是类的本身
