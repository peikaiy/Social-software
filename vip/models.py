from django.db import models


class Vip(models.Model):
    '''VIP表'''
    name = models.CharField(max_length=32, unique=True, verbose_name='会员等级对应的名称')
    level = models.IntegerField(verbose_name='VIP 等级')
    price = models.FloatField(verbose_name='会员等级对应的价格')

    class Meta:
        ordering = ['level']

    @property
    def perms(self):
        '''取出当前 VIP 拥有的所有权限'''
        relations = VipPermRelation.objects.filter(vip_id=self.id)
        perm_id_list = [rlt.perm_id for rlt in relations]
        return Permission.objects.filter(id__in=perm_id_list)

    def has_perm(self, perm_name):
        '''检查当前 VIP 是否拥有某权限'''
        for perm in self.perms:
            if perm.name == perm_name:
                return True
        return False


class Permission(models.Model):
    '''权限表'''
    name = models.CharField(max_length=16, unique=True, verbose_name='权限名称')
    desc = models.TextField(verbose_name='对权限的描述')


class VipPermRelation(models.Model):
    '''Vip 和 权限 的关系表'''
    vip_id = models.IntegerField()
    perm_id = models.IntegerField()
