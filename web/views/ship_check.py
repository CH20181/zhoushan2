import datetime
import os

from dateutil.relativedelta import relativedelta
from django.http import FileResponse
from django.shortcuts import render
from django.urls import re_path

from django.db.models import Q
from django.utils.encoding import escape_uri_path

from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_datetime_text, StarkModelForm
from web import models

############## 指挥中心审核船情
from web.update.update_today_order import Create
from web.update.update_today_report import Create_report


class CheckPlanModelForm(StarkModelForm):
    class Meta:
        model = models.Plan
        exclude = ['boat_status', 'check_user']
        widgets = {
            'move_time': DateTimePickerInput,
        }


class ShipCheckHandler(StarkHandler):
    model_form_class = CheckPlanModelForm
    order_list = ['-id', 'boat_status']
    search_list = ['ship__chinese_name__contains', 'ship__MMSI__contains', 'ship__IMO__contains']
    per_page_count = 50

    def action_multi_confirm(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        user_id = request.session['user_info']['id']
        for pk in pk_list:
            # plan_obj = models.Plan.objects.filter(pk=pk, boat_status__lt=6).first()
            plan_obj = models.Plan.objects.filter(pk=pk, boat_status__in=[1, 2, 3, 4, 5, 9]).first()
            if not plan_obj:
                continue
            plan_obj.boat_status_id = 7
            plan_obj.check_user_id = user_id
            plan_obj.save()
            plan_obj.ship.boat_status_id = 7
            plan_obj.ship.save()

    action_multi_confirm.text = '批量通过'

    def action_multi_cancel(self, request, *args, **kwargs):
        pk_list = request.POST.getlist('pk')
        user_id = request.session['user_info']['id']
        for pk in pk_list:
            plan_obj = models.Plan.objects.filter(pk=pk, boat_status__lt=6).first()
            if not plan_obj:
                continue
            plan_obj.boat_status_id = 8
            plan_obj.check_user_id = user_id
            plan_obj.save()
            plan_obj.ship.boat_status_id = 8
            plan_obj.ship.save()

    action_multi_cancel.text = '批量驳回'
    action_list = [action_multi_confirm, action_multi_cancel]

    def save(self, form, request, is_update, *args, **kwargs):
        user_id = 1  # 审核通过的人
        plan_choice = form.instance.title_id
        if not is_update:
            form.instance.boat_status = plan_choice
            form.instance.check_user_id = user_id
            form.save()
        form.save()

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
        elif type_obj.title == '人证对照/抄关':
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

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '申请人'
        return '%s--%s:%s' % (obj.agent.company, obj.agent, obj.agent.phone)

    def display_imo(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return 'MMSI'
        return obj.ship.MMSI

    def display_report(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '1'
        return obj.report

    def display_apply_time(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '申报时间'
        return obj.apply.strftime("%m-%d %H:%M")

    has_add_btn = False

    def file_response_download1(self, request, file_path):
        try:
            response = FileResponse(open(file_path, 'rb'))
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
                escape_uri_path(os.path.basename(file_path)))
            return response
        except Exception:
            # return HttpResponse('兄弟，应该是船情没出来。要不等会再试试！！！')
            return render(request, 'error.html',
                          {'msg': '兄弟，应该是船情没出来。要不等会再试试！！！', 'url': 'stark:web_plan_play_list', 'pk': None})

    has_update_today_btn = True

    def get_update_today_btn(self, request, *args, **kwargs):
        """
        下载今日船情
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if self.has_update_today_btn:
            return "<a class='btn btn-warning' href='%s' target='_blank'>下载预报船情</a>" % self.reverse_commens_url(
                'update_today_order',
                *args, **kwargs)

        return None

    has_update_btn = True

    def get_update_btn(self, request, *args, **kwargs):
        """
        下载在港船舶动态
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if self.has_update_btn:
            return "<a class='btn btn-success' href='%s' target='_blank'>下载补报船情</a>" % self.reverse_commens_url(
                'update_today_report',
                *args, **kwargs)
        return None

    @property
    def get_time(self):
        e = datetime.datetime.now().year
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day + 1
        c = '%s年%s月%s日' % (e, a, b)
        return c

    @property
    def get_time_report(self):
        e = datetime.datetime.now().year
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day
        c = '%s年%s月%s日' % (e, a, b)
        return c

    def update_today(self, request, *args, **kwargs):
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        list_dir = os.listdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for i in list_dir:
            if i.endswith('.xls'):
                os.remove(path + '\\' + i)
        user_id = request.session['user_info']['id']  # 获取用户的id
        department = request.session['user_info']['department']  # 获取执勤部门
        two_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        Create(two_path, department, user_id, )
        first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\舟山站%s船情预报.xls' % (self.get_time)

        return self.file_response_download1(request, first_path)

    def update_today_report(self, request, *args, **kwargs):
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        list_dir = os.listdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        for i in list_dir:
            if i.endswith('.xls'):
                os.remove(path + '\\' + i)
        user_id = request.session['user_info']['id']  # 获取用户的id
        department = request.session['user_info']['department']  # 获取执勤部门
        two_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        Create_report(two_path, department, user_id, )
        first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\舟山站%s补报船情.xls' % (
            self.get_time_report)
        return self.file_response_download1(request, first_path)

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^updatejob/$', self.wrapper(self.update_today), name='update_today_order'),
            re_path(r'^updatereport/$', self.wrapper(self.update_today_report), name='update_today_report'),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_query_set(self, request, *args, **kwargs):
        return self.model_class.objects.filter(~Q(boat_status=6),
                                               Q(move_time__gt=datetime.date.today() + relativedelta(days=1)) | Q(
                                                   report=4, move_time__gt=datetime.date.today()))
        # return self.model_class.objects.filter(boat_status__in=[1,2,3,4,5])

    def get_list_display(self, request, *args, **kwargs):
        """
        获取页面上应该显示的列，预留的自定义扩展，例如：以后根据用户的不同显示不同的列
        :return:
        """
        value = []
        if self.list_display:
            value.extend(self.list_display)
        return value

    list_display = [StarkHandler.display_checkbox, 'ship', display_imo, 'title',
                    get_datetime_text('计划时间', 'move_time', time_format='%m-%d %H:%M'), display_location,
                    'boat_status', display_agent, display_report,display_apply_time,]
