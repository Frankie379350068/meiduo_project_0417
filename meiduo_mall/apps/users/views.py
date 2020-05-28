from django.shortcuts import render
from django.views import View
from django import http
import logging, json
import re
from django.contrib.auth import  login
from .models import User
from django_redis import get_redis_connection

# Create your views here.
# 日志输出器
logger = logging.getLogger('django')


class RegisterView(View):
    '''用户注册地址
    GET /register/
    '''

    def post(self, request):
        # 接收参数
        # 获取json数据，并转换成字典格式
        json_bytes = request.body
        json_str = json_bytes.decode()
        json_dict = json.loads(json_str)
        # 提取参数
        username = json_dict.get('username')
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        mobile = json_dict.get('mobile')
        allow = json_dict.get('allow')
        # 提取短信验证码参数
        sms_code_client = json_dict.get('sms_code')

        # 校验参数
        # 判断是否缺少必传参数，即上述五个数据不能有空值
        # all()方法判断是否缺少必传参数，底层封装好的方法
        if not all([username, password, password2, mobile, allow]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 判断用户名格式是否满足要求，防止用户乱写
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.JsonResponse({'code': 400, 'errmsg': '参数username有误'})
        # 判断用户名的密码格式是否符合要求
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '参数password有误'})
        # 判断两次输入的密码是否一致
        if password != password2:
            return http.JsonResponse({'code': 400, 'errmsg': '两次密码输入不一致'})
        # 判断手机号码是否满足要求
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})
        # 判断是否同意用户协议
        if allow != True:
            return http.JsonResponse({'code': 400, 'errmsg': '参数allow有误'})
        # 判断短信验证码是否正确
        # 提取服务端存储的短信验证码
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断服务器端的短信验证码是否过期
        if not sms_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码过期'})
        # 从redis提取出来的数据一定要由bytes类型转换为str类型再比较
        if sms_code_client != sms_code_server.decode():
            return http.JsonResponse({'code': 400, 'errmsg': '短信验证码有误'})

        # 实现核心逻辑：保存用户注册数据到数据表
        # 模型类.objects.create_user()进行数据添加，如果用create()需要自己设置默认值，密码需要自己加密
        try: # create_user()有返回值 return user, 可以整一个变量保存
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '注册失败'})

        # 实现状态保持：用户注册成功即登录成功
        login(request, user)

        # 响应结果, 如果注册成功，前端会引导到首页，引导代码是前端写的
        return http.JsonResponse({'code': 0, 'errmsg': '注册成功'})


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
            return http.JsonResponse({'code': '400', 'errmsg': '数据错误'})

        return http.JsonResponse({'code': '0', 'errmsg': 'ok', 'count': count})
