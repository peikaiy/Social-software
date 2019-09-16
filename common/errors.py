'''各种错误码'''

class LogicError(Exception):
    code = None
    data = None

    def __init__(self, data=None):
        self.data = data

    def __str__(self):
        return '%s' % self.__class__.__name__


def gen_logic_err(name, code):
    '''产生一个 LogicError 子类'''
    attr_dict = {'code': code}
    return type(name, (LogicError,), attr_dict)


VcodeErr = gen_logic_err('VcodeErr', 1000)  # 验证码错误
ProfileErr = gen_logic_err('ProfileErr', 1001)  # 修改用户资料错误
LoginRequired = gen_logic_err('LoginRequired', 1002)  # 用户必须先登录
UserNotExist = gen_logic_err('UserNotExist', 1003)  # 用户不存在
RewindLimited = gen_logic_err('RewindLimited', 1004)  # 反悔次数达到每日上限
NotHasPerm = gen_logic_err('NotHasPerm', 1005)  # 用户没有某种权限
