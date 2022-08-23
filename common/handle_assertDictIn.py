# class AssertDictIn:
#
#     def __init__(self, expected, res):
#         self.expected = expected
#         self.res = res

def assert_dict_in(expected,res):
    """字典成员运算的逻辑"""
    for k, v in expected.items():
        if res.get(k) == v:
            pass
        else:
            raise AssertionError("{} not in {}".format(expected, res))
