from django.urls import path

from . import views

urlpatterns = [
               path('<int:im_width>/<int:im_height>/<int:norder>/<str:pickle1>/<str:set>/<str:state>', views.homePageView, name = 'generated'),
    path('test', views.test, name='test'),
]
