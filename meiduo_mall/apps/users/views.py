from django.shortcuts import render
from django.views import View
from django import http
import logging, json
import re
from django.contrib.auth import login, authenticate, logout
from .models import User
from django_redis import get_redis_connection

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_email_verify_url
from apps.users.utils import generate_verify_email_url, check_verify_email_url

# Create your views here.
# 日志输出器
logger = logging.getLogger('django')


class EmailVerifyView(View):
    # 验证激活接口设计
    # 邮箱激活地址 www.meiduo.site: 8080/emails/verification/
    def put(self, request):
        # 接收参数token，并提取
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.JsonResponse({'code': 400, 'errmsg': 'token参数缺失'})
        # 把email_active设置激活
        user = check_verify_email_url(token)
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': 'email激活失败'})
        return http.JsonResponse({'code': 0, 'errmsg': 'ok'})


class EmailsView(View):
    # 发送验证激活邮件地址:  www.meiduo.site:8080/email/
    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        if not email:
            return http.JsonResponse({'code': 400,
                                      'errmsg': '缺少email参数'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({'code': 400, 'errmsg': '邮箱格式有误'})
        # 把email用赋值法写入数据库
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '添加邮箱失败'})
        # 发送邮箱验证激活邮件给转发邮件的中间人，比如网易邮箱
        # 调用自定义的发送函数send_email_verify_url.delay(email, '激活连接')
        verify_url = generate_verify_email_url(request.user)
        send_email_verify_url.delay(email, verify_url)
        return http.JsonResponse({'code': 400, 'errmsg': 'ok'})


class UserInfoView(LoginRequiredJSONMixin, View):
    # 如果未登录，返回400状态码，errmsg为'用户未登录'数据给前端
    # 如果登录，继续分发请求
    # 小技巧: 如果该接口只有登录用户能够访问， 则可以通过request.user获取到当前登录用户的信息
    def get(self, request):
        json_dict = {'code': 0,
                     'errmsg': 'ok',
                     'info_data': {
                         'username': request.user.username,
                         'mobile': request.user.mobile,
                         'email': request.user.email,
                         'email_active': request.user.email_active}
                     }
        return http.JsonResponse(json_dict)


class LogoutView(View):
    def delete(self, request):
        # 清除登录状态,清楚服务端的session
        logout(request)
        # 响应对象
        response = http.JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


class LoginView(View):
    def post(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        account = json_dict.get('username')
        password = json_dict.get('password')
        # True==False，可真可假，可传可不传
        remembered = json_dict.get('remembered')

        # 校验参数
        if not all([account, password]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # if not re.match(r'^[0-9A-Za-z_-]{5,20}$', account):
        #     return http.JsonResponse({'code':400, 'errmsg':'用户名username格式错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '密码password格式错误'})

        # 实现多账号登录
        # 判断用户输入的是用户名还是手机号
        if re.match(r'^1[3-9]\d{9}$', account):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'

        # 核心业务逻辑
        # 核心思想：先判断用户名在数据库中是否存在，如果不存在则返回，存在则校验密码是否正确
        # django封装的authenticate()只是证明该用户是注册用户，且密码没错，但是并不代表登录是它执行的
        user = authenticate(request=request, username=account, password=password)
        if not user:
            # 一定要写'用户名或者密码错误', 不能把真实的情况告诉用户，安全性考虑！
            return http.JsonResponse({'code': 400, 'errmsg': '用户名或者密码错误'})
        # 实现状态保持
        login(request, user)
        # 依据remembered的值来设置session状态保持周期
        # 如果用户选择了'记住登录状态'，则默认保持两周，否则在浏览器会话结束后，状态保持就销毁
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        # 创建响应对象，写入cookie
        response = http.JsonResponse({'code': 0, 'errmsg': '登录成功'})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        # 响应结果
        return response


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
        try:  # create_user()有返回值 return user, 可以整一个变量保存
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': 400, 'errmsg': '注册失败'})

        # 实现状态保持：用户注册成功即登录成功
        login(request, user)
        # 创建响应对象，写入cookie
        response = http.JsonResponse({'code': 0, 'errmsg': '登录成功'})
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        # 响应结果, 如果注册成功，前端会引导到首页，引导代码是前端写的
        return response


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
