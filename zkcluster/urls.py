from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^terminal/$', views.terminal, name='terminal'),
    url(r'^terminal/scan$', views.terminal_scan, name='terminal_scan'),
    url(r'^terminal/add$', views.terminal_add, name='terminal_add')
]