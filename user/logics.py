import os
from urllib.parse import urljoin

from django.conf import settings

from swiper import config
from lib.qncloud import upload_to_qiniu
from worker import celery_app


def save_upload_avatar(uid, upload_avatar):
    '''保存上传的用户头像'''
    filename = 'Avatar-%s' % uid
    filepath = os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, filename)

    with open(filepath, 'wb') as fp:
        for chunk in upload_avatar.chunks():
            fp.write(chunk)
    return filepath, filename


@celery_app.task
def upload_avatar(user, upload_avatar):
    '''上传个人形象处理'''
    filepath, filename = save_upload_avatar(user.id, upload_avatar)  # 保存到本地
    upload_to_qiniu(filepath, filename)  # 保存到七牛

    # 修改 user.avatar 地址
    avatar_url = urljoin(config.QN_URL_PREFIX, filename)
    user.avatar = avatar_url
    user.save()
