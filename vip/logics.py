from common import errors


def need_perm(perm_name):
    '''检查用户是否具有某种权限'''
    def deco(view_func):
        def wrap(request, *args, **kwargs):
            # 先获取当前用户
            user = request.user
            # 检查用户权限
            if user.vip.has_perm(perm_name):
                return view_func(request, *args, **kwargs)
            else:
                raise errors.NotHasPerm('用户没有 %s 权限' % perm_name)
        return wrap
    return deco
