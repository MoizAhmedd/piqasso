from django.urls import path

from . import views

urlpatterns = [
    path('<int:im_width>/<int:im_height>/<int:norder>/<str:pickle1>/<str:set>', views.homePageView, name = 'generated'),
]
