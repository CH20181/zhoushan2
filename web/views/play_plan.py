import datetime
import os

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.urls import re_path
from django.utils.encoding import escape_uri_path
from web.update.update_today import Create
from stark.service.v1 import StarkHandler, StarkModelForm, get_datetime_text
from web import models
from stark.forms.widgets import DateTimePickerInput


# 这个是执勤队做船情

class PlanPlayModelForm(StarkModelForm):
    class Meta:
        model = models.Plan
        fields = ['move_time', 'next_port', ]
        widgets = {
            'move_time': DateTimePickerInput,
        }


class PlanPlayHandler(StarkHandler):
    model_form_class = PlanPlayModelForm
    has_add_btn = False

    def display_IMO(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return 'IMO'
        return obj.ship.IMO

    def display_MMSI(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return 'MMSI'
        return obj.ship.MMSI

    def display_nationality(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '国籍'
        return obj.ship.nationality

    def display_goods(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '货物'
        return obj.ship.goods

    def display_location(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '计划'
        return obj.title

    def display_purpose(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '来港目的'
        return obj.ship.purpose

    def display_last_port(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '上一港'
        return obj.ship.last_port

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '代理'
        return '%s:%s' % (obj.ship.user.company, obj.agent.phone)

    def display_note(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '备注'
        try:
            note = obj.note[:30]
        except:
            note = obj.note
        return note

    def display_plan(self, obj=None, is_header=None, *args, **kwargs):

        if is_header:
            return '计划'
        title_into_list = [3, 4, 5]
        title_id = obj.title_id
        # print(title_id, obj.ship.location)
        # if title_id in title_into_list:
        #     return '%s----->%s' % (obj.ship.location, str(obj.location) + obj.next_port)
        # 移泊
        if title_id == 3:
            plan_obj = models.Plan.objects.filter(ship_id=obj.ship_id, title_id=3)
            plan_obj_number = obj.move_number
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
        # 入港、入境
        elif title_id == 4 or title_id == 5:
            try:
                return '%s----->%s' % (obj.ship.last_port, obj.location.title + obj.next_port)
            except:
                return '%s----->%s' % (obj.ship.last_port, obj.location.title)
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
                            is_remove.last().location.title + is_remove.last().next_port, obj.next_port)
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

    list_display = [StarkHandler.display_checkbox, 'ship', display_IMO, display_MMSI, display_nationality,
                    display_goods, display_purpose, display_last_port, get_datetime_text('时间', 'move_time'),
                    display_location, display_plan,display_agent]

    def action_multi_complete(self, request, *args, **kwargs):
        user_obj = request.obj
        pk_list = request.POST.getlist('pk')
        pk_list.reverse()
        # department = request.session['user_info']['department']
        # 移泊、入境、入港
        status_list = [3, 4, 5]
        # 出境、出港
        status_list_two = [1, 2]
        for pk in pk_list:
            # 这里后期添加上部门进行过滤
            a = Q(location__department=user_obj.department)
            b = Q(last_location__department=user_obj.department)
            plan_obj = models.Plan.objects.filter(pk=pk, boat_status_id=7).filter(a | b).first()
            # 这里有个问题，过滤的条件不对，应该将当前船舶的历史申报船情进行过滤
            # 将本次船的只有有没有完成的入港、入境计划，就不能完成。
            ship_id = models.Plan.objects.filter(pk=pk).first().ship
            # print(ship_id)
            # into_obj = models.Plan.objects.filter(title_id__in=[1, 2, 4, 5], boat_status_id=7).first()
            into_obj = models.Plan.objects.filter(title_id__in=[4, 5], boat_status_id=7,
                                                  ship_id=ship_id.pk).first()
            if into_obj and plan_obj != into_obj:  # 如果有入港入境船情，必须先完成入港入境船情，否则无法完成
                continue
            if plan_obj:
                location = plan_obj.location
                # 这个是判断今天是否有出港、出境计划
                is_complete = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[1, 2]).first()
                if is_complete:
                    # is_over是出港、出境的船舶对象
                    is_over = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[1, 2], boat_status=7).first()
                    if plan_obj == is_over:
                        plan_obj.ship.location = plan_obj.last_location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                    elif location and is_over:
                        plan_obj.ship.location = location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                    else:
                        pass
                else:
                    if location:
                        plan_obj.ship.location = location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                plan_obj.boat_status_id = 6
                plan_obj.save()
                # 将船舶表的状态也改变过来
                plan_obj.ship.boat_status_id = 6
                plan_obj.ship.save()

    action_multi_complete.text = '完成'
    action_list = [action_multi_complete]

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

    def file_response_download1(self, file_path):
        try:
            response = FileResponse(open(file_path, 'rb'))
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
                escape_uri_path(os.path.basename(file_path)))
            return response
        except Exception:
            return HttpResponse('兄弟，应该是船情没出来。要不等会再试试！！！')

    has_update_today_btn = True

    @property
    def get_time(self):
        e = datetime.datetime.now().year
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day
        c = '%s年%s月%s日' % (e, a, b)
        return c

    def update_today(self, request, *args, **kwargs):

        user_id = request.session['user_info']['id']  # 获取用户的id
        department = request.session['user_info']['department']  # 获取执勤部门
        two_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        Create(two_path, department, user_id, )
        first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\%s%s船情.xls' % (
            department, self.get_time)
        if department == '指挥中心':
            first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\舟山站%s船情.xls' % (
                self.get_time)

        return self.file_response_download1(first_path)
        # return HttpResponse('ok')

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
        obj = self.model_class.objects.filter(pk=pk).first().ship
        obj.boat_status_id = None
        obj.save()
        # 此步骤为了将已经删除的船情申请状态进行恢复。
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^update/$', self.wrapper(self.update_today), name='update_today'),
            re_path(r'^delete/(?P<pk>\d+)/$', self.wrapper(self.delete_view), name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    order_list = ['title__order']
    def get_query_set(self, request, *args, **kwargs):
        # 这里是每个队的工单列表
        obj = request.obj
        if obj.department.title == '指挥中心':
            return self.model_class.objects.filter(boat_status=7)
        a = Q(location__department=obj.department)
        b = Q(last_location__department=obj.department)
        # return self.model_class.objects.filter(boat_status=7, location__department=obj.department)
        # return self.model_class.objects.filter(boat_status=7).filter(a | b).filter(move_time__range=[datetime.date.today() - relativedelta(days=1),datetime.date.today() + relativedelta(days=1)])
        # return self.model_class.objects.filter(a | b).filter(move_time__range=[datetime.date.today() - relativedelta(days=1),datetime.date.today() + relativedelta(days=1)])
        return self.model_class.objects.filter(a | b).filter(move_time__range=[datetime.date.today(),datetime.date.today() + relativedelta(days=1)])
