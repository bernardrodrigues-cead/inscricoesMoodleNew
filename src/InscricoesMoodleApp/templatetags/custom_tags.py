from django.template import Library
from django.template.defaultfilters import stringfilter
from InscricoesMoodleApp.models import Curso

register = Library()

@register.filter
@stringfilter
def flag_documentos(nome_curso):
    return Curso.objects.get(nome=nome_curso).anexar_documentacao

@register.filter
def format_cpf(cpf):
    return cpf[:3] + '.' + cpf[3:6] + '.' + cpf[6:9] + '-' + cpf[9:]

@register.filter
def format_telefone(telefone):
    if len(telefone) == 11:
        return '(' + telefone[:2] + ') ' + telefone[2:7] + '-' + telefone[7:]
    elif len(telefone) == 10:
        return '(' + telefone[:2] + ') ' + telefone[2:6] + '-' + telefone[6:]
    return telefone

@register.filter
def format_cep(cep):
    return cep[:2] + '.' + cep[2:5] + '-' + cep[5:]