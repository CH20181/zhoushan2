from django.urls import re_path

from django.db.models import Q
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_datetime_text, StarkModelForm
from web import models


############## 指挥中心审核船情

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
            return obj.next_port
        type_obj = obj.title
        if type_obj.title == '入境' or type_obj.title == '入港':
            try:
                return '%s--->%s' % (obj.ship.last_port, str(obj.location.title + obj.next_port))
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
            # print(plan_obj_number,type(plan_obj_number),plan_obj[1])
            try:
                if plan_obj_number != None:
                    return '%s--->%s' % (plan_obj[plan_obj_number].location.title + plan_obj[plan_obj_number].next_port, obj.location.title + obj.next_port)
                return '%s--->%s' % (obj.ship.location.title + obj.ship.port_in, obj.location.title + obj.next_port)
            except:
                return '%s--->%s' % (obj.ship.location.title + obj.ship.port_in, obj.location.title)
        # 出港、出境
        else:
            ship_id = obj.ship_id
            # 此处判断是否为当天入出船舶
            is_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5]).first()
            if is_into:
                return '%s----->%s' % (is_into.location.title + is_into.next_port, obj.next_port)
            # print(type_obj.title,obj.location.title,obj.next_port)
            try:
                return '%s--->%s' % (obj.ship.location.title, obj.next_port)
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
            return 'IMO'
        return obj.ship.IMO

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

    def get_query_set(self, request, *args, **kwargs):
        return self.model_class.objects.filter(~Q(boat_status=6))

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
                    'boat_status', display_agent]
