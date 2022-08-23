import unittest
from unittestreport import TestRunner
from common.handle_path import CASES_DIR, REPORT_DIR
from unittestreport.core.sendEmail import SendEmail


def main():
    """程序的入口函数"""
    suite = unittest.defaultTestLoader.discover(CASES_DIR)
    runner = TestRunner(suite,
                        filename='apicases.html',
                        report_dir=REPORT_DIR,
                        tester='邓润恒',
                        title='20220815测试报告')
    runner.run()

    # 将测试结果发送到邮箱
    """
    host：str类型，（smtp服务器地址）
    port：int类型，（smtp服务器地址端口）
    user：str类型，（发件人邮箱账号）
    password：str类型，（smtp服务授权码）
    to_addrs：str（单个收件人）or list（多个收件人）收件人列表
    """
    runner.send_email(host='smtp.qq.com',
                      port=465,
                      user='872011469@qq.com',
                      password='frvygbptjqjibegj',
                      to_addrs=['872011469@qq.com', 'dengrunheng@metamedical.cn'],
                      is_file=True)


# --------------------扩展自定义邮件的标题和内容--------------------
# em = SendEmail(host='smtp.qq.com',
#                port=465,
#                user='872011469@qq.com',
#                password='frvygbptjqjibegj')
# em.send_email(subject="测试报告", content='邮件内容', filename='报告文件的完整路径', to_addrs='str（单个收件人）or list（多个收件人）收件人列表')

if __name__ == '__main__':
    main()

"""
扩展知识讲解：
一、测试结果的推送
    1.通过邮件发送到相关人员邮箱
    2.推送测试结果到钉钉群

二、
"""
