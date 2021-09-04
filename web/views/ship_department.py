import os
from django.urls import re_path, reverse
from django.utils.encoding import escape_uri_path
from django.utils.safestring import mark_safe
from django.http import HttpResponse, Http404, FileResponse
from stark.service.v1 import StarkHandler, get_datetime_text, get_choice_text
from web.create_file import Create


# 各执勤队在港船舶预览

class ShipDepartmentHandler(StarkHandler):
    """
    代理公司视图
    """
    per_page_count = 100
    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '名称'
        return '%s   %s' % (obj.chinese_name, obj.english_name)

    has_add_btn = False
    search_list = ['IMO__contains', 'MMSI__contains', 'chinese_name__contains']
    has_update_btn = True

    def file_response_download1(self, file_path):
        try:
            response = FileResponse(open(file_path, 'rb'))
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(
                escape_uri_path(os.path.basename(file_path)))
            return response
        except Exception:
            raise Http404

    def update(self, request, *args, **kwargs):
        user_id = request.session['user_info']['id']  # 获取用户的id
        department = request.session['user_info']['department']  # 获取执勤部门
        two_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        Create(two_path, department, user_id, )
        first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\%s在港船舶动态.xls' % department
        if department == '指挥中心':
            first_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\舟山站在港船舶动态.xls'
        return self.file_response_download1(first_path)

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
            re_path(r'^update/$', self.wrapper(self.update), name='update'),
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
        location = obj.location
        if not location:
            return obj.port_in
        return '%s--%s' % (location, obj.port_in)

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶代理'
        return '%s-%s:%s' % (obj.user.company.title[0:5], obj.user, obj.user.phone)
    order_list = ['location']
    def get_query_set(self, request, *args, **kwargs):
        # 在这里过滤所属船舶
        user_obj = request.obj
        if request.session['user_info']['department'] == '指挥中心':
            # 返回在港或者位置的船舶
            return self.model_class.objects.filter(status=1)
            # return self.model_class.objects
        # return self.model_class.objects.filter(status=1, location__department=user_obj.department)
        return self.model_class.objects.filter(status=1, location__department=user_obj.department)

    def display_information(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '查看详情'
        base_url = reverse('stark:web_plan_department_list', kwargs={'ship_id': obj.pk})
        return mark_safe("<a href='%s' class='btn btn-primary btn-xs'>历史船情</a>" % base_url)
    def display_crew_detail(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船员国籍和人数'
        if len(obj.crew_detail) > 20:
            str_list = list(obj.crew_detail)
            str_list.insert(20,'222222')
            str_out = ''.join(str_list)
            print(str_out,22222)
            return mark_safe(str_out)
        return obj.crew_detail

    list_display = [display_name, 'nationality', 'IMO', 'MMSI', 'crew_total', display_crew_detail, 'purpose', 'last_port',
                    display_port,
                    get_choice_text('船舶状态', 'status'), display_information, get_datetime_text('添加时间', 'create_time'),
                    display_agent]
