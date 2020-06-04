from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
from meiduo_mall.utils.BaseModel import BaseModel


class User(AbstractUser):
    # 自定义用户模型类
    # 增加mobile字段 字符串类型，最长11位，唯一不重复
    mobile = models.CharField(max_length=11, unique=True)
    # 追加email_active字段
    email_active = models.BooleanField(default=False, verbose_name='激活状态')
    # 给用户表追加默认收货地址default_address
    default_address = models.ForeignKey('Address', related_name='users', on_delete=models.SET_NULL, null=True, verbose_name='用户地址')

    # 给表起名
    class Meta:
        db_table = 'tb_users'

# 增加地址的模型类, 放到User模型类的下方:
class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='addresses',
                             verbose_name='用户')

    province = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='province_addresses',
                                 verbose_name='省')

    city = models.ForeignKey('areas.Area',
                             on_delete=models.PROTECT,
                             related_name='city_addresses',
                             verbose_name='市')

    district = models.ForeignKey('areas.Area',
                                 on_delete=models.PROTECT,
                                 related_name='district_addresses',
                                 verbose_name='区')

    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,
                           null=True,
                           blank=True,
                           default='',
                           verbose_name='固定电话')

    email = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             default='',
                             verbose_name='电子邮箱')

    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        ordering = ['-update_time']