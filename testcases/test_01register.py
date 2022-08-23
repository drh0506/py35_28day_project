import unittest
import os
import requests
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handler_log import log
from common.handle_assertDictIn import assert_dict_in
from common.handle_RandomMobile import random_mobile
from common.handle_mysql import HandleDB
from common.handle_data import replace_data


@ddt
class Testregister(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, "apicases.xlsx"), "register")
    # 读取用例数据
    cases = excel.read_data()
    # 项目的基本地址
    base_url = conf.get('env', 'base_url')
    # 请求头
    headers = eval(conf.get('env', 'headers'))
    db = HandleDB()

    @list_data(cases)
    def test_register(self, item):
        # 第一步，准备用例数据
        # 1.接口地址
        url = self.base_url + item['url']
        # 2.接口请求参数
        # 判断是否有手机号需要替换
        if '#mobile_phone#' in item['data']:
            Testregister.mobile_phone = random_mobile()
            item['data'] = replace_data(item['data'],Testregister)

        params = eval(item['data'])
        # 3.请求头
        # 4.获取请求方法，并转换为小写
        method = item['method'].lower()
        # 5.用例预期结果
        expected = eval(item['expected'])
        # 6.获取每一条测试用例的在excel的行数
        row = item["case_id"] + 1

        # 第二步，请求接口，获取返回实际结果
        response = requests.request(method=method, url=url, headers=self.headers, json=params)
        res = response.json()

        # 查询数据库中该手机对应的账户数量
        sql = 'SELECT * FROM futureloan.member WHERE mobile_phone = "{}";'.format(params.get('mobile_phone',''))
        count = self.db.find_count(sql)

        # 第三步，断言
        # print("预期结果:", expected)
        # print("实际结果:", res)



        try:
            # self.assertEqual(expected['code'], res['code'])
            # self.assertEqual(expected['msg'], res['msg'])
            assert_dict_in(expected, res)
            if item["check_sql"]:
                self.assertEqual(count,1)


        except AssertionError as e:
            # 记录日志
            log.error("用例--【{}】--执行失败".format(item['title']))
            log.exception(e)
            # 回写结果到excel
            # self.excel.write_data(row=row, column=8, value='不通过')
            raise e
        else:
            log.info("用例--【{}】--执行通过".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
