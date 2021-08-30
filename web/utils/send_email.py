from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse


def send_email():
    message1 = ('计划完成', '内容1', '458426162@qq.com', ['458426162@163.com'])
    message2 = ('邮件标题2', '内容2', '458426162@qq.com', ['458426162@163.com'])
    send_mass_mail((message1, message2), fail_silently=False)
    return HttpResponse('OK')