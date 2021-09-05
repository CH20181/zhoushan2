from django.db.models import Q
from django.shortcuts import render
from django.urls import re_path, reverse
from stark.service.v1 import StarkHandler
from stark.utils.pagination import Pagination



class AllShipDetailView(StarkHandler):
    """
    代理公司视图
    """
    add_template = 'shipdetail.html'
    change_list_template = 'shipdetaillist.html'
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


    order_list = ['status']
    def get_query_set(self, request, *args, **kwargs):
        return self.model_class.objects.all()



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
        order_list = self.get_order_list()
        # 获取组合的条件
        query_set = self.get_query_set(request, *args, **kwargs)
        search_group_condition = self.get_search_group_condition(request)
        queryset = query_set.filter(conn).filter(**search_group_condition).order_by(*order_list)

        # ########## 4. 处理分页 ##########
        all_count = queryset.count()
        if all_count < 10:
            is_show = False
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

        body_list = {}
        obj_list = queryset
        if obj_list:
            for i in obj_list:
                note = i.note
                if note:
                    #   0    1    2        3      4    5    6     7
                    # 内容、文件、申报时间、原始名称、id、船名、url 、备注
                    del_url = ''
                    body_list[i.title] = [i.content,i.file,i.add_time,i.old_name,i.id,i.ship.chinese_name,del_url,i.note]
                else:
                    del_url = reverse('stark:web_shipdetail_detail_delete', kwargs={'pk': i.id,'ship_id':i.ship_id})
                    #   0   1    2          3     4   5     6
                    # 内容、文件、申报时间、原始名称、id、船名、删除url
                    body_list[i.title] = [i.content, i.file, i.add_time, i.old_name, i.id,i.ship.chinese_name,del_url]
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
                'body_list': body_list,
                'pager': pager,
                'add_btn': add_btn,
                'id':request.obj.pk,
                'is_show':is_show,
                'url': reverse('stark:web_shipdetail_alldetail_list')
            }
        )
