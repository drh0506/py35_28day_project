import rsa
import base64
from time import time

class HandleSign:
    server_pub = """
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQENQujkLfZfc5Tu9Z1LprzedE
    O3F7gs+7bzrgPsMl29LX8UoPYvIG8C604CprBQ4FkfnJpnhWu2lvUB0WZyLq6sBr
    tuPorOc42+gLnFfyhJAwdZB6SqWfDg7bW+jNe5Ki1DtU7z8uF6Gx+blEMGo8Dg+S
    kKlZFc8Br7SHtbL2tQIDAQAB
    -----END PUBLIC KEY-----
    """

    @classmethod
    def encrypt(cls,msg):
        """
        非对称加密
        :param msg: 待加密字符串或者字节
        :return: 密文
        """
        msg = msg.encode('utf-8')
        pub_key = cls.server_pub.encode('utf-8')
        # 创建PublicKey对象
        pubilc_key_obj = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
        # 生成加密文本
        cryto_msg = rsa.encrypt(msg,pubilc_key_obj)
        # 将加密文本转化为base64编码
        cipher_base64 = base64.b64encode(cryto_msg)
        # 将字节类型的base64编码转化为字符串类型
        return cipher_base64.decode()

    @classmethod
    def generate_sign(cls,token,timestamp=None):
        """
        生成sign
        :param token: token，为str类型
        :param timestamp: 当前秒计时间戳，为int类型
        :return: 时间戳和sign组成的字典
        """
        # 获取当前的时间戳
        timestamp = timestamp or int(time())
        # 获取token前50位
        prefix_50_token = token[:50]
        # 将token前50位与时间戳字符串进行拼接
        message = prefix_50_token + str(timestamp)
        # 生成sign
        sign = cls.encrypt(message)
        return {"timestamp":timestamp,"sign":sign}