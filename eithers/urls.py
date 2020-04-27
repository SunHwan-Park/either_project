from django.urls import path
from . import views

app_name = 'eithers'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:vote_pk>/', views.detail, name='detail'),
    path('<int:vote_pk>/comments/', views.comment_create, name='comment_create'),
    path('<int:vote_pk>/selectitem/', views.selectitem, name='selectitem'),
]
