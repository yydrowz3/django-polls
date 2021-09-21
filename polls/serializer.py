from rest_framework import serializers

from polls.models import TbSubject, TbTeacher


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = TbSubject
        fields = '__all__'


class SubjectSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = TbSubject
        fields = ('no', 'name')


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = TbTeacher
        exclude = ('subject', )

