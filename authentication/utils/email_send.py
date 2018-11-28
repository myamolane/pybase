from random import Random # 用于生成随机码
from django.core.mail import send_mail # 发送邮件模块
from authentication.models import EmailVerifyRecord # 邮箱验证model
from core.settings import EMAIL_FROM  # setting.py添加的的配置信息

# 生成随机字符串
def random_str(random_length=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str+=chars[random.randint(0, length)]
    return str


def send_register_email(email, code):
    email_title = "注册激活链接"
    email_body = "请点击下面的链接激活你的账号:http://127.0.0.1:8000/#/user/verify/{0}/email".format(code)
    # 发送邮件
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    if send_status:
        pass


def send_forget_email(email, code):
    email_title = "找回密码链接"
    email_body = "请点击下面的链接重新设置你的密码:http://127.0.0.1:8000/#/user/verify/{0}/reset_password".format(code)
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    if send_status:
        pass

send_types_handler = {
    'register': lambda email, code: send_register_email(email, code),
    'forget': lambda email, code: send_forget_email(email, code)
}


def send(email, send_type='register'):
    email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    send_types_handler[send_type](email, code)
