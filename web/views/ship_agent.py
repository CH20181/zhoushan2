import datetime
from types import FunctionType

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, re_path
from django.utils.safestring import mark_safe
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_choice_text, StarkModelForm
from stark.utils.pagination import Pagination
from web import models


class ShipGetMove(StarkModelForm):
    class Meta:
        model = models.Plan
        fields = ['title', 'move_time', 'next_port', 'note']
        widgets = {
            'move_time': DateTimePickerInput,
        }
        labels = {'next_port': '下一港口'}

    def __init__(self, *args, **kwargs):
        super(ShipGetMove, self).__init__(*args, **kwargs)
        # 此处是添加出港出境计划的视图
        self.fields['title'].queryset = models.PlanStatus.objects.filter(pk__in=[1, 2])

    def clean_move_time(self):
        move_time = self.cleaned_data.get('move_time')
        tomorrow = datetime.date.today() + relativedelta(days=2)
        if tomorrow > move_time.date():
            return move_time
        raise ValidationError('只能申报今天或者明天的船情！！！！')


class ShipCheckModelForm(StarkModelForm):
    class Meta:
        model = models.Ship
        # exclude = ['user', 'boat_status', 'status', 'port_in', 'display', 'location','note']
        exclude = ['user', 'boat_status', 'status', 'display', 'note', ]
        # fields = ['chinese_name','english_name','nationality','crew_detail','crew_total','goods','IMO','MMSI','purpose','guns','last_port','location']
        labels = {'port_in': '泊位（进港船舶填无）', 'location': '船厂/码头/锚地（进港船舶选无）'}

    def __init__(self, *args, **kwargs):
        super(ShipCheckModelForm, self).__init__(*args, **kwargs)
        # 此处是添加出港出境计划的视图
        self.fields['location'].queryset = models.Location.objects.all()

    def clean_port_in(self):
        port_in = self.cleaned_data.get('port_in')
        str_list = ['秀山东', '虾峙门', ]
        for i in str_list:
            if i in port_in:
                raise ValidationError('锚地填写锚地两个字')
        if port_in and len(port_in) < 10:
            return port_in
        raise ValidationError('请输入在港泊位，格式：1#码头2#泊位，锚地填写无')

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location:
            raise ValidationError('请填写该轮在港位置，如果为入境、入港船舶，请选择最后一项“无”')
        return location

    def clean_IMO(self):
        IMO = self.cleaned_data.get('IMO')
        if len(IMO) < 7:
            raise ValidationError('输入的IMO长度不够！')
        return IMO

    def clean_MMSI(self):
        MMSI = self.cleaned_data.get('MMSI')
        if len(MMSI) < 9:
            raise ValidationError('输入的MMSI长度不够！')
        return MMSI


class ShipAgentHandler(StarkHandler):
    """
    代理公司视图
    """
    model_form_class = ShipCheckModelForm
    search_list = ['IMO__contains', 'MMSI__contains', 'chinese_name__contains']
    has_temporary_btn = True

    def display_edit_del(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '操作'
        title = obj.status
        tpl = ''
        if title == 0:
            tpl = "<a href='%s' class='btn btn-warning btn-xs'>编辑</a> <a href='%s' class='btn btn-warning btn-xs'>删除</a>" % (self.reverse_change_url(pk=obj.pk), self.reverse_delete_url(pk=obj.pk))
        elif title == 1:
            tpl = "<a href='%s' class='btn btn-warning btn-xs' style='text-align: center'>归档</a>" % (self.reverse_delete_url(pk=obj.pk))
        return mark_safe(tpl)

    def display_plan(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶计划'
        record_url = reverse('stark:web_plan_agent_list', kwargs={'ship_id': obj.pk})
        return mark_safe("<a class='btn btn-primary btn-sm' href='%s'>计划列表</a>" % record_url)

    def display_move(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '出港/出境'
        record_url = reverse('stark:web_ship_agent_get_move', kwargs={'ship_id': obj.pk})
        return mark_safe('<a  href="%s">添加</a>' % record_url)

    def display_port(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '在港位置'
        location = obj.location
        if not location:
            return obj.port_in
        return '%s%s' % (location, obj.port_in)

    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶名称'
        return '%s\n%s' % (obj.chinese_name, obj.english_name)

    def extra_urls(self):
        return [
            re_path(r'^add/move/(?P<ship_id>\d+)/$', self.wrapper(self.add_move), name=self.get_url_name('get_move')),
        ]

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            return "<a class='btn btn-danger' href='%s'>添加船舶基本信息</a>" % self.reverse_commens_url(self.get_add_url_name,
                                                                                                 *args, **kwargs)
        return None

    def add_move(self, request, *args, **kwargs):
        """
        添加出港/出境
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        user_id = request.session['user_info']['id']
        ship_id = kwargs.get('ship_id')
        form = ShipGetMove()
        ship_obj = models.Ship.objects.filter(pk=ship_id).first()
        if ship_obj:
            name = ship_obj.chinese_name
        else:
            name = None
        if request.method == 'POST':
            form = ShipGetMove(request.POST)
            # print(request.POST)
            if form.is_valid():
                location = models.Ship.objects.filter(pk=ship_id).first().location
                # 阻止未入港的船直接申请出境
                title_id = form.instance.title_id
                # 判断是否为补报船舶
                move_time = form.instance.move_time
                now_time = datetime.datetime.now()
                try:
                    if move_time.date() == datetime.date.today() and now_time > datetime.datetime(
                            datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
                            16, 00):
                        return render(request, 'error.html',
                                      {'msg': '根据规定，当日补报计划不得迟于当天下午16:00，详情请咨询指挥中心。', 'url': 'stark:web_plan_agent_list',
                                       'pk': ship_id})
                    elif now_time > datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,
                                                      datetime.datetime.now().day, 16,
                                                      00) or move_time.date() == datetime.date.today():
                        form.instance.report = 4
                except:
                    pass
                if title_id == 1 or title_id == 2:
                    is_alive = models.Ship.objects.filter(pk=ship_id).first().location_id
                    if is_alive == 83:
                        is_have_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5]).first()
                        if not is_have_into:
                            # return HttpResponse('该船不在港，或没有在港位置，不能申请出港、出境')
                            return render(request, 'error.html',
                                          {'msg': '该船不在港，或没有在港位置，不能申请出港、出境', 'url': 'stark:web_plan_agent_list',
                                           'pk': ship_id})
                # print(location)
                # 先获取原来的所属执勤队，在这次添加出港出境计划后
                title_num = form.instance.title_id  # 船舶计划名称的id
                form.instance.ship_id = ship_id
                form.instance.agent_id = user_id
                form.instance.boat_status_id = title_num  # 船舶状态的id
                # plan_obj = models.Plan.objects.filter(ship_id=ship_id, title__in=[3, 4, 5],boat_status__in=[3,4,5])
                plan_obj = models.Plan.objects.filter(ship_id=ship_id, title__in=[3, 4, 5])
                if plan_obj:
                    try:
                        form.instance.last_location_id = plan_obj.last().location_id
                        form.instance.last_port = plan_obj.last().next_port
                    except:
                        form.instance.last_location_id = models.Ship.objects.filter(pk=ship_id).first().location_id
                        form.instance.last_port = ''
                else:
                    form.instance.last_location_id = models.Ship.objects.filter(pk=ship_id).first().location_id
                    form.instance.last_port = models.Ship.objects.filter(pk=ship_id).first().port_in
                form.save()
                form.instance.ship.boat_status_id = title_num
                form.instance.ship.agent_id = user_id
                form.instance.ship.save()
                return redirect(reverse('stark:web_plan_agent_list', kwargs={'ship_id': ship_id}))
        return render(request, 'stark/change.html', {'form': form, 'name': name})

    list_display = [display_name, 'IMO', 'MMSI', 'nationality', 'crew_detail', 'goods', 'purpose',
                    'last_port', display_port, 'boat_status',
                    get_choice_text('是否在港', 'status'), display_plan, ]

    def save(self, form, request, is_update, *args, **kwargs):
        user_id = request.session['user_info']['id']
        if not is_update:
            form.instance.user_id = user_id
        form.save()

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
        obj = models.Ship.objects.filter(pk=pk, status=1)
        # 船舶如果已经属于在港或者离港，就不能删除
        if obj:
            obj.update(display=2)
            return redirect(origin_list_url)
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)

    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """
        current_change_object = self.model_class.objects.filter(pk=pk).first()
        if not current_change_object:
            # return HttpResponse('要修改的数据不存在，请重新选择！')
            return render(request, 'error.html',
                          {'msg': '要修改的数据不存在，请重新选择！！', 'url': 'stark:web_ship_agent_list', 'pk': None})
        obj = models.Ship.objects.filter(pk=pk).filter(status=0)
        if not obj:
            # return HttpResponse('禁止修改！！！')
            return render(request, 'error.html', {'msg': '禁止修改！！！', 'url': 'stark:web_ship_agent_list', 'pk': None})
        # obj = self.model_class.objects.filter(status__in=[1, 2]).first()
        # obj = models.Ship.objects.filter(status__in=[1, 2]).first()
        # print(obj)
        # if obj:
        #     return HttpResponse('禁止修改！！！')

        model_form_class = self.get_model_form_class(False, request, pk, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class(instance=current_change_object)
            return render(request, self.change_template or 'stark/change.html', {'form': form})
        form = model_form_class(data=request.POST, instance=current_change_object)
        if form.is_valid():
            response = self.save(form, request, is_update=True, *args, **kwargs)
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.change_template or 'stark/change.html', {'form': form})

    # 过滤没有被删除的船舶，后期加上代理公司的id进行过滤
    # order_list = ['-plan__move_time']
    def get_query_set(self, request, *args, **kwargs):
        obj = request.obj
        # print(self.model_class.objects.filter(display=1, user__company=obj.company).filter(status__in=[0, 1]))
        # print(self.model_class.objects.filter(display=1, user__company=obj.company).filter(status__in=[0, 1]).values('plan','plan__move_time'))
        obj_list = self.model_class.objects.filter(display=1, user__company=obj.company).filter(status__in=[0, 1])
        pk_list = []
        if obj_list:
            for i in obj_list:
                is_obj = i.plan_set.all().first()
                if not is_obj:
                    pk_list.append(i.pk)
                else:
                    pk_list.insert(0, i.plan_set.all().first().ship_id)
            query_list = self.model_class.objects.filter(pk__in=pk_list).filter(display=1,
                                                                                user__company=obj.company).filter(
                status__in=[0, 1])
        else:
            query_list = obj_list
        # return self.model_class.objects.filter(display=1, user__company=obj.company).filter(status__in=[0, 1])
        return query_list

    def changelist_view(self, request, *args, **kwargs):
        """
        列表页面
        :param request:
        :return:
        """
        # ########## 1. 处理Action ##########
        action_list = self.get_action_list()
        action_dict = {func.__name__: func.text for func in action_list}  # {'multi_delete':'批量删除','multi_init':'批量初始化'}

        if request.method == 'POST':
            action_func_name = request.POST.get('action')
            if action_func_name and action_func_name in action_dict:
                action_response = getattr(self, action_func_name)(request, *args, **kwargs)
                if action_response:
                    return action_response

        # ########## 2. 获取排序 ##########
        search_list = self.get_search_list()
        search_value = request.GET.get('q', '')
        conn = Q()
        conn.connector = 'OR'
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value))

        # ########## 3. 获取排序 ##########

        # 获取组合的条件
        query_set = self.get_query_set(request, *args, **kwargs)
        search_group_condition = self.get_search_group_condition(request)
        queryset = query_set.filter(**search_group_condition)
        # ########## 4. 处理分页 ##########
        all_count = queryset.count()

        query_params = request.GET.copy()
        query_params._mutable = True

        pager = Pagination(
            current_page=request.GET.get('page'),
            all_count=all_count,
            base_url=request.path_info,
            query_params=query_params,
            per_page=self.per_page_count,
        )

        data_list = queryset[pager.start:pager.end]

        # ########## 5. 处理表格 ##########
        list_display = self.get_list_display(request, *args, **kwargs)
        # 5.1 处理表格的表头
        header_list = []
        if list_display:
            for key_or_func in list_display:
                if isinstance(key_or_func, FunctionType):
                    verbose_name = key_or_func(self, obj=None, is_header=True, *args, **kwargs)
                else:
                    verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
                header_list.append(verbose_name)
        else:
            header_list.append(self.model_class._meta.model_name)

        # 5.2 处理表的内容

        body_list = []
        for row in data_list:
            tr_list = []
            if list_display:
                for key_or_func in list_display:
                    if isinstance(key_or_func, FunctionType):
                        tr_list.append(key_or_func(self, row, is_header=False, *args, **kwargs))
                    else:
                        tr_list.append(getattr(row, key_or_func))  # obj.gender
            else:
                tr_list.append(row)
            body_list.append(tr_list)

        # ########## 6. 添加按钮 #########
        add_btn = self.get_add_btn(request, *args, **kwargs)
        update_btn = self.get_update_btn(request, *args, **kwargs)
        update_today_btn = self.get_update_today_btn(request, *args, **kwargs)
        temporary_btn = self.get_temporary_btn(request, *args, **kwargs)
        move_btn = self.get_move_btn(request, *args, **kwargs)
        # ########## 7. 组合搜索 #########
        search_group_row_list = []
        search_group = self.get_search_group()  # ['gender', 'depart']
        for option_object in search_group:
            row = option_object.get_queryset_or_tuple(self.model_class, request, *args, **kwargs)
            search_group_row_list.append(row)

        return render(
            request,
            self.change_list_template or 'stark/changelist.html',
            {
                'data_list': data_list,
                'header_list': header_list,
                'body_list': body_list,
                'pager': pager,
                'add_btn': add_btn,
                'update_btn': update_btn,
                'update_today_btn': update_today_btn,
                'temporary_btn': temporary_btn,
                'move_btn': move_btn,
                'search_list': search_list,
                'search_value': search_value,
                'action_dict': action_dict,
                'search_group_row_list': search_group_row_list
            }
        )
