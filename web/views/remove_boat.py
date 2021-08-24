from django.urls import re_path, reverse
from stark.service.v1 import StarkHandler, get_datetime_text, get_choice_text
from django.utils.safestring import mark_safe


# 各执勤队离港船舶预览
class ShipRemoveHandler(StarkHandler):
    """
    执勤队视图，指挥中心视图
    """

    def display_name(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '名称'
        return '%s   %s' % (obj.chinese_name, obj.english_name)

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
            return '离港之前的位置'
        location = obj.location
        if not location:
            return obj.port_in
        return '%s' % location

    def display_agent(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '船舶代理'
        return '%s-%s:%s' % (obj.user.company, obj.user, obj.user.phone)

    def get_query_set(self, request, *args, **kwargs):
        # 在这里过滤所属船舶
        user_obj = request.obj
        if request.session['user_info']['department'] == '指挥中心':
            # return self.model_class.objects.filter(status=1)
            return self.model_class.objects.filter(status=2)
        # return self.model_class.objects.filter(status=1, location__department=user_obj.department)
        return self.model_class.objects.filter(status=2, location__department=user_obj.department)

    def display_information(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '查看详情'
        base_url = reverse('stark:web_plan_department_list', kwargs={'ship_id': obj.pk})
        return mark_safe("<a href='%s' class='btn btn-primary btn-xs'>历史船情</a>" % base_url)

    list_display = [display_name, 'nationality', 'crew_total', 'IMO', 'MMSI', 'crew_detail', 'purpose', 'last_port',
                    display_port,
                    get_choice_text('船舶状态', 'status'), display_information, get_datetime_text('添加时间', 'create_time'),
                    display_agent]
