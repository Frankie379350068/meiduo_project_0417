from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from django import http

# Create your views here.


class SubsAreasView(View):
    # 查询父级下属地址: http://www.meiduo.site:8000/areas/(?P<pk>[1-9]\d+)/
    def get(self, request, parentid):
        # 通过id找到满足条件的地区，如id是140000，则对应找到的是山西省
        parent_area = Area.objects.get(id=parentid)
        # 一查多，父级对应多个子级， 如省下有多个市，市下有多个区,  模型类对象.模型类类名小写_set.all()
        # sub_model_list = parent_area.area_set.all(), 因为Area模型类中有relate_name=subs，所以该方法不能用
        sub_model_list = parent_area.subs.all()
        subs = []
        for sub_model in sub_model_list:
            sub_dict = {
                'id': sub_model.id,
                'name': sub_model.name,
            }
            subs.append(sub_dict)
        sub_data = {
            'id': parent_area.id,
            'name': parent_area.name,
            'subs': subs,
        }
        return http.JsonResponse({'code': 0, 'errmsg': 'ok', 'sub_data': sub_data})



class ProvinceAreasView(View):
    # 查询省份地址: http://www.meiduo.site:8000/areas/

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


