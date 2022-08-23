import unittest
import os
import requests
from jsonpath import jsonpath
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_data import replace_data
from common.handle_mysql import HandleDB
from common.handle_assertDictIn import assert_dict_in
from common.handler_log import log
from testcases.basetest import BaseTest


@ddt
class TestLoanAdd(unittest.TestCase,BaseTest):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'loan_add')
    cases = excel.read_data()
    base_url = conf.get('env', 'base_url')
    db = HandleDB()

    @classmethod
    def setUpClass(cls):
        cls.login()

    @list_data(cases)
    def test_loan_add(self, item):
        url = self.base_url + item['url']
        method = item['method'].lower()
        if '#member_id' in item['data']:
            item['data'] = replace_data(item['data'], TestLoanAdd)
        params = eval(item['data'])
        expected = eval(item['expected'])
        row = item['case_id'] + 1

        if item['check_sql']:
            sql = 'SELECT * FROM futureloan.loan WHERE member_id = "{}";'.format(self.member_id)
            start_count = self.db.find_count(sql)

        response = requests.request(method=method, url=url, json=params, headers=self.headers)
        res = response.json()
        # print("预期结果：", expected)
        # print("实际结果：", res)
        try:
            assert_dict_in(expected, res)
            if item['check_sql']:
                sql = 'SELECT * FROM futureloan.loan WHERE member_id = "{}";'.format(self.member_id)
                end_count = self.db.find_count(sql)
                self.assertEqual(end_count - start_count, 1)
        except AssertionError as e:
            log.error("用例--【{}】--执行失败。".format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='未通过')
            raise e
        else:
            log.info("用例--【{}】--执行成功。".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
