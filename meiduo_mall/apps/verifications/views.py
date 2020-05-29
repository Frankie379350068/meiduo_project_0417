from django.shortcuts import render
from django.views import View
from apps.verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
import random, logging
from apps.verifications.libs.yuntongxun.ccp_sms import CCP

# Create your views here.
# 创建日志输出器
logger = logging.getLogger('django')


# GET请求 /sms_codes/(?P<mobile>1[3-9]\d{9})/
class SMSCodeView(View):
    def get(self, request, mobile):
        """
        :param mobile:手机号
        :return:Json
        """
        # 从逻辑一开始的地方就判断用户是否频繁发送短信，对手机号进行校验
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': 400, 'errmsg': '频繁发送短信验证码'})
        # 接收参数： mobile参数（正则已做配对，不需要再次校验），
        # image_code图形验证码参数，image_code_id图形验证码uuid
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 实现核心的业务逻辑
        # 提取图形验证码: 以前怎么存，现在怎么取

        image_code_server = redis_conn.get('img_%s' % uuid)
        # 判断图形验证码是否过期
        if not image_code_server:
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码过期'})

        # 删除redis中的图形验证码：为了避免恶意用户利用图形验证码恶意发送短信， 需要将redis数据库中的图形验证码删除，保证图形验证码只能使用1次
        redis_conn.delete('img_%s' % uuid)
        # 比对图形验证码
        # 先将image_code_server由bytes类型数据转换成str类型数据, decode()是python内置的方法
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': 400, 'errmsg': '图形验证码输入有误'})

        # 生成随机短信验证码: 1.随机数字 2.不足六位的需补齐 ‘0’， %__d
        random_num = random.randint(0, 999999)
        sms_code = '%06d' % random_num
        # 验证码输出到日志
        logger.info(sms_code)
        # 保存短信验证码
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('sms_%s' % mobile, 300, sms_code)
        # # 发送短信之前，给该用户设置标记，记录他的手机号，给予手机号一个冷却时间，避免页面刷新即可立即发短信
        # redis_conn.setex('send_flag_%s' %mobile, 60, 1)

        # 使用pipline管道来操作redis数据库的数据写入，提升redis性能
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, 300, sms_code)
        pl.setex('send_flag_%s' %mobile, 60, 1)
        pl.execute()

        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # 响应结果
        return http.JsonResponse({'code': 0, 'errmsg': '短信验证码发送成功'})


class ImageCodeView(View):
    def get(self, request, uuid):
        # 生成图形验证码
        text, image = captcha.generate_captcha()

        # 保存图形验证码到redis数据库
        # 则需要创建连接redis的连接对象
        redis_conn = get_redis_connection('verify_code')
        # 图形验证码需要设置有效期set(key, time, value), 加个前缀img_更好
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 响应结果
        return http.HttpResponse(image, content_type='image.jpg')
