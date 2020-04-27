from django.urls import path
from . import views

app_name = 'eithers'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create'),
    path('<int:vote_pk>/', views.detail, name='detail'),
    path('<int:vote_pk>/comments/', views.comment_create, name='comment_create'),
    path('random_vote/', views.random_vote, name='random_vote'),
]