from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import re_path, reverse
from stark.service.v1 import StarkHandler, StarkModelForm
from web import models


class GetTemporaryModelForm(StarkModelForm):
    class Meta:
        model = models.Ship
        exclude = ['user', 'boat_status', 'status', 'display', 'last_port', 'note', 'purpose']
        labels = {'port_in': '在港泊位(锚地填写锚地)'}

    def __init__(self, *args, **kwargs):
        super(GetTemporaryModelForm, self).__init__(*args, **kwargs)
        # 此处是添加出港出境计划的视图
        self.fields['location'].queryset = models.Location.objects.all()

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


class ShipTemporaryHandler(StarkHandler):
    """
    代理公司视图
    """
    model_form_class = GetTemporaryModelForm

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^add/$', self.wrapper(self.add_view), name=self.get_add_url_name),
        ]

        patterns.extend(self.extra_urls())
        return patterns

    # 给添加的船舶加上用户标签
    def save(self, form, request, is_update, *args, **kwargs):
        user_id = request.session['user_info']['id']
        if not is_update:
            form.instance.user_id = user_id
        form.save()

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
        form = model_form_class(data=request.POST)
        if form.is_valid():
            response = self.save(form, request, is_update=False, *args, **kwargs)
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            # 添加跳转路径
            return response or redirect(reverse('stark:web_ship_agent_list'))
        return render(request, self.add_template or 'stark/change.html', {'form': form})
