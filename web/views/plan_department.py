import datetime

from django.urls import re_path

from stark.service.v1 import StarkHandler, get_datetime_text
from web import models


class PlanDepartmentHandler(StarkHandler):
    """
    执勤队船情视图
    """

    def get_query_set(self, request, *args, **kwargs):
        ship_id = kwargs.get("ship_id")
        # print(1111,self.model_class.objects.filter(pk=ship_id, ))
        return self.model_class.objects.filter(ship=ship_id, )
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
                is_remove = models.Plan.objects.filter(ship_id=ship_id, title_id=3,boat_status_id__in=[1, 2, 3, 4, 5, 7, 8, 9],move_time__year=datetime.datetime.now().year,move_time__month=datetime.datetime.now().month,move_time__day=datetime.datetime.now().day)
                if is_remove:
                    try:
                        return '%s----->%s' % (is_remove.last().location.title + is_remove.last().last_port,obj.next_port)
                    except:
                        return obj.next_port
                return '%s----->%s' % (is_into.location.title + is_into.next_port, obj.next_port)
            # print(type_obj.title,obj.location.title,obj.next_port)
            try:

                return '%s--->%s' % (obj.last_location.title+obj.last_port, obj.next_port)
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
    # def display_location(self, obj=None, is_header=None, *args, **kwargs):
    #     if is_header:
    #         return '停靠地点'
    #     location = obj.location
    #     if not location:
    #         return '%s' % obj.next_port
    #     return '%s--%s' % (obj.location, obj.next_port)

    has_add_btn = False
    list_display = ['ship', 'title', get_datetime_text('计划时间', 'move_time'),
                    display_location,
                    'boat_status']

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/(?P<ship_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
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
        return value
