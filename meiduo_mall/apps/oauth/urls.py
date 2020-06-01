from django.urls import path
from . import views

urlpatterns = [
    # /qq/authorization
    path('qq/authorization/', views.QQURLView.as_view()),
    # 回调地址: http: // www.meiduo.site: 8000 / oauth_callback
    path('oauth_callback/', views.QQUserView.as_view()),

]