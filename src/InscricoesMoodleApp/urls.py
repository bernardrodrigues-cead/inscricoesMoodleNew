from django.urls import path
from InscricoesMoodleApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.thanks, name='thanks'),
    path('aluno/cadastro/', views.CadastroAlunoCreateView.as_view(), name='aluno_cadastro'),
    path('curso/cadastro/', views.CadastroCursoCreateView.as_view(), name='curso_cadastro'),
    path('curso/lista/', views.CursoListView.as_view(), name='curso_lista'),
    path('curso/<int:pk>/', views.CursoDetailView.as_view(), name='curso_detail'),
    path('administracao/', views.Administracao, name='administracao'),
]