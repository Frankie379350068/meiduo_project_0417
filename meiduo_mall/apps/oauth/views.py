from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
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
        open_id = oauth.get_open_id(access_tocken)
        pass


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

