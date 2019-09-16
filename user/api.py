import logging

from django.core.cache import cache

from lib.http import render_json
from lib.sms import send_vcode
from common import keys
from common import errors
from user.models import User
from user.forms import ProfileForm
from user import logics

inf_log = logging.getLogger('inf')


def submit_phone(request):
    '''提交手机号，发送验证码'''
    phone = request.POST.get('phone')
    send_vcode(phone)
    return render_json(None)


def submit_vcode(request):
    '''提交短信验证码，登录'''
    phone = request.POST.get('phone')
    vcode = request.POST.get('vcode')

    cache_vcode = cache.get(keys.VCODE_KEY % phone)

    if vcode == cache_vcode:
        # 执行登录过程
        user, _ = User.get_or_create(phonenum=phone, nickname=phone)

        # 在 session 中记录登录状态
        request.session['uid'] = user.id
        inf_log.info(f'login {user.id}')  # 日志记录

        return render_json(user.to_dict())
    else:
        raise errors.VcodeErr('验证码错误')


def get_profile(request):
    '''获取个人资料'''
    user = request.user
    key = 'ProfileDict-%s' % user.id
    # 先从缓存获取
    profile_dict = cache.get(key)
    print('get from cache: %s' % profile_dict)
    if profile_dict is None:
        # 如果缓存中没有，从数据库中获取
        profile_dict = user.profile.to_dict()
        print('get from db: %s' % profile_dict)
        # 将数据库中的数据添加到缓存
        cache.set(key, profile_dict, 86400 * 7)
        print('set to cache')
    return render_json(profile_dict)


def set_profile(request):
    '''修改个人配置'''
    form = ProfileForm(request.POST)
    if form.is_valid():
        profile = form.save(commit=False)
        profile.id = request.session['uid']
        profile.save()

        # 更新缓存
        print('update cache')
        key = 'ProfileDict-%s' % profile.id
        cache.set(key, profile.to_dict(), 86400 * 7)

        return render_json(None)
    else:
        raise errors.ProfileErr(form.errors)


def upload_avatar(request):
    '''头像上传'''
    user = request.user
    avatar = request.FILES.get('avatar')  # 取出文件对象

    logics.upload_avatar.delay(user, avatar)
    return render_json(None)
