import random, string
from django.conf import settings
from django.core.mail import send_mail


# send mail to the specified mothafucka.
class SendEmail(object):
    def __init__(self, subject=None,  message=None, emailfrom=settings.EMAIL_HOST_USER, recipients=None):
        self.subject = subject
        self.message = message
        self.emailfrom = emailfrom
        self.recipients = recipients

    def send(self):
        return send_mail(self.subject, self.message, self.emailfrom, self.recipients)



class PasswdGen(object):
    """
    """

    def __init__(self, size=8):
        """
        """
        self.size = size
        self.password = []
        self.special = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    def run(self):
        """
        """
        self.password.append(random.choice(string.ascii_lowercase))
        self.password.append(random.choice(string.digits))
        self.password.append(random.choice(string.ascii_uppercase))
        self.password.append(random.choice("!@#$%^&*()"))
        for i in range(self.size - 4):
            self.password.append(random.choice(self.special))

        random.shuffle(self.password)
        return "".join(self.password)