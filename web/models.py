from django.db import models
from rbac.models import UserInfo as RbacUserInfo


# Create your models here.

class UserInfo(RbacUserInfo):
    """
    用户表
    """
    nickname = models.CharField(verbose_name='真实姓名', max_length=16)
    phone = models.CharField(verbose_name='手机号', max_length=32)

    gender_choices = (
        (1, '男'),
        (2, '女'),
    )
    gender = models.IntegerField(verbose_name='性别', choices=gender_choices, default=1)

    company = models.ForeignKey(verbose_name='代理公司', to="Company", on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(verbose_name='所属执勤队', to='Department', blank=True, null=True,
                                   on_delete=models.CASCADE)

    def __str__(self):
        return self.nickname


class Company(models.Model):
    """
    代理公司
    """
    title = models.CharField(verbose_name='公司名称', max_length=32)
    addr = models.CharField(verbose_name='地址', max_length=64)
    email = models.EmailField(verbose_name='公司邮箱')
    phone = models.CharField(verbose_name='电话', max_length=20)

    def __str__(self):
        return self.title


class Department(models.Model):
    """
    执勤队
    """
    title = models.CharField(verbose_name='执勤队名称', max_length=12)
    addr = models.CharField(verbose_name='地址', max_length=32)
    phone = models.CharField(verbose_name='电话', max_length=12)
    email = models.EmailField(verbose_name='邮箱')

    def __str__(self):
        return self.title


class Location(models.Model):
    """
    船厂码头表
    """
    title = models.CharField(verbose_name='船厂/码头名称', max_length=64)
    department = models.ForeignKey(verbose_name='所属执勤队', to='Department', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title


class Ship(models.Model):
    """
    船舶表
    """
    chinese_name = models.CharField(verbose_name='中文名', max_length=32)
    english_name = models.CharField(verbose_name='英文名', max_length=32)
    nationality = models.CharField(verbose_name='国籍', max_length=16)
    crew_detail = models.TextField(verbose_name='船员国籍和人数')
    crew_total = models.PositiveIntegerField(verbose_name='船员总数')
    goods = models.CharField(verbose_name='货物情况', max_length=32)
    IMO = models.CharField(verbose_name='IMO', max_length=7)
    MMSI = models.CharField(verbose_name='MMSI', max_length=9)
    purpose = models.CharField(verbose_name='来港目的', max_length=32)
    guns_choise = (
        (1, '无'),
        (2, '有')
    )
    guns = models.IntegerField(verbose_name='枪支弹药', choices=guns_choise, default=1)
    last_port = models.CharField(verbose_name='上一港', max_length=32)
    user = models.ForeignKey(verbose_name='申报人', blank=True, null=True, to='UserInfo', on_delete=models.CASCADE)
    note = models.TextField(verbose_name='备注', blank=True, null=True)

    boat_status = models.ForeignKey(verbose_name='船舶申请状态', to='BoatStatus', on_delete=models.CASCADE, null=True,
                                    blank=True)

    create_time = models.DateTimeField(verbose_name='添加时间', auto_now_add=True, null=True)
    status_type = (
        (0, '暂无'),
        (1, '在港'),
        (2, '离港'),
    )
    status = models.IntegerField(verbose_name='是否在港', default=0, null=True, blank=True, choices=status_type)
    location = models.ForeignKey(verbose_name='船厂/码头', to='Location', on_delete=models.CASCADE, null=True, blank=True)
    port_in = models.CharField(verbose_name='在港位置', null=True, blank=True, max_length=42)
    display_choice = (
        (1, '未删除'),
        (2, '删除'),
    )
    display = models.IntegerField(verbose_name='是否显示', choices=display_choice, default=1)

    def __str__(self):
        return self.chinese_name


class Plan(models.Model):
    """
    在港船舶计划表
    """
    ship = models.ForeignKey(verbose_name='船名', to='Ship', on_delete=models.CASCADE)
    title = models.ForeignKey(verbose_name='船舶计划', to='PlanStatus', on_delete=models.CASCADE)
    move_time = models.DateTimeField(verbose_name='计划时间')
    location = models.ForeignKey(verbose_name='船厂/码头', to='Location', on_delete=models.CASCADE, null=True, )
    next_port = models.CharField(verbose_name='下一港口/泊位', max_length=16, null=True, blank=True)
    boat_status = models.ForeignKey(verbose_name='船舶申请状态', to='BoatStatus', on_delete=models.CASCADE, null=True,
                                    blank=True)
    agent = models.ForeignKey(verbose_name='代理', to='UserInfo', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='agent')
    check_user = models.ForeignKey(verbose_name='审核人', to='UserInfo', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='check_user')
    display_choice = (
        (1, '未删除'),
        (2, '删除'),
    )
    display = models.IntegerField(verbose_name='是否显示', choices=display_choice, default=1)
    order = models.ForeignKey(verbose_name='工单', to='Order', null=True, blank=True, on_delete=models.CASCADE)
    note = models.TextField(verbose_name='备注', blank=True, null=True)
    move_number = models.IntegerField(verbose_name='移泊次数', blank=True, null=True)
    last_location = models.ForeignKey(verbose_name='上一次位置',to='Location', on_delete=models.CASCADE, null=True,blank=True,related_name='locations')
    last_port = models.CharField(verbose_name='上一次的位置',null=True,blank=True,max_length=25)
    apply = models.DateTimeField(verbose_name='申报时间',blank=True,auto_now_add=True,null=True)
    report = models.BooleanField(default=0,choices=((0,'否'),(1,'是')),verbose_name='是否为补报')
    def __str__(self):
        return "%s  %s" % (self.move_time, self.location)


class BoatStatus(models.Model):
    """
    船舶状态
    """
    title = models.CharField(verbose_name='船舶状态', max_length=32)

    def __str__(self):
        return self.title


class PlanStatus(models.Model):
    """
    存放船情计划名称：
                    移泊  入境   出境   入港   出港
    """
    title = models.CharField(verbose_name='计划', max_length=32)
    order = models.IntegerField(verbose_name='排序',blank=True,null=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    """
    工单列表
    """
    title = models.CharField(verbose_name='工单名称', max_length=16)

    def __str__(self):
        return self.title
