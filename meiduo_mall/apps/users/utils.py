# 对openid进行序列化和反序列化
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
from apps.users.models import User
import logging

logger = logging.getLogger('django')


def generate_verify_email_url(user):
    # 创建序列化器
    s = Serializer(settings.SECRET_KEY, 24 * 3600)
    # 需要进行序列化的数据, 可以自主选择需要的字段
    data = {'user_id': user.id, 'email': user.email}
    # 对数据进行序列化, 并解码
    token = s.dumps(data).decode()
    # 拼接地址
    url = settings.EMAIL_VERIFY_URL + token
    return url


def check_verify_email_url(token):
    # 创建序列化器
    s = Serializer(settings.SECRET_KEY, 24 * 3600)
    # 对数据进行反序列化
    try:
        data = s.loads(token)
    except BadData:
        return None
    user_id = data.get('user_id')
    email = data.get('email')
    # 通过模型类.objects.get(筛选条件)得到目标用户对象
    try:
        user = User.objects.get(id=user_id, email=email)
    except User.DoesNotExist:
        return None
    return user
