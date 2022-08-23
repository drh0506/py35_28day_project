import requests
from jsonpath import jsonpath
from common.handle_conf import conf

class BaseTest:

    @classmethod
    def admin_login(cls):
        url = conf.get('env', 'base_url') + '/member/login'
        admin_headers = eval(conf.get('env', 'headers'))
        admin_params = {
            "mobile_phone": conf.get('test_data', 'admin_mobile'),
            "pwd": conf.get('test_data', 'admin_pwd')
        }
        admin_response = requests.post(url=url, json=admin_params, headers=admin_headers)
        admin_res = admin_response.json()
        cls.admin_token = jsonpath(admin_res, '$..token')[0]
        admin_headers['Authorization'] = 'Bearer ' + cls.admin_token
        cls.admin_headers = admin_headers
        cls.admin_member_id = jsonpath(admin_res, '$..id')[0]

    @classmethod
    def login(cls):
        url = conf.get('env', 'base_url') + '/member/login'
        headers = eval(conf.get('env', 'headers'))
        params = {
            "mobile_phone": conf.get('test_data', 'mobile'),
            "pwd": conf.get('test_data', 'pwd')
        }
        response = requests.post(url=url, json=params, headers=headers)
        res = response.json()
        cls.token = jsonpath(res, '$..token')[0]
        headers['Authorization'] = 'Bearer ' + cls.token
        cls.headers = headers
        cls.member_id = jsonpath(res, '$..id')[0]

    @classmethod
    def invest_login(cls):
        url = conf.get('env', 'base_url') + '/member/login'
        invest_headers = eval(conf.get('env', 'headers'))
        invest_params = {
            "mobile_phone": conf.get('test_data', 'invest_mobile'),
            "pwd": conf.get('test_data', 'invest_pwd')
        }
        invest_response = requests.post(url=url, json=invest_params, headers=invest_headers)
        invest_res = invest_response.json()
        cls.invest_token = jsonpath(invest_res, '$..token')[0]
        invest_headers['Authorization'] = 'Bearer ' + cls.invest_token
        cls.invest_headers = invest_headers
        cls.invest_member_id = jsonpath(invest_res, '$..id')[0]

    @classmethod
    def add_loan(cls):
        add_url = conf.get('env', 'base_url') + '/loan/add'
        add_params = {"member_id": cls.member_id,
                      "title": "新增项目成功-借款期限1个月",
                      "amount": 1000,
                      "loan_rate": 1.2,
                      "loan_term": 1,
                      "loan_date_type": 1,
                      "bidding_days": 5
                      }
        add_response = requests.post(url=add_url, json=add_params, headers=cls.headers)
        add_res = add_response.json()
        cls.loan_id = jsonpath(add_res, '$..id')[0]

    @classmethod
    def true_audit(cls):
        true_audit_url = conf.get('env', 'base_url') + '/loan/audit'
        true_audit_params = {"loan_id": cls.loan_id,
                            "approved_or_not": "true"
                            }
        requests.patch(url=true_audit_url, json=true_audit_params, headers=cls.admin_headers)
        cls.true_loan_id = cls.loan_id

    @classmethod
    def false_audit(cls):
        false_audit_url = conf.get('env', 'base_url') + '/loan/audit'
        false_audit_params = {"loan_id": cls.loan_id,
                            "approved_or_not": "false"
                            }
        requests.patch(url=false_audit_url, json=false_audit_params, headers=cls.admin_headers)
        cls.false_loan_id = cls.loan_id
