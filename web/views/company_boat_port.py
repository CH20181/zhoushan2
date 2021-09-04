import datetime
import os

from django.shortcuts import render, redirect
from django.urls import re_path, reverse
from django.utils.encoding import escape_uri_path
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404, FileResponse
from stark.service.v1 import StarkHandler, get_datetime_text, get_choice_text
from web import models
from web.create_file import Create
from django import forms


# 各执勤队在港船舶预览
class ShipView(forms.Form):
    chinese_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}),
                                   label='中文名', required=False)
    english_name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}),
                                   label='英文名', required=False)
    nationality = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}), label='国籍',
                                  required=False)
    crew_detail = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control", 'disabled': True}),
                                  label='船员分布', required=False)
    goods = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}), label='货物',
                            required=False)
    IMO = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}), label='IMO',
                          required=False)
    MMSI = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}), label='MMSI',
                           required=False)
    purpose = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control", 'disabled': True}), label='目的',
                              required=False)
    port_in = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}), label='当前泊位')
    note = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control",'placeholder':"请填写移泊时间"}), label='备注',required=False)


class CompanyPortHandler(StarkHandler):
    """
    代理公司视图
    """
    per_page_count = 50
    change_template = 'company.html'

    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶名称'
        try:
            return '%s   %s' % (obj.chinese_name, obj.english_name)
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
            re_path(r'^change/(?P<pk>\d+)/$', self.wrapper(self.change_view), name=self.get_change_url_name),
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

    def display_port(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '在港位置'
        return obj.port_in

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶代理'
        return '%s-%s:%s' % (obj.user.company.title[0:5], obj.user, obj.user.phone)

    def display_report(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '1'
        return obj.report

    def display_edit(self, obj=None, is_header=None, *args, **kwargs):
        """
        自定义页面显示的列（表头和内容）
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return "更改位置"
        return mark_safe("<a href='%s' class='btn btn-danger btn-xs'>移泊</a>" % self.reverse_change_url(pk=obj.pk))

    def change_view(self, request, pk, *args, **kwargs):
        """
        编辑页面
        :param request:
        :param pk:
        :return:
        """
        current_change_object = self.model_class.objects.filter(pk=pk).first()
        is_owener = current_change_object.location
        if not current_change_object or is_owener != request.obj.company_port:
            return render(request, 'error.html', {'msg': '要修改的数据不存在，请重新选择！', 'url': 'stark:web_ship_company_view_list'})

        if request.method == 'GET':
            del current_change_object.__dict__['note']
            del current_change_object.__dict__['port_in']
            form = ShipView(data=current_change_object.__dict__)
            return render(request, self.change_template or 'stark/change.html', {'form': form})
        form = ShipView(data=request.POST)
        if form.is_valid():
            port_in = request.POST.get("port_in", "")
            last_port = current_change_object.__dict__['port_in']
            note = request.POST.get("note", "")
            obj = request.obj.pk
            models.MovePlan.objects.create(port_in=port_in, last_port=last_port, user_id=obj,note=note)
            models.Ship.objects.filter(pk=pk).update(port_in=port_in)
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            return redirect(reverse('stark:web_ship_company_view_list'))
        del current_change_object.__dict__['note']
        del current_change_object.__dict__['port_in']
        form = ShipView(data=current_change_object.__dict__)
        return render(request, self.change_template or 'stark/change.html', {'form': form})

    def get_query_set(self, request, *args, **kwargs):
        # 在这里过滤所属船舶
        user_obj = request.obj
        print(self.model_class,111111)
        return self.model_class.objects.filter(location=user_obj.company_port, status=1)

    list_display = [display_name, display_port, display_edit, 'MMSI', 'IMO', display_agent]
