from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth urls
    path("", include("apps.authentication.urls")),

    path("", include("apps.dashboard.urls")),
    

]

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)
