# Celery的入口文件
from celery import Celery
# 在创建实例之前，把Django的配置文件加载到celery运行环境中
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
# 创建Celery实例
# Celery（‘别名’）
celery_app = Celery('meiduo')

# 加载配置
# celery_app.config_from_object('配置文件')
celery_app.config_from_object('celery_tasks.config')

# 注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])

