import unittest
import os
import requests
from unittestreport import ddt, list_data
from jsonpath import jsonpath
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_assertDictIn import assert_dict_in
from common.handler_log import log
from common.handle_mysql import HandleDB
from common.handle_data import replace_data
from testcases.basetest import BaseTest


@ddt
class TestWithdraw(unittest.TestCase,BaseTest):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'withdraw')
    cases = excel.read_data()
    base_url = conf.get('env', 'base_url')
    db = HandleDB()

    @classmethod
    def setUpClass(cls):
        cls.login()

    @list_data(cases)
    def test_withdraw(self, item):
        url = self.base_url + item['url']
        method = item['method'].lower()
        if "#member_id#" in item['data']:
            item['data'] = replace_data(item['data'], TestWithdraw)
        params = eval(item['data'])
        expected = eval(item['expected'])
        row = item['case_id'] + 1

        sql = 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone = "{}";'.format(
                conf.get('test_data', 'mobile'))
        start_amount = self.db.find_one(sql)[0]

        response = requests.request(method=method, url=url, json=params, headers=self.headers)
        res = response.json()

        # print("预期结果：", expected)
        # print("实际结果：", res)

        end_amount = self.db.find_one(sql)[0]

        try:
            assert_dict_in(expected, res)
            if item['check_sql']:
                self.assertEqual(float(start_amount - end_amount), float(params['amount']))
        except AssertionError as e:
            log.error("用例--【{}】--执行失败。".format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='未通过')
            raise e
        else:
            log.info("用例--【{}】--执行成功。".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
