from django.urls import path
from . import views

urlpatterns = [
    # 判断用户名是否重复注册 GET /usernames/itcast/count/
    # path('usernames/itcast/count/', views.UsernameCountView.as_view()),
    # path('usernames/<'匹配用户名的路由转换器:变量'>/count/', views.UsernameCountView.as_view()),
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 用户注册地址: /register/
    path('register/', views.RegisterView.as_view()),
    # 用户登录地址: www.meiduo.site:8000/login/
    path('login/', views.LoginView.as_view()),
    # 用户退出登录地址: www.meiduo.site:8000/logout/
    path('logout/', views.LogoutView.as_view()),
    # 用户个人信息地址: www.meiduo.site:8000/info/
    path('info/', views.UserInfoView.as_view()),
    # 用户添加邮箱地址: www.meiduo.site:8000/email/
    path('emails/', views.EmailsView.as_view()),
    # 邮箱激活地址 www.meiduo.site: 8000/emails/verification/
    path('emails/verification/', views.EmailVerifyView.as_view()),
    # 新增地址:POST http://www.meiduo.site:8000/addresses/create/
    path('addresses/create/', views.CreateAddressView.as_view()),
    # 获取收货地址:GET http://www.meiduo.site:8000/addresses/
    path('addresses/', views.AddressView.as_view()),
]