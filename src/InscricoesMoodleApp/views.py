import csv, json, os

from django.shortcuts import render
from django.contrib import messages
from django.views.generic.edit import CreateView
from InscricoesMoodleApp.forms import AlunosForm, CursosForm
from InscricoesMoodleApp.utils import PasswdGen, SendEmail
from InscricoesMoodleApp.models import Curso
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    return render(request, 'index.html')

class CadastroAlunoCreateView(CreateView):
    form_class = AlunosForm
    template_name = 'form_aluno.html'
    success_url = '/thanks'
    
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
        new_data = form.save(commit=False)
        # Atualização dos dados com máscara para que contenham apenas numerais
        new_data.telefone = form.cleaned_data['telefone'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
        new_data.cpf = form.cleaned_data['cpf'].replace('.', '').replace('-', '')
        new_data.cep = form.cleaned_data['cep'].replace('-', '')
        
        # Formatação do diretório e do arquivo PDF que será armazenado
        dir_name = form.cleaned_data['curso'].data_inicio.strftime('%Y%m%d') + "_" + form.cleaned_data['curso'].nome_breve
        file_name = form.cleaned_data['nome'] + "_" + form.cleaned_data['sobrenome'] + ".pdf"
        if new_data.documentacao:
            if not os.path.isdir('uploads/' + dir_name):
                os.mkdir('uploads/' + dir_name)
            new_data.documentacao.name = dir_name + '/' + file_name
        
        new_data.save()
        
        self.request.session['dados_aluno'] = new_data.id

        # Criação do nome do arquivo com base nos dados do curso
        data_matricula = form.cleaned_data['curso'].matricula_inicio.strftime('%d%m%y')
        nome = form.cleaned_data['curso'].nome
        nome_breve = form.cleaned_data['curso'].nome_breve
        
        if not os.path.isdir('outputs/' + dir_name):
            os.mkdir('outputs/' + dir_name)
        filename = 'outputs/' + dir_name + '/' + nome + '_' + data_matricula

        # Atualização dos campos do dicionário para a formatação de interesse 
        form.cleaned_data['curso'] = form.cleaned_data['curso'].nome
        form.cleaned_data['data_nascimento'] = form.cleaned_data['data_nascimento'].strftime('%d%m%y')
        form.cleaned_data['cpf'] = form.cleaned_data['cpf'].replace('.', '').replace('-', '')
        form.cleaned_data['telefone'] = form.cleaned_data['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
        form.cleaned_data['cep'] = form.cleaned_data['cep'].replace('-', '')
        if form.cleaned_data['documentacao']:
            form.cleaned_data['documentacao'] = form.cleaned_data['documentacao'].name
        
        ### JSON ###
        # Verificação para o caso de já existirem alunos cadastrados no curso em questão
        try:
            with open(filename + '.json') as f:
                listObj = json.load(f)
        except:
            listObj = []
        listObj.append(form.cleaned_data)

        # Conversão dos dados para json
        cleaned_data_json = json.dumps(listObj, indent=4, ensure_ascii=False)
        # Escrita do json
        with open(filename + '.json', 'w') as f:
            f.write(cleaned_data_json)

        ### CSV ###
        # Criação de um dicionário com cabeçalho adequado
        pwd = PasswdGen()
        new_data = {
            'username': form.cleaned_data['cpf'],
            'password': pwd.run(),
            'firstname': form.cleaned_data['nome'],
            'lastname': form.cleaned_data['sobrenome'],
            'email': form.cleaned_data['email'],
            'city': form.cleaned_data['cidade'],
            'auth': 'manual',
            'course1': nome_breve,
        }

        # Verificação para o caso de já existirem alunos cadastrados no curso em questão
        try:
            with open(filename + '.csv', 'r') as f:
                if f.readline().split(',')[0] == 'username':
                    flag = True
                else:
                    flag = False
        except:
            flag = False
            
        # Escrita do arquivo .csv
        with open(filename + '.csv', 'a') as f:
            writer = csv.DictWriter(f, fieldnames=list(new_data.keys()))
            if not flag:
                writer.writeheader()
            writer.writerows([new_data])

        ### MYSQL ###
        # Escrita do arquivo MySQL
        with open(filename + '_mysql.sql', 'a') as f:
            f.write('INSERT INTO {{TABLE}}.{{SGDB}} ' + str(tuple(new_data.keys())) + ' ')
            f.write('VALUES ' + str(tuple(new_data.values())) + ';\n')

        ### SQL ###
        with open(filename + '_postgresql.sql', 'a') as f:
            f.write('INSERT INTO {{TABLE}}.{{SGDB}}' + str(tuple(new_data.keys())) + ' ')
            f.write('VALUES ' + str(tuple(new_data.values())) + ';\n')
        f.close()

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

        """.format(form.cleaned_data['curso'], new_data['username'], new_data['password'])

        recipients = [new_data['email']]

        new_email = SendEmail(subject=subject, message=message, recipients=recipients)
        new_email.send()

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.success(self.request, str(form.errors.as_data()))
        return super().form_invalid(form)
        
def thanks(request):
    return render(request, 'thanks.html')

class CadastroCursoCreateView(LoginRequiredMixin, CreateView):
    login_url = "/accounts/login"
    form_class = CursosForm
    template_name = "form_curso.html"
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, "Curso cadastrado com sucesso")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors.as_data())
        messages.success(self.request, form.errors.as_data())
        return super().form_invalid(form)