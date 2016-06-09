from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^terminal/$', views.terminal, name='terminal'),
    url(r'^terminal/save$', views.terminal_save, name='terminal_save'),
    url(r'^terminal/add$', views.terminal_add, name='terminal_add'),
    url(r'^terminal/edit/(?P<terminal_id>[0-9]+)/$', views.terminal_edit, name='terminal_edit'),
    url(r'^terminal/delete/(?P<terminal_id>[0-9]+)/$', views.terminal_delete, name='terminal_delete')
]