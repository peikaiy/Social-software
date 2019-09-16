import logging

from django.utils.deprecation import MiddlewareMixin

from lib.http import render_json
from common import errors
from user.models import User

err_log = logging.getLogger('err')


class AuthMiddleware(MiddlewareMixin):
    URL_WHITE_LIST = [
        '/api/user/submit/phone',
        '/api/user/submit/vcode',
    ]

    def process_request(self, request):
        # 如果当前 url 在白名单内，直接忽略
        if request.path in self.URL_WHITE_LIST:
            return

        # 检查用户是否登录
        uid = request.session.get('uid')
        if uid:
            try:
                request.user = User.get(id=uid)
            except User.DoesNotExist:
                return render_json('用户不存在', errors.UserNotExist.code)
        else:
            return render_json('用户未登录', errors.LoginRequired.code)


class LogicErrMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        '''处理程序中的 LogicError'''
        if isinstance(exception, errors.LogicError):
            err_log.error(exception)
            return render_json(exception.data, exception.code)
