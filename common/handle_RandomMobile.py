import random


def random_mobile():
    mobile = '133'
    for i in range(8):
        n = str(random.randint(0, 9))
        mobile += n
    return mobile
