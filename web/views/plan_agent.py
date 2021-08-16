from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import re_path
from django.utils.safestring import mark_safe
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_choice_text, get_datetime_text, StarkModelForm
from web import models


class PlanAgentModelForm(StarkModelForm):
    """
    代理添加编辑船情计划的model
    """

    class Meta:
        model = models.Plan
        exclude = ['ship', 'boat_status', 'agent', 'check_user', 'complete', 'display', 'order','move_number','last_location']
        widgets = {
            'move_time': DateTimePickerInput,
        }
        labels = {'next_port': '泊位', 'location': '船厂/码头/锚地'}

    def __init__(self, *args, **kwargs):
        super(PlanAgentModelForm, self).__init__(*args, **kwargs)
        # 此处是只是添加移泊入港入境的计划
        self.fields['title'].queryset = models.PlanStatus.objects.filter(pk__in=[3, 4, 5, 6])

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location.id == 83:
            raise ValidationError('哎！跟你说了好几次了，这个位置就不要填无，锚地有选项的！！！！！')
        return location

    def clean_next_port(self):
        next_port = self.cleaned_data.get('next_port')
        if not next_port:
            raise ValidationError('请填写泊位。如果是锚地，此处填写锚地两个字就ok了！！')
        return next_port

class PlanAgentHandler(StarkHandler):
    """
    代理公司视图
    """
    model_form_class = PlanAgentModelForm

    # 记住这里到时添加一下用户的id，进行过滤，必须是本公司的船，才能添加
    def save(self, form, request, is_update, *args, **kwargs):

        ship_id = kwargs.get('ship_id')
        user_id = request.session['user_info']['id']
        obj = models.Ship.objects.filter(pk=ship_id).first()
        if not is_update:  # 判断是否为更新
            if obj:
                title_id = form.instance.title_id  # 获取船舶计划名称的id
                form.instance.ship_id = ship_id
                form.instance.agent_id = user_id  # 添加添加人的信息
                form.instance.ship.user_id = user_id
                # 申请人证对照
                if title_id == 6:
                    form.instance.boat_status_id = 9  # 船舶计划表添加船舶状态信息
                    form.instance.ship.boat_status_id = 9
                    form.instance.save()
                    form.instance.ship.save()
                else:
                    form.instance.boat_status_id = title_id
                    form.instance.ship.boat_status_id = title_id  # 在船舶表里添加船舶状态信息
                    if title_id == 3:
                        plan_obj_len = len(models.Plan.objects.filter(title_id=3, ship_id=ship_id))
                        if plan_obj_len == 1:
                            form.instance.move_number = 0
                        elif plan_obj_len == 2:
                            form.instance.move_number = 1
                        elif plan_obj_len == 3:
                            form.instance.move_number = 2
                    plan_obj = models.Plan.objects.filter(ship_id=ship_id, title__in=[3, 4, 5])
                    try:
                        form.instance.last_location_id = plan_obj.last().location_id
                    except:
                        form.instance.last_location_id = models.Ship.objects.filter(pk=ship_id).first().location_id
                    form.instance.ship.save()
                    form.instance.save()

            else:
                return HttpResponse('非法输入！！！')
        form.save()  # 如果为更新就直接保存

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/(?P<ship_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<ship_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^delete/(?P<pk>\d+)/(?P<ship_id>\d+)/$', self.wrapper(self.delete_view),
                    name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def display_location(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '停靠地点'
        location = obj.location
        if not location:
            return '%s' % obj.next_port
        return '%s--%s' % (obj.location, obj.next_port)

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "删除"
        ship_id = kwargs.get('ship_id')
        return mark_safe('<a href="%s">删除</a>' % self.reverse_delete_url(pk=obj.pk, ship_id=ship_id))

    # 去掉编辑按钮
    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
            value.append(type(self).display_del)
        return value

    list_display = ['ship', 'title', get_datetime_text('计划时间', 'move_time', time_format='%Y-%m-%d %H:%M'),
                    display_location,
                    'boat_status']

    def delete_view(self, request, pk, *args, **kwargs):
        """
        删除页面
        :param request:
        :param pk:
        :return:
        """
        origin_list_url = self.reverse_list_url(*args, **kwargs)
        if request.method == 'GET':
            return render(request, self.delete_template or 'stark/delete.html', {'cancel': origin_list_url})
        obj = models.Plan.objects.filter(pk=pk, boat_status=6)
        # 如果工单已经完成就不能删除
        if obj:
            obj.update(display=2)
            return redirect(origin_list_url)
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)

    # 后期加上代理公司进行过滤
    def get_query_set(self, request, *args, **kwargs):
        ship_id = kwargs.get('ship_id')
        if request.obj.company:
            return self.model_class.objects.filter(ship_id=ship_id)
        user_id = request.session['user_info']['id']
        return self.model_class.objects.filter(display=1, user_company=user_id.company, ship_id=ship_id)
