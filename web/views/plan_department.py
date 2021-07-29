from django.urls import re_path

from stark.service.v1 import StarkHandler, get_datetime_text


class PlanDepartmentHandler(StarkHandler):
    """
    执勤队船情视图
    """

    def get_query_set(self, request, *args, **kwargs):
        ship_id = kwargs.get("ship_id")
        # print(1111,self.model_class.objects.filter(pk=ship_id, ))
        return self.model_class.objects.filter(ship=ship_id, )

    def display_location(self, obj=None, is_header=None, *args, **kwargs):
        if is_header:
            return '停靠地点'
        location = obj.location
        if not location:
            return '%s' % obj.next_port
        return '%s--%s' % (obj.location, obj.next_port)

    has_add_btn = False
    list_display = ['ship', 'title', get_datetime_text('计划时间', 'move_time'),
                    display_location,
                    'boat_status']

    def get_urls(self):
        """
        生成URL
        :return:
        """
        patterns = [
            re_path(r'^list/(?P<ship_id>\d+)/$', self.wrapper(self.changelist_view), name=self.get_list_url_name),
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
