from django.urls import path
from .views import dashboard,add_customer,customer_list,customer_info,edit_customer


urlpatterns = [
    path("dashboard/",dashboard,name="dashboard",),
    path('add_customers/', add_customer, name='add_customer'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer/<int:id>', customer_info, name='customer_info'),
    path('customer/<int:id>/edit/', edit_customer, name='edit_customer'),

]
