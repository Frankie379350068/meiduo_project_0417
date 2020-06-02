from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django import http

# Create your views here.

class ProvinceAreasView(View):
    # 用户添加邮箱地址: http://www.meiduo.site:8080/areas/

    def get(self, request):
        # 查询省份数据
        province_model_list = Area.objects.filter(parent=None)
        # 定义一个省份空列表
        province_dict_list = []
        # 遍历查询集合
        for province_model in province_model_list:
            province_dict = {
                'id': province_model.id ,
                'name': province_model.name,
            }
            province_dict_list.append(province_dict)
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'province_list': province_dict_list})


