from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('vote/', views.VoteView.as_view(), name='vote'),
    path('root/', views.AdminView.as_view(), name='admin'),
]
