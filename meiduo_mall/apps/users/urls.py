from django.urls import path
from . import views

urlpatterns = [
    # 判断用户名是否重复注册 GET /usernames/itcast/count/
    # path('usernames/itcast/count/', views.UsernameCountView.as_view()),
    # path('usernames/<'匹配用户名的路由转换器:变量'>/count/', views.UsernameCountView.as_view()),
    path('usernames/<username:username>/count/', views.UsernameCountView.as_view()),
    # 用户注册地址: /register/
    path('register/', views.RegisterView.as_view()),
    # 用户登录地址: www.meiduo.site:8080/login/
    path('login/', views.LoginView.as_view()),
    # 用户退出登录地址: www.meiduo.site:8080/logout/
    path('logout/', views.LogoutView.as_view()),
    # 用户退出登录地址: www.meiduo.site:8080/info/
    path('info/', views.UserInfoView.as_view()),
]