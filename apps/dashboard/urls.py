from django.urls import path
from .views import dashboard,add_customer,customer_list,customer_info


urlpatterns = [
    path("dashboard/",dashboard,name="dashboard",),
    path('add_customers/', add_customer, name='add_customer'),
    path('customer_list/', customer_list, name='customer_list'),
    path('customer/<int:id>', customer_info, name='customer_info'),

]
