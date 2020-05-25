from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # 自定义用户模型类
    # 增加mobile字段 字符串类型，最长11位，唯一不重复
    mobile = models.CharField(max_length=11, unique=True)
    # 给表起名
    class Meta:
        db_table = 'tb_users'