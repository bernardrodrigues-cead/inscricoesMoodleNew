from django import forms
from django.utils import timezone
from InscricoesMoodleApp.models import Curso, DadosDoAluno
from django.utils import timezone

class AlunosForm(forms.ModelForm):
    email_confirmacao = forms.EmailField(label="Confirmar e-mail")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.filter(
            ativo=True, 
            matricula_inicio__lte=timezone.now(), 
            matricula_fim__gte=timezone.now()
        ).order_by('nome')

    class Meta:
        model = DadosDoAluno
        fields = [
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
            'cidade_prefeitura',
            'secretaria',
            'cargo',
            'matricula',
        ]
        widgets = {
            'cpf': forms.TextInput(attrs={'placeholder': 'Somente números'}),
            'data_nascimento': forms.TextInput(attrs={'type': 'date'}),
            'nome': forms.TextInput(attrs={'placeholder': 'Primeiro nome ou nome social'}),
            'sobrenome': forms.TextInput(attrs={'placeholder': 'Demais sobrenomes'}),
            'email': forms.TextInput(attrs={'placeholder': 'Para confirmação de matrícula'}),
            'cidade': forms.TextInput(),
            'telefone': forms.TextInput(attrs={'placeholder': 'Somente números'}),
            'cep': forms.TextInput(attrs={'placeholder': 'Somente números'}),
            'logradouro': forms.TextInput(),
            'numero': forms.TextInput(),
            'complemento': forms.TextInput(attrs={'placeholder': 'ex.: apartamento 101'}),
            'bairro': forms.TextInput(),
            'uf': forms.Select(),
            'siga': forms.Select(choices=((False, "Não"), (True, "Sim"))),
            'documentacao': forms.FileInput(),
            'secretaria': forms.TextInput(),
            'cargo': forms.TextInput(),
            'matricula': forms.TextInput(),
        }

    def clean(self):
        cleaned_data = super(AlunosForm, self).clean()
        if {'cpf': cleaned_data['cpf'].replace('.', '').replace('-', ''), 'curso': cleaned_data['curso'].id} in DadosDoAluno.objects.all().values('cpf', 'curso'):
            self.add_error('cpf', 'CPF já cadastrado no curso solicitado')
        

class CursosForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = [
            'nome',
            'nome_breve',
            'categoria',
            'limite_vagas',
            'vagas',
            'data_inicio',
            'data_fim',
            'matricula_inicio',
            'matricula_fim',
            'anexar_documentacao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do curso'}),
            'nome_breve': forms.TextInput(attrs={'placeholder': 'Ex.: DIS123-' + str(timezone.now().year) + '.1-A'}),
            'categoria': forms.Select(),
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
            'matricula_inicio': forms.DateInput(attrs={'type': 'date'}),
            'matricula_fim': forms.DateInput(attrs={'type': 'date'}),
            'anexar_documentacao': forms.Select(choices=((False, "Não"), (True, "Sim"))),
            'limite_vagas': forms.Select(choices=((False, "Não"), (True, "Sim")))
        }