from django.urls import path
from . import views


urlpatterns = [
    # GET 请求http://www.meiduo.site:8000/image_codes/550e8400-e29b-41d4-a716-446655440000/
    path('image_codes/<uuid:uuid>/', views.ImageCodeView.as_view()),
]