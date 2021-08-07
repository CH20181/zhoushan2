import datetime

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
            self.new_wb.save(file_name + '\\舟山站%s船情.xlsx'%(self.get_time))
        else:
            self.new_wb.save(file_name + '\\舟山站%s船情.xlsx'%(self.get_time))

    @property
    def get_time(self):
        a = datetime.datetime.now().month
        b = datetime.datetime.now().day
        c = '%s月%s日' % (a, b)
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
        new_sheet.write_merge(0, 0, 0, 15, b, self.style2)
        new_sheet.write(1, 0, "序号", self.style1)
        new_sheet.write(1, 1, "船名", self.style1)
        new_sheet.write(1, 2, "国籍", self.style1)
        new_sheet.write(1, 3, "船员国籍人数", self.style1)
        new_sheet.write(1, 4, "货物", self.style1)
        new_sheet.write(1, 5, "在港泊位", self.style1)
        new_sheet.write(1, 6, "入", self.style1)
        new_sheet.write(1, 7, "上一港", self.style1)
        new_sheet.write(1, 8, "出", self.style1)
        new_sheet.write(1, 9, "下一港", self.style1)
        new_sheet.write(1, 10, "来港目的", self.style1)
        new_sheet.write(1, 11, "代理公司", self.style1)
        new_sheet.write(1, 12, "风险等级", self.style1)
        new_sheet.write(1, 13, "执勤部门", self.style1)
        new_sheet.write(1, 14, "工单任务", self.style1)
        new_sheet.write(1, 15, "备注", self.style1)
        return new_sheet

    def set_init1(self, a):
        """
        设置项目标题的样式
        :param a:
        :return:
        """
        font = xlwt.Font()
        font.height = 20 * 15
        font.bold = True
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
        sheet_port = a.col(5)
        sheet_port24 = a.col(1)
        sheet_port4 = a.col(2)
        sheet_port1 = a.col(15)
        sheet_port2 = a.col(0)
        sheet_port3 = a.col(3)
        sheet_port11 = a.col(11)
        sheet_port14 = a.col(4)
        sheet_port16 = a.col(6)
        sheet_port17 = a.col(7)
        sheet_port18 = a.col(8)
        sheet_port19 = a.col(9)
        sheet_port20 = a.col(10)
        sheet_port21 = a.col(12)
        sheet_port22 = a.col(13)
        sheet_port23 = a.col(14)
        sheet_port.width = 256 * 25
        sheet_port1.width = 256 * 30
        sheet_port4.width = 256 * 15
        sheet_port2.width = 256 * 8
        sheet_port3.width = 256 * 20
        sheet_port11.width = 256 * 20
        sheet_port14.width = 256 * 20
        sheet_port16.width = 256 * 15
        sheet_port17.width = 256 * 20
        sheet_port18.width = 256 * 15
        sheet_port19.width = 256 * 20
        sheet_port20.width = 256 * 20
        sheet_port21.width = 256 * 20
        sheet_port22.width = 256 * 20
        sheet_port23.width = 256 * 20
        sheet_port24.width = 256 * 15
        font = xlwt.Font()
        font.height = 20 * 15
        tall_style = xlwt.easyxf('font:height 720;')
        first_row = a.row(0)
        first_row.set_style(tall_style)
        borders = xlwt.Borders()  # Create Borders
        al = xlwt.Alignment()
        al.horz = 0x02
        al.vert = 0x01
        al.wrap = 1
        borders.left = xlwt.Borders.THIN
        # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, THIN_DASH_DOT_DOTTED, MEDIUM_DASH_DOT_DOTTED, SLANTED_MEDIUM_DASH_DOTTED, or 0x00 through 0x0D.
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
        font.height = 20 * 26
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
        c = '%s-%s-%s' % (c,a, b)
        return c
    def main(self):
        if self.department == '指挥中心':
            plan_obj = models.Plan.objects.filter(boat_status=7,move_time__gt=self.get_today_time).order_by('-title')
        else:
            plan_obj = models.Plan.objects.filter(boat_status=7, location__department__title=self.department,move_time__year=datetime.datetime.now().year,move_time__month=datetime.datetime.now().month,move_time__day=datetime.datetime.now().day).order_by(
                'title')
            obj = models.Plan.objects.filter(boat_status=7,ship__location__department__title=self.department,title=3,move_time__year=datetime.datetime.now().year,move_time__month=datetime.datetime.now().month,move_time__day=datetime.datetime.now().day)
            # 将两个QuerySet对象合并为一个
            plan_obj = chain(plan_obj,obj)

        if not plan_obj:
            return HttpResponse('别急小伙子，船情还没出来！！！！！')
        for i in plan_obj:
            ship_obj = i.ship
            self.write(i, ship_obj)

    def which_plan(self, plan_obj, ship_obj):
        name = plan_obj.title.title
        plan_str = ''
        if name == '入境' or name == '入港':
            # print(ship_obj.location.title, plan_obj.location.title, plan_obj.next_port)
            plan_str += ship_obj.last_port + '------>' + plan_obj.location.title + plan_obj.next_port
        elif name == '出境' or name == '出港':
            plan_str += ship_obj.location.title + '------>' + plan_obj.next_port
        else:
            plan_str += ship_obj.location.title + '------>' + plan_obj.location.title + plan_obj.next_port
        return plan_str

    def into_or_out(self, plan_obj, ship_obj):
        """
        判断是移泊、入、出
        :param plan_obj:
        :param ship_obj:
        :return:
        """
        type_name = plan_obj.title.id
        if type_name == 1:
            self.new_sheet.write(self.number, 6, '', self.style)
            self.new_sheet.write(self.number, 7, '', self.style)
            self.new_sheet.write(self.number, 8, '出境' + plan_obj.move_time.strftime('%m-%d %H:%M'), self.style)
            self.new_sheet.write(self.number, 9, plan_obj.next_port, self.style)
        elif type_name == 2:
            self.new_sheet.write(self.number, 6, '', self.style)
            self.new_sheet.write(self.number, 7, '', self.style)
            self.new_sheet.write(self.number, 8, '出港' + plan_obj.move_time.strftime('%m-%d %H:%M'), self.style)
            self.new_sheet.write(self.number, 9, plan_obj.next_port, self.style)
        elif type_name == 3:
            self.new_sheet.write(self.number, 6, '移泊' + plan_obj.move_time.strftime('%m-%d %H:%M'), self.style)
            self.new_sheet.write(self.number, 7, '', self.style)
            self.new_sheet.write(self.number, 8, '', self.style)
            self.new_sheet.write(self.number, 9, '', self.style)
        elif type_name == 4:
            self.new_sheet.write(self.number, 6, '入港' + plan_obj.move_time.strftime('%m-%d %H:%M'), self.style)
            self.new_sheet.write(self.number, 7, ship_obj.last_port, self.style)
            self.new_sheet.write(self.number, 8, '', self.style)
            self.new_sheet.write(self.number, 9, '', self.style)
        elif type_name == 5:
            self.new_sheet.write(self.number, 6, '入境' + plan_obj.move_time.strftime('%m-%d %H:%M'), self.style)
            self.new_sheet.write(self.number, 7, ship_obj.last_port, self.style)
            self.new_sheet.write(self.number, 8, '', self.style)
            self.new_sheet.write(self.number, 9, '', self.style)

    def write(self, plan_obj, ship_obj):
        self.new_sheet.write(self.number, 0, str(self.number - 1), self.style)
        self.new_sheet.write(self.number, 1, str(ship_obj.chinese_name + "\n" + ship_obj.english_name), self.style)
        self.new_sheet.write(self.number, 2, ship_obj.nationality, self.style)
        self.new_sheet.write(self.number, 3, ship_obj.crew_detail, self.style)
        self.new_sheet.write(self.number, 4, ship_obj.goods, self.style)
        # 此处应该判断一下，当前是入境、入港
        self.new_sheet.write(self.number, 5, self.which_plan(plan_obj, ship_obj), self.style)
        self.into_or_out(plan_obj, ship_obj)
        self.new_sheet.write(self.number, 10, ship_obj.purpose, self.style)
        self.new_sheet.write(self.number, 11,
                             ship_obj.user.company.title + "\n" + ship_obj.user.nickname + ship_obj.user.company.phone,
                             self.style)
        self.new_sheet.write(self.number, 12, '', self.style)
        self.new_sheet.write(self.number, 13, plan_obj.location.department.title, self.style)
        self.new_sheet.write(self.number, 14, '', self.style)
        self.new_sheet.write(self.number, 15, 'MMSI:' + ship_obj.MMSI + ship_obj.note, self.style)
        self.number += 1
