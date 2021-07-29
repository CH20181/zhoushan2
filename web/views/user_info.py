from stark.service.v1 import StarkHandler,get_choice_text,StarkModelForm
from web import models



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
