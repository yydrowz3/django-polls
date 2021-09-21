import jwt
from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect

from polls.forms import LoginForm
from polls.models import TbSubject, TbTeacher, TbUser
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404

from polls.utils import gen_random_code, gen_md5_digest, check_tel, gen_mobile_code, send_mobile_code, \
    upload_stream_to_qiniu
from polls.captcha import Captcha
import xlwt
from io import BytesIO
from urllib.parse import quote
from reportlab.pdfgen import canvas
from polls.mappers import SubjectMapper
from rest_framework.decorators import api_view
from rest_framework.response import Response
from polls.serializer import SubjectSerializer, SubjectSimpleSerializer, TeacherSerializer
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt
import os
import uuid
import jwt
from django.conf import settings
from django.core.cache import caches
from jwt import InvalidTokenError
from django.utils import timezone
import datetime
from django.db import DatabaseError


def show_index(requests: HttpRequest) -> HttpResponse:
    return redirect('/static/html/subjects.html')

# 使用模板生成页面
# def show_subjects(request):
#     subjects = TbSubject.objects.all().order_by('no')
#     return render(request, 'subjects.html', {'subjects': subjects})


# # 发送JSON数据
# def show_subjects(request):
#     queryset = TbSubject.objects.all()
#     subjects = []
#     for subject in queryset:
#         subjects.append(SubjectMapper(subject).as_dict())
#     return JsonResponse(subjects, safe=False)


# @api_view(('GET', ))
# def show_subjects(request: HttpRequest) -> HttpResponse:
#     subjects = TbSubject.objects.all().order_by('no')
#     # 创建序列化器对象并指定要序列化的模型
#     serializer = SubjectSerializer(subjects, many=True)
#     # 通过序列化器的data属性获得模型对应的字典并通过创建Response对象返回JSON格式的数据
#     return Response(serializer.data)


# 引入外部Serializer类 继承ListAPIView 只显示一种视图
# class SubjectView(ListAPIView):
#     # 通过queryset指定如何获取学科数据
#     queryset = TbSubject.objects.all()
#     # 通过serializer_class指定如何序列化学科数据
#     serializer_class = SubjectSerializer


# 自定义分页器，在类中调用
# class CustomizedPagination(PageNumberPagination):
#     # 默认页面大小
#     page_size = 5
#     # 页面大小对应的查询参数
#     page_size_query_param = 'size'
#     # 页面大小的最大值
#     max_page_size = 50


# 继承ModelSet有多种视图，需要在urls中指明
class SubjectViewSet(ModelViewSet):
    queryset = TbSubject.objects.all()
    serializer_class = SubjectSerializer
    # pagination_class = CustomizedPagination
    # 不使用分页器
    # pagination_class = None


@api_view(('GET', ))
# @cache_page(timeout=86400, cache='default')
def show_subjects(request):
    """获取学科数据"""
    queryset = TbSubject.objects.all()
    data = SubjectSerializer(queryset, many=True).data
    return Response({'code': 20000, 'subjects': data})


# @method_decorator(decorator=cache_page(timeout=86400, cache='default'), name='get')
# class SubjectView(ListAPIView):
#     """获取学科数据的视图类"""
#     queryset = TbSubject.objects.all()
#     serializer_class = SubjectSerializer


# 手写缓存式编程
# def show_subjects(request):
#     """获取学科数据"""
#     redis_cli = get_redis_connection()
#     # 先尝试从缓存中获取学科数据
#     data = redis_cli.get('vote:polls:subjects')
#     if data:
#         # 如果获取到学科数据就进行反序列化操作
#         data = json.loads(data)
#     else:
#         # 如果缓存中没有获取到学科数据就查询数据库
#         queryset = Subject.objects.all()
#         data = SubjectSerializer(queryset, many=True).data
#         # 将查到的学科数据序列化后放到缓存中
#         redis_cli.set('vote:polls:subjects', json.dumps(data), ex=86400)
#     return Response({'code': 20000, 'subjects': data})


# def show_teachers(request):
#     try:
#         sno = int(request.GET.get('sno'))
#         # teachers = []
#         if sno:
#             subject = TbSubject.objects.only('name').get(no=sno)
#             teachers = TbTeacher.objects.filter(subject=subject).order_by('no')
#             return render(request, 'teachers.html', {
#                 'subject': subject,
#                 'teachers': teachers,
#             })
#     except(ValueError, TbSubject.DoesNotExist):
#         return redirect('/')


@api_view(('GET', ))
def show_teachers(request: HttpRequest) -> HttpResponse:
    try:
        sno = int(request.GET.get('sno'))
        subject = TbSubject.objects.only('name').get(no=sno)
        teachers = TbTeacher.objects.filter(subject=subject).defer('subject').order_by('no')
        subject_seri = SubjectSimpleSerializer(subject)
        teacher_seri = TeacherSerializer(teachers, many=True)
        return Response({'subject': subject_seri.data, 'teachers': teacher_seri.data})
    except (TypeError, ValueError, TbSubject.DoesNotExist):
        return Response(status=404)

# class TeacherView(ListAPIView):
#     serializer_class = TeacherSerializer
#
#     def get_queryset(self):
#         queryset = TbTeacher.objects.defer('subject')
#         try:
#             sno = self.request.GET.get('sno', '')
#             queryset = queryset.filter(subject__no=sno)
#             return queryset
#         except ValueError:
#             raise Http404('No teachers found.')


# 之前用session的
# def prise_or_criticize(request: HttpRequest) -> HttpResponse:
#     """"好评"""
#     if request.session.get('userid'):
#         try:
#             tno = int(request.GET.get('tno'))
#             teacher = TbTeacher.objects.get(no=tno)
#             if request.path.startswith('/praise'):
#                 teacher.good_count += 1
#                 count = teacher.good_count
#             else:
#                 teacher.bad_count += 1
#                 count = teacher.bad_count
#             teacher.save()
#             data = {'code': 20000, 'mesg': '操作成功', 'count': count}
#         except(ValueError, TbTeacher.DoesNotExist):
#             data = {'code': 20001, 'mesg': '操作失败'}
#     else:
#         data = {'code': 20002, 'mesg': '请先登录', }
#     return JsonResponse(data)

# 无中间件
def praise_or_criticize(request: HttpRequest) -> HttpResponse:
    token = request.META.get('HTTP_TOKEN', None)
    if token and token != 'undefined':
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            tno = int(request.GET.get('tno'))
            teacher = TbTeacher.objects.get(no=tno)
            if request.path.startswith('/praise/'):
                teacher.good_count += 1
                count = teacher.good_count
            else:
                teacher.bad_count += 1
                count = teacher.bad_count
            teacher.save()
            data = {
                'code': 20000,
                'mesg': '投票成功',
                'count': count,
            }
        except (ValueError, TbTeacher.DoesNotExist):
            data = {
                'code': 20001,
                'mesg': '投票失败',
            }
        except InvalidTokenError:
            data = {
                'code': 20002,
                'mesg': '登录已过期',
            }
    else:
        data = {
            'code': 20002,
            'mesg': '请先登录',
        }
    return JsonResponse(data)


# def login(request: HttpRequest) -> HttpResponse:
#     hint = ''
#     return render(request, 'login.html', {'hint': hint})


def get_captcha(request: HttpRequest) -> HttpResponse:
    """验证码"""
    captcha_text = gen_random_code()
    request.session['captcha'] = captcha_text
    image_data = Captcha.instance().generate(captcha_text)
    return HttpResponse(image_data, content_type='image/png')


# 无中间件
@api_view(('POST', ))
def login(request: HttpRequest) -> HttpResponse:
    username = request.data.get('username')
    password = request.data.get('password')
    if username and password:
        password = gen_md5_digest(password)
        user = TbUser.objects.filter(username=username, password=password).first()
        if user:
            payload = {
                'exp': timezone.now() + datetime.timedelta(days=1),
                'userid': user.no
            }
            token = jwt.encode(payload, settings.SECRET_KEY)
            return Response({'code': 10000, 'token': token, 'username': username})
        else:
            hint = '用户名或密码错误'
    else:
        hint = '请输入有效的用户名和密码'
    return Response({'code':10001, 'mesg': hint})


@api_view(('POST', ))
def register(request: HttpRequest) -> HttpResponse:
    agreement = request.data.get('agreement')
    if agreement:
        tel = request.data.get('tel')
        mobilecode = request.data.get('mobilecode', '0')
        mobilecode2 = caches['default'].get(f'tel:valid:{tel}', '1')
        if mobilecode == mobilecode2:
            username = request.data.get('username')
            password = request.data.get('password')
            if username and password and tel:
                try:
                    password = gen_md5_digest(password)
                    user = TbUser(username=username, password=password, tel=tel)
                    user.save()
                    return Response({'code': 30000, 'mesg': '注册成功'})
                except DatabaseError:
                    hint = '注册失败，请尝试更换用户名'
            else:
                hint = '请输入有效的注册信息'
        else:
            hint = '请输入有效的手机验证码'
    else:
        hint = '请勾选同意网站用户协议以及隐私政策'
    return Response({'code': 30001, 'mesg': hint})


def logout(request):
    """注销"""
    request.session.flush()
    return redirect('/')


def export_teachers_excel(request):
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('老师信息表')
    # 查询所有老师的信息
    queryset = TbTeacher.objects.all().select_related('subject')
    # 向Excel表单中写入表头
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('name', 'detail', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, TbSubject):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 中文文件名需要处理成百分号编码
    filename = quote('老师.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
    return resp


def export_pdf(request: HttpRequest) -> HttpResponse:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Helvetica", 80)
    pdf.setFillColorRGB(0.2, 0.5, 0.3)
    pdf.drawString(100, 550, 'hello, world!')
    pdf.showPage()
    pdf.save()
    resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    resp['content-disposition'] = 'inline; filename="demo.pdf"'
    return resp


def get_teachers_data(request):
    queryset = TbTeacher.objects.all().only('name', 'good_count', 'bad_count')
    names = [teacher.name for teacher in queryset]
    good_counts = [teacher.good_count for teacher in queryset]
    bad_counts = [teacher.bad_count for teacher in queryset]
    return JsonResponse({'names': names, 'good': good_counts, 'bad': bad_counts})


# 修改前的版本
# @api_view(('GET', ))
# def get_mobile_code(request, tel):
#     """获取短信验证码"""
#     if check_tel(tel):
#         redis_cli = get_redis_connection()
#         if redis_cli.exists(f'vote:block-mobile:{tel}'):
#             data = {'code': 30001, 'message': '请不要在60秒内重复发送短信验证码'}
#         else:
#             code = random_code()
#             send_mobile_code(tel, code)
#             # 通过Redis阻止60秒内容重复发送短信验证码
#             redis_cli.set(f'vote:block-mobile:{tel}', 'x', ex=60)
#             # 将验证码在Redis中保留10分钟（有效期10分钟）
#             redis_cli.set(f'vote2:valid-mobile:{tel}', code, ex=600)
#             data = {'code': 30000, 'message': '短信验证码已发送，请注意查收'}
#     else:
#         data = {'code': 30002, 'message': '请输入有效的手机号'}
#     return Response(data)


@api_view(('GET', ))
def get_mobile_code(request: HttpRequest, tel) -> HttpResponse:
    """"获取短信验证码"""
    if check_tel(tel):
        if caches['default'].get(f'tel:block:{tel}'):
            data = {'code': 40003, 'message': '请不要在120秒内重复发送短信验证码'}
        else:
            code = gen_mobile_code()
            result = send_mobile_code(tel, code)
            if result == 0:
                caches['default'].set(f'tel:valid:{tel}', code, timeout=1800)
                caches['default'].set(f'tel:block:{tel}', code, timeout=120)
                data = {'code': 40000, 'message': '短信验证码已发送到您的手机'}
            else:
                data = {'code': 40001, 'message': '短信验证码发送失败，请稍后重试'}
    else:
        data = {'code': 40002, 'message': '请输入有效的手机号码'}
    return JsonResponse(data)


@csrf_exempt
def upload(request):
    # 如果上传的文件小于2.5M，则photo对象的类型为InMemoryUploadedFile，文件在内存中
    # 如果上传的文件超过2.5M，则photo对象的类型为TemporaryUploadedFile，文件在临时路径下
    photo = request.FILES.get('photo')
    _, ext = os.path.splitext(photo.name)
    # 通过UUID和原来文件的扩展名生成独一无二的新的文件名
    filename = f'{uuid.uuid1().hex}{ext}'
    # 对于内存中的文件，可以使用上面封装好的函数upload_stream_to_qiniu上传文件到七牛云
    # 如果文件保存在临时路径下，可以使用upload_file_to_qiniu实现文件上传
    upload_stream_to_qiniu(filename, photo.file, photo.size)
    return redirect('/static/html/upload.html')



