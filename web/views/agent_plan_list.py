import datetime
import os
from django.urls import re_path, reverse
from django.utils.encoding import escape_uri_path
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404, FileResponse
from stark.service.v1 import StarkHandler, get_datetime_text, get_choice_text
from web import models
from web.create_file import Create


# 各执勤队在港船舶预览

class AgentPlanHandler(StarkHandler):
    """
    代理公司视图
    """
    per_page_count = 50
    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶名称'
        try:
            return '%s   %s' % (obj.ship.chinese_name, obj.english_name)
        except:
            return '%s' % obj.ship.chinese_name


    has_add_btn = False

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

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

    def display_port(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '在港位置'
        location = obj.location
        if not location:
            return obj.port_in
        return '%s--%s' % (location, obj.port_in)
    def display_ship(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶名称'
        location = obj.ship.Chinesename
        if not location:
            return obj.port_in
        return '%s--%s' % (location, obj.port_in)

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶代理'
        return '%s-%s:%s' % (obj.user.company.title[0:5], obj.user, obj.user.phone)
    def display_report(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '1'
        return obj.report
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

    def display_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return "取消计划"
        ship_id = obj.ship.pk
        if obj.boat_status_id == 6:
            return mark_safe("<a href='#' class='btn btn-danger btn-xs' disabled='disabled'>取消</a>")
        return mark_safe("<a href='%s' class='btn btn-danger btn-xs'>取消</a>" % reverse('stark:web_plan_agent_delete', kwargs={'ship_id': ship_id,'pk':obj.pk}))

    def get_query_set(self, request, *args, **kwargs):
        # 在这里过滤所属船舶
        user_obj = request.obj
        return self.model_class.objects.filter(agent__company=user_obj.company,move_time__gt=datetime.date.today())

    def display_information(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '查看详情'
        base_url = reverse('stark:web_plan_department_list', kwargs={'ship_id': obj.pk})
        return mark_safe("<a href='%s' class='btn btn-primary btn-xs'>历史船情</a>" % base_url)
    def display_crew_detail(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船员国籍和人数'
        if len(obj.crew_detail) > 20:
            str_list = list(obj.crew_detail)
            str_list.insert(20,'222222')
            str_out = ''.join(str_list)
            print(str_out,22222)
            return mark_safe(str_out)
        return obj.crew_detail

    list_display = ['ship','title',get_datetime_text('计划时间', 'move_time', time_format='%Y-%m-%d %H:%M'),display_location,get_datetime_text('申报时间', 'apply', time_format='%Y-%m-%d %H:%M'),display_report,'boat_status']
