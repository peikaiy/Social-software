from django.db import models
from django.core.cache import cache


def to_dict(self):
    '''创建模型的属性字典'''
    attr_dict = {}
    for field in self._meta.get_fields():
        name = field.attname
        attr_dict[name] = getattr(self, name)
    return attr_dict


@classmethod
def get(cls, *args, **kwargs):
    '''对 objects.get 做一层封装，添加缓存处理'''
    pk = kwargs.get('pk') or kwargs.get('id')
    if pk is not None:
        # 先从缓存获取
        key = 'Model-%s-%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        if model_obj is not None:
            return model_obj

    # 从数据库获取 model 对象
    model_obj = cls.objects.get(*args, **kwargs)

    # 将取出的对象写入缓存
    key = 'Model-%s-%s' % (cls.__name__, model_obj.pk)
    cache.set(key, model_obj, 86400 * 14)

    return model_obj


@classmethod
def get_or_create(cls, *args, **kwargs):
    pk = kwargs.get('pk') or kwargs.get('id')
    if pk is not None:
        # 先从缓存获取
        key = 'Model-%s-%s' % (cls.__name__, pk)
        model_obj = cache.get(key)
        if model_obj is not None:
            return model_obj

    # 从数据库获取或创建 model 对象
    model_obj, created = cls.objects.get_or_create(*args, **kwargs)

    # 将取出的对象写入缓存
    key = 'Model-%s-%s' % (cls.__name__, model_obj.pk)
    cache.set(key, model_obj, 86400 * 14)

    return model_obj, created


def save(self, force_insert=False, force_update=False, using=None,
            update_fields=None):
    '''对原 save 做封装，添加更新缓存处理'''
    # 将 model 对象添加到缓存
    key = 'Model-%s-%s' % (self.__class__.__name__, self.pk)
    cache.set(key, self, 86400 * 14)

    # 使用原生 save 方法保存到数据库
    self._origin_save()


def patch_model():
    '''通过 Monkey Patch 的方式给原生的 Model 打补丁'''
    # 给 Model 增加一些方法
    models.Model.to_dict = to_dict
    models.Model.get = get
    models.Model.get_or_create = get_or_create

    # 修改原生的 save
    models.Model._origin_save = models.Model.save
    models.Model.save = save
