from django.shortcuts import render, redirect

from stark.service.v1 import StarkHandler,get_choice_text,StarkModelForm
from web import models
from web.utils.md5 import gen_md5


class UserInfoModelForm(StarkModelForm):
    """
    用户model类
    """
    class Meta:
        model = models.UserInfo
        fields = ['name','password','phone','email','company','department']

class UserInfoHandler(StarkHandler):
    """
    用户视图
    """
    model_form_class = UserInfoModelForm
    list_display = ['name','nickname',get_choice_text('性别','gender'),'phone','company']
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
        form = model_form_class(data=request.POST.copy())
        password = gen_md5(form.data['password'])
        form.data['password'] = password
        if form.is_valid():
            response = self.save(form, request, is_update=False, *args, **kwargs)
            # 在数据库保存成功后，跳转回列表页面(携带原来的参数)。
            return response or redirect(self.reverse_list_url(*args, **kwargs))
        return render(request, self.add_template or 'stark/change.html', {'form': form})
