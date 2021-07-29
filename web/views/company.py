from stark.service.v1 import StarkHandler


class CompanyHandler(StarkHandler):
    """
    代理公司视图
    """
    list_display = ['title','phone','addr','email']