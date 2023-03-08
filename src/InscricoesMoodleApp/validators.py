import re
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validateCPF(cpf):

    """ Efetua a validação do CPF, tanto formatação quando dígito verificadores.

    Parâmetros:
        cpf (str): CPF a ser validado

    Retorno:
        bool:
            - Falso, quando o CPF não possuir o formato 999.999.999-99;
            - Falso, quando o CPF não possuir 11 caracteres numéricos;
            - Falso, quando os dígitos verificadores forem inválidos;
            - Verdadeiro, caso contrário.

    Exemplos:

    --- validate('529.982.247-25')
    True
    --- validate('52998224725')
    False
    --- validate('111.111.111-11')
    False
    """

    # Verifica a formatação do CPF
    if not re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', cpf):
        raise ValidationError(_('CPF com formato inválido'), params={'cpf': cpf})

    # Obtém apenas os números do CPF, ignorando pontuações
    numbers = [int(digit) for digit in cpf if digit.isdigit()]

    # Verifica se o CPF possui 11 números ou se todos são iguais:
    if len(numbers) != 11 or len(set(numbers)) == 1:
        raise ValidationError(_('CPF inválido.'), params={'cpf': cpf})

    # Validação do primeiro dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[9] != expected_digit:
        raise ValidationError(_('CPF inválido.'), params={'cpf': cpf})

    # Validação do segundo dígito verificador:
    sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
    expected_digit = (sum_of_products * 10 % 11) % 10
    if numbers[10] != expected_digit:
        raise ValidationError(_('CPF inválido.'), params={'cpf': cpf})

def validatePDF(file):
    if file.name[-4:] != ".pdf":
        raise ValidationError(_('O documento enviado deve estar no formato PDF'), params={'file': file})

def validateBirthdate(date):
    if timezone.make_aware(timezone.datetime(date.year, date.month, date.day)) > timezone.now() - timezone.timedelta(days=365*18+4):
        raise ValidationError(_('Este curso é, incialmente, indicado para maiores de 18 anos. Entre em contato com a coordenação do curso para maiores informações.'), params={'date': date})