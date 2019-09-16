from random import randrange

import requests
from django.core.cache import cache

from common import keys
from swiper import config
from worker import celery_app


def gen_vcode(length=4):
    '''生成一个验证码'''
    start = 10 ** (length - 1)
    end = 10 ** length
    return str(randrange(start, end))


@celery_app.task
def send_sms(phonenum, msg):
    '''给手机发送信息'''
    params = config.YZX_SMS_PARAMS.copy()
    params['mobile'] = phonenum
    params['param'] = msg

    resp = requests.post(config.YZX_SMS_API, json=params)
    if resp.status_code == 200:
        result = resp.json()
        if result['code'] == '000000':
            return True, result['msg']
        else:
            return False, result['msg']
    else:
        return False, '短信服务器错误'


def send_vcode(phonenum):
    '''发送手机验证码'''
    vcode = gen_vcode()  # 创建验证码
    cache.set(keys.VCODE_KEY % phonenum, vcode, 300)  # 将验证码添加到缓存
    send_sms.delay(phonenum, vcode)  # 发送信息
