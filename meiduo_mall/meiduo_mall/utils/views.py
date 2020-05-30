from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

class LoginRequiredJSONMixin(LoginRequiredMixin):
    # 自定义LoginRequiredJSONMixin， 重写LoginRequiredMixin中的方法
    def handle_no_permission(self):
        return http.JsonResponse({'code': 400, 'errmsg': '用户未登录'})