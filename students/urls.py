from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('staff_register/', views.staff_register, name='staff_register'),
    path('register/', views.StudentRegistrationView.as_view(), name='student_registration'), 
    path('enroll-client/', views.StudentEnrollClientView.as_view(), name='student_enroll_client'),
    path('clients/', views.StudentClientListView.as_view(), name='student_client_list'),
    path('client/<pk>/', views.StudentClientDetailView.as_view(), name='student_client_detail'),
    path('client/<pk>/<module_id>/', views.StudentClientDetailView.as_view(), name='student_client_detail_module'),
]