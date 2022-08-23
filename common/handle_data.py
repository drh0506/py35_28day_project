import re
from common.handle_conf import conf

def replace_data(data,cls):
    """
    替换数据方法
    :param data: 要进行替换的用例数据（字符串）
    :param cls: 测试类
    :return:
    """
    while re.search('#(.+?)#', data):
        res = re.search('#(.+?)#', data)
        item = res.group()
        attr = res.group(1)
        try:
            value = getattr(cls, attr)
        except AttributeError:
            value = conf.get('test_data',attr)

        # 进行替换
        data = data.replace(item, str(value))
    return data



if __name__ == '__main__':
    class Data:
        id = 123
        name = 'musen'
        data = '1122'
        title = '测试数据'

    s = "{'id':'#id#','name':'#name#','data':'#data#','title':'#title#','aaa':11,'bbb':222}"

    res = replace_data(s,Data)
    print(res)


