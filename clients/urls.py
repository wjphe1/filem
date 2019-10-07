from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'login_success/$', views.login_success, name='login_success'),
     path('mine/', views.ManageClientListView.as_view(), name='manage_client_list'),
     path('create/', views.ClientCreateView.as_view(), name='client_create'),
     path('<pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
     path('<pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
     path('<pk>/module/', views.ClientModuleUpdateView.as_view(), name='client_module_update'),
     path('module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(), name='module_content_create'),
     path('module/<int:module_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(), name='module_content_update'),
     path('module/<int:module_id>/', views.ModuleContentListView.as_view(), name='module_content_list'),
     path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),
     path('module/order/', views.ModuleOrderView.as_view(), name='module_order'),
     path('content/order/', views.ContentOrderView.as_view(), name='content_order'),
     path('category/<slug:category>)/', views.ClientListView.as_view(), name='client_list_category'),
     path('<slug:slug>/', views.ClientDetailView.as_view(), name='client_detail'),
]