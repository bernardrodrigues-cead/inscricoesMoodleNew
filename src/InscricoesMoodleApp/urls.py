from django.urls import path
from InscricoesMoodleApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.thanks, name='thanks'),
    path('cadastro/aluno', views.CadastroAlunoCreateView.as_view(), name='aluno_cadastro'),
    path('cadastro/curso', views.CadastroCursoCreateView.as_view(), name='curso_cadastro'),
]