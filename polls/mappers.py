from bpmappers.djangomodel import ModelMapper
from bpmappers import RawField
from polls.models import TbSubject, TbTeacher


class SubjectMapper(ModelMapper):
    isHot = RawField('is_hot')

    class Meta:
        model = TbSubject
        exclude = ('is_hot', )


class TeacherMapper(ModelMapper):

    class Meta:
        model = TbTeacher


