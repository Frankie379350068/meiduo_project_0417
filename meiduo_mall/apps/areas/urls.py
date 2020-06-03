from django.urls import path
from . import views

urlpatterns = [
    # 查询省份地址: http://www.meiduo.site:8000/areas/
    path('areas/', views.ProvinceAreasView.as_view()),
    # 查询父级下属地址: http://www.meiduo.site:8000/areas/(?P<pk>[1-9]\d+)/
    path('areas/<int:parentid>/', views.SubsAreasView.as_view()),
]