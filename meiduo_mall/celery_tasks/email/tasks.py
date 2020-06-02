# 定义发送验证激活邮件的异步任务
from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


@celery_app.task(name='send_email_verify_url')
def send_email_verify_url(to_email, verify_url):
    # 标题
    subject = "美多商城邮箱验证"
    # 发送内容:
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    send_mail(subject=subject,
              message='',
              from_email=settings.EMAIL_FROM,
              recipient_list=[to_email],
              html_message=html_message)
