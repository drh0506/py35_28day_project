"""
审核接口：管理员去审核

审核的前置条件：
    1.管理员登录（类级别的前置）
    2.普通用户的角色添加项目
        （1）普通用户登录（类级别的前置）
        （2）创建一个项目（用例级别的前置）
"""
import unittest
import os
import requests
from jsonpath import jsonpath
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_data import replace_data
from common.handle_assertDictIn import assert_dict_in
from common.handle_mysql import HandleDB
from common.handler_log import log
from testcases.basetest import BaseTest


@ddt
class TestAudit(unittest.TestCase,BaseTest):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'loan_audit')
    cases = excel.read_data()
    db = HandleDB()

    @classmethod
    def setUpClass(cls):
        # 管理员登录
        cls.admin_login()

        # 普通用户登录
        cls.login()

    def setUp(self):
        """用例级别的前置：添加项目"""
        # 准备请求数据
        self.add_loan()

    @list_data(cases)
    def test_audit(self, item):
        url = conf.get('env', 'base_url') + item['url']
        method = item['method'].lower()
        item['data'] = replace_data(item['data'], TestAudit)
        params = eval(item['data'])
        expected = eval(item['expected'])
        row = item['case_id'] + 1
        response = requests.request(method=method, url=url, json=params, headers=self.admin_headers)
        res = response.json()
        # 判断用例是否执行通过，如果执行通过保存项目id
        if res['msg'] == 'OK' and params['approved_or_not'] == 'true':
            TestAudit.true_loan_id = int(params['loan_id'])
        if res['msg'] == 'OK' and params['approved_or_not'] == 'false':
            TestAudit.false_loan_id = int(params['loan_id'])

        # print("预期结果：", expected)
        # print("实际结果：", res)
        try:
            self.assertEqual(expected['code'],res['code'])
            self.assertEqual(expected['msg'],res['msg'])
            if item['check_sql']:
                sql = "SELECT STATUS FROM futureloan.loan WHERE id = '{}';".format(params['loan_id'])
                status = self.db.find_one(sql)[0]
                self.assertEqual(status, expected['status'])
        except AssertionError as e:
            log.error('用例--【{}】--执行失败。'.format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='未通过')
            raise e
        else:
            log.info('用例--【{}】--执行成功。'.format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
