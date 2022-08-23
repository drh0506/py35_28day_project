import unittest
import os
import requests
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_assertDictIn import assert_dict_in
from common.handler_log import log
from common.handle_data import replace_data
from common.handle_RandomMobile import random_mobile


@ddt
class TestLogin(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'login')
    cases = excel.read_data()
    base_url = conf.get('env', 'base_url')
    headers = eval(conf.get('env', 'headers'))

    @list_data(cases)
    def test_login(self, item):
        url = self.base_url + item['url']
        if '#mobile#' in item['data']:
            item['data'] = replace_data(item['data'], TestLogin)
        elif '#no_mobile#' in item['data']:
            TestLogin.no_mobile = random_mobile()
            item['data'] = replace_data(item['data'],TestLogin)
        params = eval(item['data'])
        method = item['method'].lower()
        expected = eval(item['expected'])
        row = item['case_id'] + 1

        response = requests.request(method=method, url=url, headers=self.headers, json=params)
        res = response.json()
        # print("预期结果：", expected)
        # print("实际结果：", res)

        try:
            assert_dict_in(expected, res)
        except AssertionError as e:
            log.error("用例--【{}】--执行失败".format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='不通过')
            raise e
        else:
            log.info("用例--【{}】--执行成功".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
