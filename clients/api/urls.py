from django.urls import path, include
from . import views
from rest_framework import routers

app_name = 'clients'

router = routers.DefaultRouter()
router.register('clients', views.ClientViewSet)

urlpatterns = [
    path('categories/',
        views.CategoryListView.as_view(),
        name='category_list'),

    path('categories/<pk>/',
        views.CategoryDetailView.as_view(),
        name='category_detail'),
        
    path('clients/<pk>/enroll/',
     views.ClientEnrollView.as_view(),
     name='client_enroll'),

    path('', include(router.urls)),

]