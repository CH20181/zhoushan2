import re

from django.forms import fields, widgets
from django.shortcuts import render, redirect
from web import models
from web.utils.md5 import gen_md5
from rbac.service.init_permission import init_permission
from stark.service.v1 import StarkModelForm
from django import forms
from django.core.exceptions import ValidationError


def login(request):
    """
    用户登录
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html', )
    user = request.POST.get('user')
    pwd = gen_md5(request.POST.get('pwd', ''))
    # 根据用户名和密码去用户表中获取用户对象
    user = models.UserInfo.objects.filter(name=user, password=pwd).first()
    if not user:
        return render(request, 'login.html', {'msg': '用户名或密码错误'})
    request.session['user_info'] = {'id': user.id, 'nickname': user.nickname, 'department': str(user.department), }
    # 用户权限信息的初始化
    init_permission(user, request)
    return redirect('/index/')


class UserinfoModelForm(forms.ModelForm):
    r_password = forms.CharField(label='确认密码', widget=forms.TextInput(attrs={'type': 'password'}))

    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'r_password', 'email', 'nickname','phone', 'company', 'gender']
        widgets = {
            'password': forms.TextInput(attrs={'type': 'password'}),
            'gender': forms.RadioSelect(choices=[(1, "男"), (2, "女"), ])
        }

    def __init__(self, *args, **kwargs):
        super(UserinfoModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'gender':
                continue
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if re.match(r"^1[35678]\d{9}$", phone):
            return phone
        else:
            raise ValidationError('手机号码格式错误！')

    def clean_r_password(self):
        password = self.cleaned_data.get('password')
        r_password = self.cleaned_data.get('r_password')
        if password == r_password:
            return r_password
        raise ValidationError('两次输入的密码不一致！！！')


def register(request):
    form = UserinfoModelForm()
    if request.method == 'POST':
        form = UserinfoModelForm(request.POST)
        if form.is_valid():
            r_password = request.POST.get('r_password')
            form.instance.password = gen_md5(r_password)
            form.save()
            return redirect('login')
    return render(request, 'register.html', {'form': form})


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    request.session.delete()

    return redirect('/login/')


def index(request):
    return render(request, 'index.html')
