# 对openid进行序列化和反序列化
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

#  s = Serializer('写一个秘钥', 过期时间)
def generate_access_token_openid(openid):
    # 创建序列化对象， 就像创建一把钥匙
    s = Serializer('secret_key', 600)
    # 构造需要序列化的数据
    data = {'openid': openid}
    # 对数据进行序列化
    token = s.dumps(data)
    # 返回密文字符串: 需要把数据类型为byte二进制字节型的token解码转化成字符串返回
    return token.decode()

def check_access_token_openid(access_token):
    s = Serializer('secret_key', 600)
    # access_token为密文字符串
    # 反序列化数据, 得到的类型为字典
    try:
        data = s.loads(access_token)
    except BadData:
        return None
    # 读取openid明文
    openid = data.get('openid')
    return openid
