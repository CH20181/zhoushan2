from stark.service.v1 import StarkHandler


class LocationHandler(StarkHandler):
    """
    代理公司视图
    """
    list_display = ['title','department']