from qiniu import Auth, put_file

from swiper import config


def upload_to_qiniu(local_filepath, key):
    '''
    上传文件到七牛云

    Args:
        local_filepath: 本地文件路径
        key: 上传到七牛后保存的文件名
    '''
    # 鉴权
    qn_auth = Auth(config.QN_ACCESS_KEY, config.QN_SECRET_KEY)

    # 生成上传 Token，可以指定过期时间等
    token = qn_auth.upload_token(config.QN_BUCKET, key, 3600)

    # 要上传文件的本地路径
    ret, info = put_file(token, key, local_filepath)
    return ret, info
