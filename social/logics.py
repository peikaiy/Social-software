import datetime

from django.core.cache import cache

from lib.cache import rds
from swiper import config
from common import errors
from common import keys
from user.models import User
from social.models import Swiped
from social.models import Friend


def rcmd_users(user):
    '''用户推荐'''
    # 筛选出所有被当前用户划过的用户的 uid
    swiped = Swiped.objects.filter(uid=user.id).only('sid')
    swiped_uid_list = [sw.sid for sw in swiped]
    swiped_uid_list.append(user.id)  # 排除自己

    # 计算出生年份的范围
    curr_year = datetime.date.today().year  # 当前年份
    max_birth_year = curr_year - user.profile.min_dating_age
    min_birth_year = curr_year - user.profile.max_dating_age

    # 根据条件筛选 user 对象
    users = User.objects.filter(
        location=user.profile.location,
        sex=user.profile.dating_sex,
        birth_year__range=[min_birth_year, max_birth_year]
    ).exclude(id__in=swiped_uid_list)[:20]

    return users


def like(user, sid):
    '''喜欢了某人'''
    # 添加滑动记录
    Swiped.swipe('like', user.id, sid)

    # 检查对方是否喜欢过你
    if Swiped.is_liked_someone(sid, user.id):
        # 建立好友关系
        Friend.make_friends(user.id, sid)
        # TODO: 向好友推送完成匹配的消息 (集成消息推送服务)

        return True  # 返回完成匹配的结果
    else:
        return False


def superlike(user, sid):
    '''超级喜欢了某人'''
    # 添加滑动记录
    Swiped.swipe('superlike', user.id, sid)

    # 检查对方是否喜欢过你
    if Swiped.is_liked_someone(sid, user.id):
        # 建立好友关系
        Friend.make_friends(user.id, sid)
        # TODO: 向好友推送完成匹配的消息 (集成消息推送服务)

        return True  # 返回完成匹配的结果
    else:
        return False


def rewind(user):
    '''
    每天允许撤销 3 次
    '''
    # 获取当前日期已撤销的次数
    now = datetime.datetime.now()
    key = keys.REWIND_KEY % (user.id, now.date())
    rewind_times = cache.get(key, 0)

    # 次数检查
    if rewind_times < config.REWIND_TIMES:
        rewind_times += 1
        # 计算到晚上凌晨剩余的秒数
        remain_second = 86400 - (now.hour * 3600 + now.minute * 60 + now.second)
        # 添加缓存记录
        cache.set(key, rewind_times, remain_second)
        # 执行撤销操作
        record = Swiped.objects.filter(uid=user.id).latest('stime')
        # 撤销好友记录
        Friend.break_off(user.id, record.sid)

        # 还原积分

        # 直接的思路
        # if record.flag == 'like':
        #     rds.zincrby(keys.HOT_RANK, record.sid, -config.SCORE_LIKE)
        # elif record.flag == 'superlike':
        #     rds.zincrby(keys.HOT_RANK, record.sid, -config.SCORE_SUPERLIKE)
        # else:
        #     rds.zincrby(keys.HOT_RANK, record.sid, -config.SCORE_DISLIKE)

        # 简化版思路
        score_mapping = {'like': -config.SCORE_LIKE,
                         'superlike': -config.SCORE_SUPERLIKE,
                         'dislike': -config.SCORE_DISLIKE}
        rds.zincrby(keys.HOT_RANK, record.sid, score_mapping[record.flag])

        # 前置操作完成后，删除滑动记录
        record.delete()
    else:
        raise errors.RewindLimited('反悔次数达到每日上限')


def get_users_liked_me(user):
    '''获取喜欢过我的用户列表'''
    uid_list = Swiped.liked_me(user.id)
    return User.objects.filter(id__in=uid_list)


def get_top_n(num):
    '''
    获取排名前 N 的用户数据

    Return: {
            '1': {id: 123, nickname: abc, ..., score: 1000}
            '2': {...}
            '3': {...}
            ...
        }
    '''
    # redis 取出的原始数据
    # origin_data = [
    #     [b'12', 15.0],
    #     [b'7', 7.0],
    #     [b'6', 7.0],
    #     ...
    # ]
    origin_data = rds.zrevrange(keys.HOT_RANK, 0, num - 1, withscores=True)

    # cleaned = [
    #     [12, 15],
    #     [7, 7],
    #     [6, 7],
    #     [5, 7],
    #     [4, 7]
    # ]
    cleaned = [[int(uid), int(score)] for uid, score in origin_data]

    uid_list = [uid for uid, _ in cleaned]
    users = User.objects.filter(id__in=uid_list)
    users = sorted(users, key=lambda user: uid_list.index(user.id))

    rank_data = {}
    for rank, (_, score), user in zip(range(1, num + 1), cleaned, users):
        user_attr = user.to_dict()
        user_attr['score'] = score
        rank_data[rank] = user_attr

    return rank_data
