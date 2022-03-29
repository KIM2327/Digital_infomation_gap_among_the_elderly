from django.urls import path
from . import views

# 시작페이지 주소와 뷰 함수 연결하기
urlpatterns = [
    path('', views.home),
    path('lessons/<str:loc>/<int:pg>', views.lessons),
    path('lessons/<str:loc>/<int:pg>/<int:num>', views.detail),
]
