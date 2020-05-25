from django.shortcuts import render
from django.views import View
from django import http
import logging

from .models import User

# Create your views here.
# 日志输出器
logger = logging.getLogger('django')

class UsernameCountView(View):
    ''' 判断用户名是否重复注册
    GET /usernames/itcast/count/
    '''
    def get(self, request, username):
        '''查询用户名记录的个数'''
        # :param username:用户名
        # :return Json
        # 模型类.objects.filter().count()
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code':'400', 'errmsg':'数据错误'})

        return http.JsonResponse({'code':'0', 'errmsg':'ok', 'count':count})
