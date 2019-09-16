from lib.cache import rds
from lib.http import render_json
from common import keys
from swiper import config
from social import logics
from social.models import Swiped
from vip.logics import need_perm


def get_rcmd_users(request):
    users = logics.rcmd_users(request.user)
    data = [user.to_dict() for user in users]  # 封装要返回的数据
    return render_json(data)


def like(request):
    '''喜欢'''
    sid = int(request.POST.get('sid'))
    matched = logics.like(request.user, sid)
    rds.zincrby(keys.HOT_RANK, sid, config.SCORE_LIKE)
    return render_json({'is_matched': matched})


@need_perm('superlike')
def superlike(request):
    '''超级喜欢'''
    sid = int(request.POST.get('sid'))
    matched = logics.superlike(request.user, sid)
    rds.zincrby(keys.HOT_RANK, sid, config.SCORE_SUPERLIKE)
    return render_json({'is_matched': matched})


def dislike(request):
    '''不喜欢'''
    sid = int(request.POST.get('sid'))
    Swiped.swipe('dislike', request.user.id, sid)
    rds.zincrby(keys.HOT_RANK, sid, config.SCORE_DISLIKE)
    return render_json(None)


@need_perm('rewind')
def rewind(request):
    '''
    反悔

    客户端传来的东西都是不可信的，所有参数都要经过检查, 能不依赖客户端参数时尽量不依赖
    '''
    logics.rewind(request.user)
    return render_json(None)


@need_perm('show_liked_me')
def show_liked_me(request):
    '''查看喜欢过我的人'''
    users = logics.get_users_liked_me(request.user)
    data = [user.to_dict() for user in users]
    return render_json(data)


def friends(request):
    my_friends = request.user.friends
    data = [friend.to_dict() for friend in my_friends]
    return render_json(data)


def hot_users(request):
    '''
    全服最火的 10 名用户

    Return: {
            '1': {id: 123, nickname: abc, ..., score: 1000}
            '2': {...}
            '3': {...}
            ...
        }
    '''
    rank_data = logics.get_top_n(10)
    return render_json(rank_data)
