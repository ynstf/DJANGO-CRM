from django.urls import path
from .views import AuthView, disconnect
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path(
        "",
        AuthView.as_view(template_name="auth_login_basic.html"),
        name="login",

    ),
    
    # Add the following line for logout
    #path('logout/', LogoutView.as_view(), name='logout'),
    path('logout/', disconnect, name='logout'),
    path('disconnect/', LogoutView.as_view(), name='disconnect'),

]
