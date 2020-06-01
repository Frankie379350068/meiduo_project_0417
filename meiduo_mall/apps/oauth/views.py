from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
from django.contrib.auth import login
import json, re
from django_redis import get_redis_connection

from apps.oauth.models import OAuthQQUser
from apps.oauth.utils import generate_access_token_openid, check_access_token_openid
from apps.users.models import User

# Create your views here.


class QQUserView(View):
    # 处理授权后的逻辑：用户在 QQ 登录成功后，QQ 会将用户重定向到我们配置的回调网址.
    # 在 QQ 重定向到回调网址时，会传给我们一个 Authorization Code 的参数.
    # 我们需要拿到 Authorization Code 并完成 OAuth2.0 认证获取 openid
    # 回调地址: http: // www.meiduo.site: 8080 / oauth_callback
    def get(self, request):
        # 获取前端发送过来的 code 参数:
        code = request.GET.get('code')
        if not code:
            return http.JsonResponse({'code': 400, 'errmsg': '缺少code参数'})
        # 调用我们安装的 QQLoginTool 工具类
        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        access_tocken = oauth.get_access_token(code)
        openid = oauth.get_open_id(access_tocken)
        # 查询openid所绑定的用户是否存在，也就是table_oath_qq表中的user_id字段是否存在
        # 利用类模型.objects.get()方法来获取open_id所在的记录对象，如果不存在，会抛出 类模型.DoesNotExist 异常。
        try:
            oauth_model = OAuthQQUser.objects.get(openid=openid)
        # 若不存在，则页面重定向到'绑定用户'页面, 注意：重定向到'绑定页面'并不代表用户没注册，只能说明没绑定
        # 工作中，会提供很多状态码，每种状态码前端都会对应一种操作
        # 在美多商城中，如果QQ用户未绑定美多用户，则会返回300状态码，前端会根据需求文档执行相应操作
        except OAuthQQUser.DoesNotExist:
            # 把openid返回给用户自己保存，将来需要保存绑定用户数据的时候，前端再传回给美多商城，access_token是前端先写死了，只能遵守，工作中时后端的的
            access_token_openid = generate_access_token_openid(openid)
            return http.JsonResponse({'code': 300, 'errmsg': '未绑定用户', 'access_token': access_token_openid})

        # 若存在，则页面重定向到美多商城首页，并且做状态保持, 状态保持的是美多商场用户对象(前端通过提取response中的cookie显示在首页上方)
        else:

            login(request=request, user=oauth_model.user)
            response = http.JsonResponse({'code': 0, 'errmsg': 'ok'})
            # oauth_model.user获取到的是外键user关联的用户对象
            response.set_cookie('username', oauth_model.user.username, max_age=14*24*3600)
            return response

    def post(self, request):
        '''实现openid绑定用户的逻辑'''
        # 接收参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')
        sms_code_client = json_dict.get('sms_code')
        access_token = json_dict.get('access_token')
        # 校验参数
        if not all([password, mobile, sms_code_client, access_token]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': '参数password有误'})
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
        # 校验openid
        openid = check_access_token_openid(access_token)
        if not openid:
            return http.JsonResponse({'code': 400, 'errmsg': '参数openid有误'})

        # 判断手机号是否存在, 通过get方法用手机号获取对象
        try:
            user = User.objects.get(mobile=mobile)
        # 如果不存在，新建用户
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        # 如果存在，校验密码
        else:
            if not user.check_password(password):
                return http.JsonResponse({'code': 400, 'errmsg': '密码错误'})
        # 状态保持
        login(request=request, user=user)
        response = http.JsonResponse({'code': 0, 'errmsg': 'OK'})
        response.set_cookie('username', user.username, max_age=14*24*3600)
        # 实现相应结果
        return response

class QQURLView(View):
    """
    GET: http://www.meiduo.site:8080/qq/authorization
    """

    def get(self, request):
        # next 表示从哪个页面进入到的登录页面
        # 将来登录成功后，就自动回到那个页面
        next = request.GET.get('next', '/')
        # 创建oauth对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        # 调用对象的获取 qq 地址方法
        login_url = oauth.get_qq_url()
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'login_url': login_url})

