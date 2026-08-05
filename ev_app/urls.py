from django.urls import path
from . import views

urlpatterns = [
    path("",               views.index,        name="index"),
    path("upload/",        views.upload,        name="upload"),
    path("dashboard/",     views.dashboard,     name="dashboard"),
    path("api/data/",      views.api_data,      name="api_data"),
    path("export/excel/",  views.export_excel,  name="export_excel"),
    path("export/pdf/",    views.export_pdf,    name="export_pdf"),
]
