import hashlib
import json
import random
import requests
import re
import qiniu


def gen_md5_digest(content):
    return hashlib.md5(content.encode()).hexdigest()


ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def gen_random_code(length=4):
    return ''.join(random.choices(ALL_CHARS, k=length))


TEL_PATTERN = re.compile(r'1[3-9]\d{9}')


def check_tel(tel):
    """检查手机号"""
    return TEL_PATTERN.fullmatch(tel) is not None


def gen_mobile_code(length=6):
    """生成随机短信验证码"""
    return ''.join(random.choices('0123456789', k=length))


def send_mobile_code(tel, code):
    """发送短信验证码"""
    resp = requests.post("http://sms-api.luosimao.com/v1/send.json",
                         auth=("api", "key-c6741440b644fc92aa5fc4aaf0538cff"),
                         data={
                             "mobile": tel,
                             "message": f'尊敬的用户，您的验证码是：{code}，请在10分钟内输入【铁壳测试】'
                         }, timeout=3, verify=False)
    result = json.loads(resp.content)
    return result['error']


AUTH = qiniu.Auth('YCh107SGoM-caJ4QFUDaa3bKdvH2SSe3mOIR_Akw', 'TejBfrB6v56yvhdAzIFqBUqeCoFF9wZX5oz_ge5h')
BUCKET_NAME = 'djangotest001'


def upload_file_to_qiniu(key, file_path):
    """上传指定路径的文件到七牛云"""
    token = AUTH.upload_token(BUCKET_NAME, key)
    return qiniu.put_file(token, key, file_path)


def upload_stream_to_qiniu(key, stream, size):
    """上传二进制数据流到七牛云"""
    token = AUTH.upload_token(BUCKET_NAME, key)
    return qiniu.put_stream(token, key, stream, None, size)

