import csv, json, os
from django.http import FileResponse

from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView
from InscricoesMoodleApp.forms import AlunosForm, CursosForm
from InscricoesMoodleApp.utils import PasswdGen, SendEmail
from InscricoesMoodleApp.models import Curso, DadosDoAluno
from django.db import models
from django.db.models import Case, When
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    return render(request, 'index.html')

@login_required(login_url='/inscricoes_critt/accounts/login/')
def Administracao(request):
    return render(request, 'administracao.html')

class CadastroAlunoCreateView(CreateView):
    form_class = AlunosForm
    template_name = 'form_aluno.html'
    success_url = '/inscricoes_critt/thanks'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flag_curso_list = []
        for curso in Curso.objects.all():
            if curso.anexar_documentacao:
                flag_curso_list.append(curso.id)
        context['flag_curso_list'] = flag_curso_list
        if len(Curso.objects.filter(ativo=True)) > 0:
            context['has_curso'] = True
        return context
    
    def form_valid(self, form):
        if form.cleaned_data['email'] != form.cleaned_data['email_confirmacao']:
            messages.error(self.request, "Campos de e-mail diferentes")
            return self.form_invalid(form)

        pwd = PasswdGen()
        senha = pwd.run()
        new_data = form.save(commit=False)
        # Atualização dos dados com máscara para que contenham apenas numerais
        new_data.telefone = form.cleaned_data['telefone'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        new_data.cpf = form.cleaned_data['cpf'].replace('.', '').replace('-', '')
        new_data.cep = form.cleaned_data['cep'].replace('-', '')
        new_data.senha_inicial = senha
        
        # Formatação do diretório e do arquivo PDF que será armazenado
        dir_name = form.cleaned_data['curso'].data_inicio.strftime('%Y%m%d') + "_" + form.cleaned_data['curso'].nome_breve
        file_name = form.cleaned_data['nome'] + "_" + form.cleaned_data['sobrenome'] + ".pdf"
        if new_data.documentacao:
            if not os.path.isdir('uploads/' + dir_name):
                os.mkdir('uploads/' + dir_name)
            new_data.documentacao.name = dir_name + '/' + file_name
        
        new_data.save()

        ### SEND EMAIL ###
        subject = "CEAD | UFJF - Orientações para Acesso à Plataforma Moodle"
        
        message = """
        Prezado(a),

        Bem-vindo(a) ao Cead UFJF!
        Você foi inscrito(a) no curso {}. 
        Ao final das inscrições, para acessar sua conta na plataforma Moodle, verifique as informações abaixo:

        Acesse: http://ead.cead.ufjf.br (ao final do período de inscrição)
        Identificação: {}
        Senha: {}

        Em caso de dúvidas referentes à plataforma, entre em contato com suporte.cead@ufjf.br
        Para demais informações, entre em contato com a coordenação do curso.

        Atenciosamente,
        SAUT - Serviço de Atendimento ao Usuário
        Coordenação Tecnológica - CEAD | UFJF

        """.format(form.cleaned_data['curso'], form.cleaned_data['cpf'].replace('.', '').replace('-', ''), senha)

        recipients = [form.cleaned_data['email']]

        new_email = SendEmail(subject=subject, message=message, recipients=recipients)
        # new_email.send()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, str(form.errors.as_data()))
        return super().form_invalid(form)
        
def thanks(request):
    return render(request, 'thanks.html')

class CadastroCursoCreateView(LoginRequiredMixin, CreateView):
    login_url = "/inscricoes_critt/accounts/login"
    form_class = CursosForm
    template_name = "form_curso.html"
    success_url = "/inscricoes_critt/"

    def form_valid(self, form):
        if(form.cleaned_data['data_inicio'] > form.cleaned_data['data_fim']):
            messages.error(self.request, 'A data de encerramento das atividades deve ser posterior à data de início.')
            return self.form_invalid(form)
        
        if(form.cleaned_data['matricula_inicio'] > form.cleaned_data['matricula_fim']):
            messages.error(self.request, 'A data de encerramento das inscrições deve ser posterior à data de início.')
            return self.form_invalid(form)
        
        if(form.cleaned_data['data_inicio'] < form.cleaned_data['matricula_fim']):
            messages.error(self.request, 'A data de início das atividades deve ser posterior ao encerramento das inscrições.')
            return self.form_invalid(form)
        
        messages.success(self.request, "Curso cadastrado com sucesso")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors.as_data())
        messages.success(self.request, form.errors.as_data())
        return super().form_invalid(form)
    
class CursoListView(LoginRequiredMixin, ListView):
    login_url = "/inscricoes_critt/accounts/login"
    model = Curso
    template_name = 'list_curso.html'
    context_object_name = 'cursos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.all().order_by('nome')
        context['now'] = timezone.now()
        return context
    
class CursoDetailView(LoginRequiredMixin, DetailView):
    model = Curso
    context_object_name = 'curso'
    template_name = 'detail_curso.html'
    login_url = "/inscricoes_critt/accounts/login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['inscritos'] = obj.dadosdoaluno_set.annotate(
            # ordena nessa ordem
            custom_order=Case(
                When(status='W', then=0),
                When(status='A', then=1),
                When(status='R', then=2),
                default=None,
                output_field=models.IntegerField()
            )
        ).order_by('custom_order', 'nome')
        context['now'] = timezone.now()
        return context
    
class InscritoDetailView(LoginRequiredMixin, UpdateView):
    model = DadosDoAluno
    fields = ['status']
    context_object_name = 'aluno'
    template_name = 'update_aluno.html'
    login_url = "/inscricoes_critt/accounts/login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.object
        return context
    
    def form_valid(self, form):
        messages.success(self.request, "Status de inscrição atualizado com sucesso")
        self.object.status = form.cleaned_data['status']
        self.object.save(update_fields = ['status'])
        return redirect('curso_detail', self.object.curso.id)
    
def download_csv_file(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    aprovados = curso.dadosdoaluno_set.filter(status='A')
    
    if(not aprovados):
        messages.error(request, "Nenhum candidato aprovado até a presente dada")
        return redirect('curso_detail', curso.id)

    header = (
        'username', 
        'password', 
        'firstname', 
        'lastname',
        'email',
        'city',
        'auth',
        'course1'
    )


    # Escrita do arquivo .csv
    dir_path = os.path.join(settings.MEDIA_ROOT, 'outputs')
    
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    file_path = dir_path + '/' + aprovados.last().curso.nome_breve + aprovados.last().curso.data_inicio.strftime('%Y%m%d') + '.csv'

    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for aprovado in aprovados:
            writer.writerow({
                'username': aprovado.cpf,
                'password': aprovado.senha_inicial,
                'firstname': aprovado.nome,
                'lastname': aprovado.sobrenome,
                'email': aprovado.email,
                'city': aprovado.cidade,
                'auth': 'manual',
                'course1': aprovado.curso.nome_breve
            })

    f.close()

    return FileResponse(open(file_path, 'rb'))

def download_csv_ordenado(request, curso_id, ordem):
    curso = Curso.objects.get(id=curso_id)
    if ordem == 'alfabetica':
        aprovados = curso.dadosdoaluno_set.filter(status='A').order_by('sobrenome').order_by('nome')
    elif ordem == 'inscritos':
        aprovados = curso.dadosdoaluno_set.filter(status='A').order_by('data_cadastro')
    
    if(not aprovados):
        messages.error(request, "Nenhum candidato aprovado até a presente dada")
        return redirect('curso_detail', curso.id)

    header = (
        'cpf',
        'data_nascimento',
        'nome',
        'sobrenome',
        'email',
        'curso',
        'cidade',
        'telefone',
        'cep',
        'logradouro',
        'numero',
        'complemento',
        'bairro',
        'uf',
        'siga',
        'documentacao',
        'secretaria',
        'cargo',
        'matricula',
        'data_cadastro'
    )


    # Escrita do arquivo .csv
    dir_path = os.path.join(settings.MEDIA_ROOT, 'outputs')
    
    if not os.path.isdir(dir_path):
        os.mkdir(dir_path)

    file_path = dir_path + '/' + aprovados.last().curso.nome_breve + aprovados.last().curso.data_inicio.strftime('%Y%m%d') + ordem + '.csv'

    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for aprovado in aprovados:
            writer.writerow({
                'cpf': aprovado.cpf,
                'data_nascimento': aprovado.data_nascimento,
                'nome': aprovado.nome,
                'sobrenome': aprovado.sobrenome,
                'email': aprovado.email,
                'curso': aprovado.curso,
                'cidade': aprovado.cidade,
                'telefone': aprovado.telefone,
                'cep': aprovado.cep,
                'logradouro': aprovado.logradouro,
                'numero': aprovado.numero,
                'complemento': aprovado.complemento,
                'bairro': aprovado.bairro,
                'uf': aprovado.uf,
                'siga': aprovado.siga,
                'documentacao': aprovado.documentacao,
                'secretaria': aprovado.secretaria,
                'cargo': aprovado.cargo,
                'matricula': aprovado.matricula,
                'data_cadastro': aprovado.data_cadastro.strftime("%d/%m/%Y %H:%M:%S")
            })

    f.close()

    return FileResponse(open(file_path, 'rb'))

