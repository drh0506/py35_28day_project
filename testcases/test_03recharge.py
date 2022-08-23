"""
充值的前提：登录-->提取token
unittest：
    用例级别的前置：setUp

    测试类级别的前置：setUpClass
        1.提取token，保存为类属性
        2.提取用户id，保存为类属性

    充值测试方法：
        1.动态的替换参数中的用户id（字符串的replace中的参数必须是字符串类型）

注册类的优化：
    1.手机号动态生成，替换到用例参数中
"""
import unittest
import os
import requests
import time
from jsonpath import jsonpath
from unittestreport import ddt, list_data
from common.handle_excle import HandleExcel
from common.handle_path import DATA_DIR
from common.handle_conf import conf
from common.handle_assertDictIn import assert_dict_in
from common.handler_log import log
from common.handle_mysql import HandleDB
from common.handle_data import replace_data


@ddt
class TestRecharge(unittest.TestCase):
    excel = HandleExcel(os.path.join(DATA_DIR, 'apicases.xlsx'), 'recharge')
    cases = excel.read_data()
    base_url = conf.get('env', 'base_url')
    db = HandleDB()

    # 获取token只需要在执行全部测试用例之前获取一次就可以，不需要每一条测试用例都获取一次token，所以使用测试类级别的前置（setUpClass(cls)）
    # setUpClass(cls)：所有的测试方法运行前运行，为单元测试做前期准备，但必须使用@classmethod装饰器进行修饰，整个测试过程中只执行一次。
    # 需要使用@classmethod装饰器进行修饰是因为setUpClass(cls)定义为一个类方法，只在类里面使用
    """
    python unitest单元测试框架中，有几个特殊的情况如下：
    setUp()：每个测试方法运行前运行，测试前的初始化工作。一条用例执行一次，若N次用例就执行N次，根据用例的数量来定。
    setUpClass()：所有的测试方法运行前运行，为单元测试做前期准备，但必须使用@classmethod装饰器进行修饰，整个测试过程中只执行一次。
    tearDown()：每个测试方法运行结束后运行，测试后的清理工作。一条用例执行一次，若N次用例就执行N次。
    tearDownClass()：所有的测试方法运行结束后运行，为单元测试做后期清理工作，但必须使用@classmethod装饰器进行修饰，整个测试过程中只执行一次。

    用例级别：
    setUp：用例级别的前置，每条测试用例执行之前都会执行
    tearDown：用例级别的后置，每条测试用例执行之后都会执行
    测试类级别：
    setUpClass：用例类级别的前置，整个测试用例类里面的全部测试用例执行之前先执行
    tearDownClass：用例类级别的后置，整个测试用例类里面的全部测试用例执行完之后再执行
    """

    @classmethod
    def setUpClass(cls):
        """用例类的前置方法，登录提取token"""
        # 1.请求登录接口，进行登录
        url = conf.get('env', 'base_url') + '/member/login'
        params = {
            "mobile_phone": conf.get('test_data', 'mobile'),
            "pwd": conf.get('test_data', 'pwd')
        }
        headers = eval(conf.get('env', 'headers'))
        response = requests.post(url=url, json=params, headers=headers)
        res = response.json()

        # 2.登录成功之后再去提取token
        token = jsonpath(res, "$..token")[0]
        # 将token添加到请求头中
        headers["Authorization"] = "Bearer " + token
        # 将含有token的请求头定义为类属性（cls代表类自己本身）
        cls.headers = headers
        # 使用动态属性设置方法把含有token的请求头定义为类属性
        # setattr(TestRecharge,'headers',headers)

        # 3.提取用户的id给充值接口使用
        cls.member_id = jsonpath(res, "$..id")[0]

    # 需要被写着测试用例的excel文件调用，excel文件是一个实例，所以定义为实例方法
    # excel文件里面的每一条测试用例作为参数调用该实例方法，所以实例方法中定义了一个item的参数来接收每一条测试用例执行实例方法里面的代码
    @list_data(cases)
    def test_recharge(self, item):
        url = self.base_url + item['url']

        # ****************************动态替换参数******************************
        # 动态处理需要进行替换的参数
        # item['data'] = item['data'].replace('#member_id#', str(self.member_id))
        item['data'] = replace_data(item['data'],TestRecharge)
        params = eval(item['data'])
        # **********************************************************************

        method = item['method'].lower()
        expected = eval(item['expected'])
        row = item['case_id'] + 1

        # ********************请求接口之前查询用户的余额********************
        sql = 'SELECT leave_amount FROM futureloan.member WHERE mobile_phone = "{}"'.format(
                conf.get('test_data', 'mobile'))
        start_amount = self.db.find_one(sql)[0]

        response = requests.request(method=method, url=url, json=params, headers=self.headers)
        res = response.json()
        # print("预期结果：", expected)
        # print("执行结果：", res)

        # ********************请求接口之后查询用户的余额********************
        end_amount = self.db.find_one(sql)[0]

        try:
            assert_dict_in(expected, res)
            # ********************校验数据库中用户余额的变化是否等于充值的金额********************
            if res['msg'] == 'OK':
                # 充值成功，用户余额的变化为充值金额
                self.assertEqual(float(end_amount - start_amount), float(params['amount']))
            else:
                # 充值失败，用户余额变化为0
                self.assertEqual(float(end_amount - start_amount), 0)

        except AssertionError as e:
            log.error("用例--【{}】--执行失败".format(item['title']))
            log.exception(e)
            # self.excel.write_data(row=row, column=8, value='不通过')
            raise e
        else:
            log.info("用例--【{}】--执行成功".format(item['title']))
            # self.excel.write_data(row=row, column=8, value='通过')
