import datetime
import locale

from django.http import HttpResponse
from itertools import chain
from web import models
import xlwt


class Create():
    def __init__(self, file_name, department, user_id, ):
        self.number = 2
        self.file_name = file_name
        self.department = department
        self.user_id = user_id
        self.new_sheet = self.create_xls()
        self.main()
        if department == '指挥中心':
            self.new_wb.save(file_name + '\\舟山站%s船情.xls' % self.get_time)
        else:
            self.new_wb.save(file_name + '\\%s%s船情.xls' % (department, self.get_time))

    @property
    def get_time(self):
        e = datetime.datetime.now().year
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day
        c = '%s年%s月%s日' % (e, a, b)
        return c

    def create_xls(self):
        self.new_wb = xlwt.Workbook()
        new_sheet = self.new_wb.add_sheet(self.department)
        self.set_init2(new_sheet)
        self.set_init3(new_sheet)
        self.set_init1(new_sheet)
        b = '%s%s船情' % (self.department, self.get_time)
        if self.department == '指挥中心':
            b = '舟山站%s船情' % (self.get_time)
        new_sheet.write_merge(0, 0, 0, 18, b, self.style2)
        new_sheet.write(1, 0, "序号", self.style1)
        new_sheet.write(1, 1, "出入类型", self.style1)
        new_sheet.write(1, 2, "入出口岸", self.style1)
        new_sheet.write(1, 3, "境外标识", self.style1)
        new_sheet.write(1, 4, "境内标识", self.style1)
        new_sheet.write(1, 5, "IMO", self.style1)
        new_sheet.write(1, 6, "MMSI", self.style1)
        new_sheet.write(1, 7, "国籍", self.style1)
        new_sheet.write(1, 8, "船员分布", self.style1)
        new_sheet.write(1, 9, "货物情况", self.style1)
        new_sheet.write(1, 10, "枪支弹药", self.style1)
        new_sheet.write(1, 11, "预计时间", self.style1)
        new_sheet.write(1, 12, "在港泊位", self.style1)
        new_sheet.write(1, 13, "来港目的", self.style1)
        new_sheet.write(1, 14, "代理公司", self.style1)
        new_sheet.write(1, 15, "风险等级", self.style1)
        new_sheet.write(1, 16, "执勤部门", self.style1)
        new_sheet.write(1, 17, "工单任务", self.style1)
        new_sheet.write(1, 18, "备注", self.style1)
        return new_sheet

    def set_init1(self, a):
        """
        设置项目标题的样式
        :param a:
        :return:
        """
        font = xlwt.Font()
        font.height = 20 * 10
        first_row = a.row(1)
        borders = xlwt.Borders()  # Create Borders
        al = xlwt.Alignment()
        al.horz = 0x02
        al.vert = 0x01
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        self.style1 = xlwt.XFStyle()  # Create Style
        self.style1.alignment = al
        self.style1.font = font
        self.style1.borders = borders  # Add Borders to Style
        return self.style1

    def set_init2(self, a):
        for i in range(16):
            sheet_width = a.col(i)
            sheet_width.width = 256 * 10
        sheet_0 = a.col(0)
        sheet_1 = a.col(1)
        sheet_2 = a.col(2)
        sheet_3 = a.col(3)
        sheet_4 = a.col(4)
        sheet_5 = a.col(5)
        sheet_6 = a.col(6)
        sheet_7 = a.col(7)
        sheet_8 = a.col(8)
        sheet_9 = a.col(9)
        sheet_10 = a.col(10)
        sheet_11 = a.col(11)
        sheet_12 = a.col(12)
        sheet_13 = a.col(13)
        sheet_14 = a.col(14)
        sheet_15 = a.col(15)
        sheet_16 = a.col(16)
        sheet_17 = a.col(17)
        sheet_18 = a.col(18)
        sheet_0.width = 256 * 5
        sheet_1.width = 256 * 8
        sheet_2.width = 256 * 10
        sheet_3.width = 256 * 8
        sheet_4.width = 256 * 8
        sheet_5.width = 256 * 11
        sheet_6.width = 256 * 11
        sheet_7.width = 256 * 11
        sheet_8.width = 256 * 22
        sheet_9.width = 256 * 12
        sheet_10.width = 256 * 8
        sheet_11.width = 256 * 13
        sheet_12.width = 256 * 14
        sheet_13.width = 256 * 9
        sheet_14.width = 256 * 10
        sheet_15.width = 256 * 10
        sheet_16.width = 256 * 9
        sheet_17.width = 256 * 9
        sheet_18.width = 256 * 22
        font = xlwt.Font()
        font.height = 20 * 10
        tall_style = xlwt.easyxf('font:height 720;')
        first_row = a.row(0)
        first_row.set_style(tall_style)
        borders = xlwt.Borders()  # Create Borders
        al = xlwt.Alignment()
        al.horz = 0x02
        al.vert = 0x01
        al.wrap = 1
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        self.style = xlwt.XFStyle()  # Create Style
        self.style.alignment = al
        self.style.font = font
        self.style.borders = borders  # Add Borders to Style

    def set_init3(self, a):
        font = xlwt.Font()
        font.height = 20 * 24
        font.bold = True
        first_row = a.row(0)
        borders = xlwt.Borders()  # Create Borders
        al = xlwt.Alignment()
        al.horz = 0x02
        al.vert = 0x01
        borders.left = xlwt.Borders.THIN
        borders.right = xlwt.Borders.THIN
        borders.top = xlwt.Borders.THIN
        borders.bottom = xlwt.Borders.THIN
        borders.left_colour = 0x40
        borders.right_colour = 0x40
        borders.top_colour = 0x40
        borders.bottom_colour = 0x40
        self.style2 = xlwt.XFStyle()  # Create Style
        self.style2.alignment = al
        self.style2.font = font
        self.style2.borders = borders  # Add Borders to Style
        return self.style2

    @property
    def get_today_time(self):
        c = datetime.datetime.now().year
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day
        c = '%s-%s-%s' % (c, a, b)
        return c

    def main(self):
        if self.department == '指挥中心':
            plan_obj = models.Plan.objects.filter(boat_status=7, move_time__gt=self.get_today_time).order_by(
                'title__order')
        else:
            plan_obj = models.Plan.objects.filter(boat_status=7, location__department__title=self.department,
                                                  move_time__year=datetime.datetime.now().year,
                                                  move_time__month=datetime.datetime.now().month,
                                                  move_time__day=datetime.datetime.now().day).order_by(
                'title__order')
            # obj = models.Plan.objects.filter(boat_status=7, ship__location__department__title=self.department, title=3,
            #                                  move_time__year=datetime.datetime.now().year,
            #                                  move_time__month=datetime.datetime.now().month,
            #                                  move_time__day=datetime.datetime.now().day).order_by(
            #     'title__order')
            # 将上一个泊位的情况也统计出来
            obj2 = models.Plan.objects.filter(boat_status=7, last_location__department__title=self.department,
                                              move_time__year=datetime.datetime.now().year,
                                              move_time__month=datetime.datetime.now().month,
                                              move_time__day=datetime.datetime.now().day).order_by(
                'title__order')
            # 将两个QuerySet对象合并为一个
            plan_obj = chain(plan_obj, obj2)

        if not plan_obj:
            return HttpResponse('别急小伙子，船情还没出来！！！！！')
        for i in plan_obj:
            ship_obj = i.ship
            self.write(i, ship_obj)

    def into_or_out(self, plan_obj, ship_obj):
        """
        判断是移泊、入、出
        :param plan_obj:
        :param ship_obj:
        :return:
        """
        type_name = plan_obj.title.id
        if type_name == 1 or type_name == 2:
            return plan_obj.next_port
        elif type_name == 3:
            return ''
        elif type_name == 4 or type_name == 5:
            return ship_obj.last_port

    def which_department(self, plan_obj, ship_obj):
        type_name = plan_obj.title.id
        # 移泊
        if type_name == 3:
            try:
                return plan_obj.last_location.department.title + '\n' + plan_obj.location.department.title
            except:
                return ''
            # 出港、出境
        elif type_name == 1 or type_name == 2:
            if ship_obj.location_id == 83:
                return plan_obj.location.department.title
            try:
                return ship_obj.location.department.title
            except:
                return ''
        # 入港、入境
        else:
            return plan_obj.location.department.title

    def where_port(self, plan_obj, ship_obj):
        type_name = plan_obj.title.id
        # 出港、出境
        if type_name == 1 or type_name == 2:
            ship_id = plan_obj.ship_id
            # 此处判断是否为当天入出船舶
            is_into = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[4, 5]).first()
            if is_into:
                return '%s----->%s' % (is_into.location.title + is_into.next_port, plan_obj.next_port)
            try:
                return ship_obj.location.title + ship_obj.port_in
            except:
                return '暂无'
            # 移泊
        elif type_name == 3:
            plan_obj_two = models.Plan.objects.filter(ship_id=plan_obj.ship_id, title_id=3)
            plan_obj_number = plan_obj.move_number
            try:
                if plan_obj_number is not None:
                    return '%s--->%s' % (
                    plan_obj_two[plan_obj_number].location.title + plan_obj_two[plan_obj_number].next_port,
                    plan_obj.location.title + plan_obj.next_port)
                return '%s--->%s' % (plan_obj.last_location.title, plan_obj.location.title + plan_obj.next_port)
                # return ship_obj.location.title + '----->' + plan_obj.location.title + plan_obj.next_port
            except:
                return '暂无'
            # 入港、入境
        else:
            try:
                return plan_obj.location.title + plan_obj.next_port
            except:
                return plan_obj.location.title

    def write(self, plan_obj, ship_obj):
        self.new_sheet.write(self.number, 0, str(self.number - 1), self.style)
        self.new_sheet.write(self.number, 1, plan_obj.title.title, self.style)
        self.new_sheet.write(self.number, 2, self.into_or_out(plan_obj, ship_obj), self.style)
        self.new_sheet.write(self.number, 3, ship_obj.english_name, self.style)
        self.new_sheet.write(self.number, 4, ship_obj.chinese_name, self.style)
        self.new_sheet.write(self.number, 5, ship_obj.IMO, self.style)
        self.new_sheet.write(self.number, 6, ship_obj.MMSI, self.style)
        self.new_sheet.write(self.number, 7, ship_obj.nationality, self.style)
        self.new_sheet.write(self.number, 8, ship_obj.crew_detail, self.style)
        self.new_sheet.write(self.number, 9, ship_obj.goods, self.style)
        self.new_sheet.write(self.number, 10, ship_obj.get_guns_display(), self.style)
        # locale.setlocale(locale.LC_CTYPE, 'chinese')
        self.new_sheet.write(self.number, 11, plan_obj.move_time.strftime("%m-%d %H:%M"), self.style)
        try:
            self.new_sheet.write(self.number, 12, self.where_port(plan_obj, ship_obj), self.style)
        except:
            self.new_sheet.write(self.number, 12, '', self.style)

        self.new_sheet.write(self.number, 13, ship_obj.purpose, self.style)
        self.new_sheet.write(self.number, 14,
                             ship_obj.user.company.title + ship_obj.user.nickname + ship_obj.user.phone, self.style)
        # 此处应该判断一下，当前是入境、入港
        self.new_sheet.write(self.number, 15, '', self.style)
        self.new_sheet.write(self.number, 16, self.which_department(plan_obj, ship_obj), self.style)
        self.new_sheet.write(self.number, 17, '', self.style)
        self.new_sheet.write(self.number, 18, plan_obj.note, self.style)
        self.number += 1
