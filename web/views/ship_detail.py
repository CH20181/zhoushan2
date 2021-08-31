import os
import time
from types import FunctionType

from django.conf.urls import url
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import re_path
from django.utils.safestring import mark_safe

from test3 import settings
from web import models
from web.models import ShipDetail
from stark.service.v1 import StarkHandler
from stark.utils.pagination import Pagination
from django import forms


class ShipDetailForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField()
    file = forms.CharField()


class ShipDetailView(StarkHandler):
    """
    代理公司视图
    """
    change_list_template = 'shipdetail.html'
    add_template = 'shipdetail.html'
    change_list_template = 'shipdetaillist.html'
    has_add_btn = True

    def get_urls(self):
        """
        生成URL
        :return:
        """

        patterns = [
            # url(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            # url(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^list/(?P<ship_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^add/(?P<ship_id>\d+)/$', self.wrapper(self.add_view), name=self.get_add_url_name),
            re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
            re_path(r'^delete/(?P<pk>\d+)/(?P<ship_id>\d+)/$', self.wrapper(self.delete_view),
                    name=self.get_delete_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    def get_add_btn(self, request, *args, **kwargs):
        if self.has_add_btn:
            return "<a class='btn btn-warning' href='%s'>添加报备信息</a>" % self.reverse_commens_url(self.get_add_url_name,
                                                                                                *args, **kwargs)
        return None

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
        # header_list = []
        # if list_display:
        #     for key_or_func in list_display:
        #         if isinstance(key_or_func, FunctionType):
        #             verbose_name = key_or_func(self, obj=None, is_header=True, *args, **kwargs)
        #         else:
        #             verbose_name = self.model_class._meta.get_field(key_or_func).verbose_name
        #         header_list.append(verbose_name)
        # else:
        #     header_list.append(self.model_class._meta.model_name)
        body_list = {}
        shi_id = kwargs.get('ship_id')
        obj_list = models.ShipDetail.objects.filter(ship_id=shi_id)
        if obj_list:
            for i in obj_list:
                body_list[i.title] = [i.content,i.file,i.add_time,i.old_name]

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
            }
        )

    def upload_file(self, request,*args, **kwargs):
        user_id = request.session['user_info']['id']
        ship_id = kwargs.get('ship_id')
        img = request.FILES.get("file")
        url = 'media/'
        img_name = int(time.time())
        if img:
            old_name = img.name
            suffix = old_name.rsplit(".")[-1]
            dir = os.path.join(os.path.join(settings.BASE_DIR, 'media'), str(img_name) + '.' + suffix)
            destination = open(dir, 'wb+')
            for chunk in img.chunks():
                destination.write(chunk)
            destination.close()
            file_name = url + str(img_name) + '.' + suffix  # 拿到图片的名字
        else:
            file_name = None
            old_name = ''
        new_img = models.ShipDetail(
            ship_id=ship_id,
            user_id=user_id,
            title=request.POST.get('title'),  # 拿到图片
            content=request.POST.get('content'),  # 拿到图片
            file=file_name,
            old_name=old_name
        )
        new_img.save()
        return True

    def add_view(self, request, *args, **kwargs):
        """
        添加页面
        :param request:
        :return:
        """

        model_form_class = self.get_model_form_class(True, request, None, *args, **kwargs)
        if request.method == 'GET':
            form = model_form_class()
            return render(request, self.add_template or 'stark/change.html', {'form': form})
        ret = self.upload_file(request, *args, **kwargs)
        if ret:
            return redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template, {'error': '未添加成功'})

    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """
        current_change_object = self.model_class.objects.filter(pk=pk).first()
        if not current_change_object:
            return HttpResponse('要修改的数据不存在，请重新选择！')

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
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(origin_list_url)
