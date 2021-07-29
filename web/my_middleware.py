from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from web import models
import re
from test3 import settings


# 此处加登录认证
#  自定义中间件，可以定制很多方法。添加参数
class UserAuth(MiddlewareMixin):
    def process_request(self, request):
        current_url = request.path_info
        for valid_url in settings.VALID_URL_LIST:
            if re.match(valid_url, current_url):
                # 白名单中的URL无需权限验证即可访问
                return None
            elif re.match('^/$',current_url):
                return None

        user_id = request.session['user_info'].get('id')
        if user_id:
            obj = models.UserInfo.objects.get(id=user_id)
            # 将当前用户登录对象封装到request对象中
            request.obj = obj
            return
        else:
            return redirect('login')
