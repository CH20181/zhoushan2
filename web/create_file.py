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
        self.new_wb.save(file_name + '\\%s在港船舶动态.xlsx' % department)

    def create_xls(self):
        self.new_wb = xlwt.Workbook()
        new_sheet = self.new_wb.add_sheet(self.department)
        self.set_init2(new_sheet)
        self.set_init3(new_sheet)
        self.set_init1(new_sheet)
        b = '%s在港船舶动态' % self.department
        new_sheet.write_merge(0, 0, 0, 14, b, self.style2)
        # new_sheet.write(0,0,b)
        new_sheet.write(1, 0, "序号", self.style1)
        new_sheet.write(1, 1, "船名", self.style1)
        new_sheet.write(1, 2, "国籍", self.style1)
        new_sheet.write(1, 3, "船员国籍人数", self.style1)
        new_sheet.write(1, 4, "货物", self.style1)
        new_sheet.write(1, 5, "在港泊位", self.style1)
        new_sheet.write(1, 6, "入境/入港", self.style1)
        new_sheet.write(1, 7, "上一港", self.style1)
        new_sheet.write(1, 8, "船员总数", self.style1)
        new_sheet.write(1, 9, "MMSI", self.style1)
        new_sheet.write(1, 10, "来港目的", self.style1)
        new_sheet.write(1, 11, "代理公司", self.style1)
        new_sheet.write(1, 12, "风险等级", self.style1)
        new_sheet.write(1, 13, "入口岸时间", self.style1)
        new_sheet.write(1, 14, "近期靠泊码头", self.style1)
        return new_sheet

    def set_init1(self, a):
        """
        设置项目标题的样式
        :param a:
        :return:
        """
        font = xlwt.Font()
        font.height = 20 * 10
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
        for i in range(15):
            sheet_width = a.col(i)
            sheet_width.width = 256 * 10
        sheet_port0 = a.col(1)  # 船名
        sheet_port11 = a.col(3)  # 船员国籍详情
        sheet_port = a.col(5)  # 在港泊位
        sheet_port1 = a.col(14)  # 近期靠港码头
        sheet_port2 = a.col(0)  # 序号
        sheet_port3 = a.col(7)  # 上一港
        sheet_port4 = a.col(13)  # 入口岸时间
        sheet_port8 = a.col(11)  # 代理公司
        sheet_port9 = a.col(9)  # MMSI
        sheet_port.width = 256 * 20
        sheet_port11.width = 256 * 30
        sheet_port0.width = 256 * 15
        sheet_port1.width = 256 * 50
        sheet_port2.width = 256 * 5
        sheet_port3.width = 256 * 15
        sheet_port4.width = 256 * 20
        sheet_port8.width = 256 * 20
        sheet_port9.width = 256 * 15
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
        self.style.borders = borders  # Add Borders to Style
        return self.style

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

    def main(self):
        if self.department == '指挥中心':
            ship_obj = models.Ship.objects.filter(status=1).order_by('location')
        else:
            ship_obj = models.Ship.objects.filter(status=1, location__department__title=self.department).order_by('location')
        for i in ship_obj:
            plan_obj = models.Ship.objects.get(id=i.id).plan_set.all().order_by('location')
            self.write(i, plan_obj)

    def write(self, ship_obj, plan_obj):
        self.new_sheet.write(self.number, 0, str(self.number - 1), self.style)
        self.new_sheet.write(self.number, 1, str(ship_obj.chinese_name + "\n" + ship_obj.english_name), self.style)
        self.new_sheet.write(self.number, 2, ship_obj.nationality, self.style)
        self.new_sheet.write(self.number, 3, ship_obj.crew_detail, self.style)
        self.new_sheet.write(self.number, 4, ship_obj.goods, self.style)
        self.new_sheet.write(self.number, 5, ship_obj.location.title + ship_obj.port_in, self.style)
        self.new_sheet.write(self.number, 6, plan_obj.first().title.title, self.style)
        self.new_sheet.write(self.number, 7, ship_obj.last_port, self.style)
        self.new_sheet.write(self.number, 8, ship_obj.crew_total, self.style)
        self.new_sheet.write(self.number, 9, ship_obj.MMSI, self.style)
        self.new_sheet.write(self.number, 10, ship_obj.purpose, self.style)
        self.new_sheet.write(self.number, 11,
                             ship_obj.user.company.title + "\n" + ship_obj.user.name + ship_obj.user.company.phone,
                             self.style)
        self.new_sheet.write(self.number, 12, '', self.style)
        self.new_sheet.write(self.number, 13, plan_obj.first().move_time.strftime('%Y-%m-%d %H:%M'), self.style)

        self.new_sheet.write(self.number, 14, self.all_plan(plan_obj), self.style)
        # self.all_plan(plan_obj)
        self.number += 1

    def all_plan(self, plan_obj):
        all_plan_str = ''
        for i in plan_obj:
            if i.title.id == 4 or i.title.id == 5:
                all_plan_str += i.move_time.strftime(
                    '%Y-%m-%d %H:%M') + i.ship.last_port + '----->' + i.ship.location.title + i.next_port
            elif i.title.id == 3:
                all_plan_str += '\n' + i.move_time.strftime(
                    '%Y-%m-%d %H:%M') + i.ship.location.title + '----->' + i.location.title + i.next_port
        return all_plan_str
