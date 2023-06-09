from django.urls import path
from InscricoesMoodleApp import views

urlpatterns = [
    path('', views.index, name='index'),
    path('thanks/', views.thanks, name='thanks'),
    path('aluno/cadastro/', views.CadastroAlunoCreateView.as_view(), name='aluno_cadastro'),
    path('aluno/<int:pk>/', views.InscritoDetailView.as_view(), name='aluno_detail'),
    path('curso/cadastro/', views.CadastroCursoCreateView.as_view(), name='curso_cadastro'),
    path('curso/lista/', views.CursoListView.as_view(), name='curso_lista'),
    path('curso/<int:pk>/', views.CursoDetailView.as_view(), name='curso_detail'),
    path('administracao/', views.Administracao, name='administracao'),

    path('download_csv/<int:curso_id>/', views.download_csv_file, name="download_csv"),
    path('download_csv/<int:curso_id>/<str:ordem>', views.download_csv_ordenado, name="download_csv_ordenado"),
    path('download_csv/<int:curso_id>/<str:ordem>/<int:cidade>', views.download_csv_cidade, name="download_csv_cidade")
]