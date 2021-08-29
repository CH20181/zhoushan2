from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import re_path, reverse
from django.utils.safestring import mark_safe
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_choice_text, get_datetime_text, StarkModelForm
from web import models
import datetime
from dateutil.relativedelta import relativedelta


class PlanAgentModelForm(StarkModelForm):
    """
    代理添加编辑船情计划的model
    """

    class Meta:
        model = models.Plan
        exclude = ['ship', 'boat_status', 'agent', 'check_user', 'complete', 'display', 'order', 'move_number',
                   'last_location', 'last_port']
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
        str_list = ['秀山东', '虾峙门', ]
        for i in str_list:
            if i in next_port:
                raise ValidationError('锚地填写锚地两个字')
        if next_port and len(next_port) < 10:
            return next_port
        raise ValidationError('请输入在港泊位，锚地填写无')
        # if not next_port:
        #     raise ValidationError('请填写泊位。如果是锚地，此处填写锚地两个字就ok了！！')
        # if '锚地' in next_port:
        #     return ''
        # return next_port

    def clean_move_time(self):
        move_time = self.cleaned_data.get('move_time')
        tomorrow = datetime.date.today() + relativedelta(days=2)
        if tomorrow > move_time.date():
            return move_time
        raise ValidationError('只能申报今天或者明天的船情！！！！')


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
                # 这里阻止一下重复添加船情
                location_id = form.instance.location_id
                is_have = models.Plan.objects.filter(ship_id=ship_id, title_id=title_id,
                                                     location_id=location_id, boat_status__in=[1, 2, 4, 5]).first()
                if is_have:
                    # return HttpResponse('请勿重复添加相同的计划，请将取消的计划删除后重试')
                    return render(request, 'error.html',
                                  {'msg': '请勿重复添加相同的计划，请将原计划取消后重试', 'url': 'stark:web_plan_agent_list', 'pk': ship_id})
                # 判断是否为补报船舶
                move_time = form.instance.move_time
                try:
                    if move_time.date() == datetime.date.today():
                        form.instance.report = 1
                except:
                    pass
                # 申请人证对照
                if title_id == 6:
                    form.instance.boat_status_id = 9  # 船舶计划表添加船舶状态信息
                    form.instance.ship.boat_status_id = 9
                    form.instance.ship.save()
                    form.instance.save()
                else:
                    form.instance.boat_status_id = title_id
                    form.instance.ship.boat_status_id = title_id  # 在船舶表里添加船舶状态信息
                    if title_id == 3:
                        # 过滤没有入港直接移泊的情况
                        obj_is_into = models.Ship.objects.filter(pk=ship_id).first().location_id
                        if obj_is_into == 83:
                            # 有入港入境计划的，可以添加移泊
                            is_have_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5]).first()
                            if not is_have_into:
                                # return HttpResponse('该船还未入港，不能移泊！！')
                                return render(request, 'error.html', {'url': 'stark:web_plan_agent_list', 'pk': ship_id,
                                                                      'msg': '该船还未入港，不能移泊！！'})

                        plan_obj_len = len(models.Plan.objects.filter(title_id=3, ship_id=ship_id))
                        if plan_obj_len == 1:
                            form.instance.move_number = 0
                        elif plan_obj_len == 2:
                            form.instance.move_number = 1
                        elif plan_obj_len == 3:
                            form.instance.move_number = 2
                    # 移泊、入港、入境
                    plan_obj = models.Plan.objects.filter(ship_id=ship_id, title__in=[3, 4, 5])
                    try:
                        form.instance.last_location_id = plan_obj.last().location_id
                        form.instance.last_port = plan_obj.last().next_port
                    except:
                        # 修复移泊出现没有具体泊位
                        try:
                            form.instance.last_location_id = models.Ship.objects.filter(pk=ship_id).first().location_id
                            form.instance.last_port = models.Ship.objects.filter(pk=ship_id).first().port_in
                        except:
                            form.instance.last_location_id = models.Ship.objects.filter(pk=ship_id).first().location_id
                            form.instance.last_port = ''
                    if title_id == 4 or title_id == 5:
                        alive = models.Ship.objects.filter(pk=ship_id).first().location_id
                        if alive != 83:
                            # return HttpResponse('该船已经入港！！请勿重复添加入港、入境计划')
                            return render(request, 'error.html', {'url': 'stark:web_plan_agent_list', 'pk': ship_id,
                                                                  'msg': '该船已经入港！！请勿重复添加入港、入境计划!'})
                    form.instance.ship.save()
                    form.instance.save()

            else:
                # return HttpResponse('非法输入！！！')
                return render(request, 'error.html',
                              {'url': 'stark:web_plan_agent_list', 'pk': ship_id, 'msg': '非法输入！！！'})
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

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            return "<a class='btn btn-success' href='%s'>添加入港、入境、移泊、人证对照</a>" % self.reverse_commens_url(
                self.get_add_url_name,
                *args, **kwargs)
        return None

    has_move_btn = True

    def get_move_btn(self, request, *args, **kwargs):
        # print(request,**kwargs)
        ship_id = kwargs.get('ship_id')
        if self.has_move_btn:
            return "<a class='btn btn-primary btn-warning' href='%s'>添加出港、出境计划</a>" % reverse(
                'stark:web_ship_agent_get_move', kwargs={'ship_id': ship_id})
        return None

    # def display_location(self, obj=None, is_header=None, *args, **kwargs):
    #     if is_header:
    #         return '停靠地点'
    #     location = obj.location
    #     if not location:
    #         return '%s' % obj.next_port
    #     return '%s--%s' % (obj.location, obj.next_port)
    def display_location(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '申请停靠地点'
        location = obj.location
        if not location:  # 如果没有值得话，说明是出港、出境情况
            try:
                return '%s----->%s' % (obj.last_location.title + obj.last_port, obj.next_port)
            except:
                return obj.next_port
        type_obj = obj.title
        if type_obj.title == '入境' or type_obj.title == '入港':
            try:
                return '%s--->%s' % (obj.ship.last_port, obj.location.title + obj.next_port)
            except:
                return '%s--->%s' % (obj.ship.last_port, obj.location.title)
        elif type_obj.title == '人证对照':
            try:
                return '%s%s' % (obj.location.title, obj.next_port)
            except:
                return obj.location.title
        elif type_obj.title == '移泊':
            plan_obj = models.Plan.objects.filter(ship_id=obj.ship_id, title_id=3)
            plan_obj_number = obj.move_number
            # print(plan_obj_number,)
            try:
                if plan_obj_number != None:
                    return '%s--->%s' % (plan_obj[plan_obj_number].location.title + plan_obj[plan_obj_number].next_port,
                                         obj.location.title + obj.next_port)
                return '%s--->%s' % (obj.last_location.title + obj.last_port, obj.location.title + obj.next_port)
            except:
                ship_id = obj.ship_id
                is_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5],
                                                     boat_status_id__in=[1, 2, 3, 4, 5, 7, 8, 9]).first()
                if is_into:
                    try:
                        return '%s----->%s' % (
                            is_into.location.title + is_into.next_port, obj.location.title + obj.next_port)
                    except:
                        return '%s----->%s' % (
                            is_into.location.title, obj.location.title)
                try:
                    return '%s--->%s' % (
                        obj.ship.location.title + obj.ship.next_port, obj.location.title + obj.next_port)
                except:
                    return '%s--->%s' % (obj.ship.location.title, obj.next_port)
                return '%s--->%s' % (obj.last_location.title, obj.location.title)
                # return '%s--->%s' % (obj.ship.location.title + obj.ship.port_in, obj.location.title)
        # 出港、出境
        else:
            ship_id = obj.ship_id
            # 此处判断是否为当天入出船舶
            is_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5]).first()
            if is_into:
                # 如果是当天入境的还要判断是否有移泊的情况
                is_remove = models.Plan.objects.filter(ship_id=ship_id, title_id=3,
                                                       boat_status_id__in=[1, 2, 3, 4, 5, 7, 8, 9],
                                                       move_time__year=datetime.datetime.now().year,
                                                       move_time__month=datetime.datetime.now().month,
                                                       move_time__day=datetime.datetime.now().day)
                if is_remove:
                    try:
                        return '%s----->%s' % (
                            is_remove.last().location.title + is_remove.last().last_port, obj.next_port)
                    except:
                        return obj.next_port
                return '%s----->%s' % (is_into.location.title + is_into.next_port, obj.next_port)
            # print(type_obj.title,obj.location.title,obj.next_port)
            try:

                return '%s--->%s' % (obj.last_location.title + obj.last_port, obj.next_port)
            except:
                try:
                    return obj.ship.location.title
                except:
                    return '未填写位置'

        # if type_obj.title == '入境' or type_obj.title == '入港':
        #     try:
        #         return '%s--->%s' % (obj.ship.last_port, str(obj.location.title + obj.next_port))
        #     except:
        #         return '%s--->%s' % (obj.ship.last_port, obj.location.title)
        # return '%s--->%s' % (obj.ship.location, obj.location)

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "取消计划"
        ship_id = kwargs.get('ship_id')
        return mark_safe(
            "<a href='%s' class='btn btn-danger btn-xs'>取消</a>" % self.reverse_delete_url(pk=obj.pk, ship_id=ship_id))

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
        try:
            ship_obj = models.Ship.objects.filter(plan=models.Plan.objects.filter(pk=pk).first()).first()
            ship_obj.boat_status_id = None
            ship_obj.save()
        except:
            pass
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)

    # 后期加上代理公司进行过滤
    def get_query_set(self, request, *args, **kwargs):
        ship_id = kwargs.get('ship_id')
        if request.obj.company:
            return self.model_class.objects.filter(ship_id=ship_id)
        user_id = request.session['user_info']['id']
        return self.model_class.objects.filter(display=1, user_company=user_id.company, ship_id=ship_id)
