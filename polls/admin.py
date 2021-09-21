from django.contrib import admin

# Register your models here.

from polls.models import TbSubject, TbTeacher


class TbSubjectModelAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'intro', 'is_hot')
    search_fields = ('name', )
    ordering = ('no', )


class TbTeacherModelAdmin(admin.ModelAdmin):
    list_display = ('no', 'name', 'sex', 'birth', 'good_count', 'bad_count', 'subject')
    search_fields = ('name', )
    ordering = ('no', )


admin.site.register(TbSubject, TbSubjectModelAdmin)
admin.site.register(TbTeacher, TbTeacherModelAdmin)

