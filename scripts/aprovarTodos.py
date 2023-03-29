from time import sleep
from InscricoesMoodleApp.models import DadosDoAluno
from InscricoesMoodleApp.views import AprovadoMail


def aprovarTodos():
    alunos = DadosDoAluno.objects.filter(status='W')

    contador = 0

    for aluno in alunos:
        contador += 1
        aluno.status = 'A'
        aluno.save(update_fields=['status'])
        AprovadoMail(aluno.curso.nome, aluno.cpf, aluno.senha_inicial, aluno.email)
        sleep(5)
        print('Aprovados: ' + '{:.2f}'.format(100*contador/len(alunos)) + '%')

aprovarTodos()