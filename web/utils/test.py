from web import models

# 移泊、入境、入港
status_list = [3, 4, 5]
# 出境、出港
status_list_two = [1, 2]

obj_list = models.Plan.objects.filter(boat_status=7)
def test():
    if obj_list:
        for plan_obj in obj_list:
            ship_id = plan_obj.ship
            # print(ship_id)
            # into_obj = models.Plan.objects.filter(title_id__in=[1, 2, 4, 5], boat_status_id=7).first()
            into_obj = models.Plan.objects.filter(title_id__in=[4, 5], boat_status_id=7,
                                                  ship_id=ship_id.pk).first()
            if into_obj and plan_obj != into_obj:  # 如果有入港入境船情，必须先完成入港入境船情，否则无法完成
                continue
            if plan_obj:
                location = plan_obj.location
                # 这个是判断今天是否有出港、出境计划
                is_complete = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[1, 2]).first()
                if is_complete:
                    # is_over是出港、出境的船舶对象
                    is_over = models.Plan.objects.filter(ship_id=ship_id, title_id__in=[1, 2], boat_status=7).first()
                    if plan_obj == is_over:
                        plan_obj.ship.location = plan_obj.last_location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                    elif location and is_over:
                        plan_obj.ship.location = location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                    else:
                        plan_obj.ship.location = location
                        now_port = plan_obj.next_port
                        plan_obj.ship.port_in = now_port
                        title_id = plan_obj.title_id
                        if title_id in status_list:
                            plan_obj.ship.status = 1
                        elif title_id in status_list_two:
                            plan_obj.ship.status = 2
                else:
                    if location:
                        title_id = plan_obj.title_id
                        if title_id == 6:
                            pass
                        else:
                            plan_obj.ship.location = location
                            now_port = plan_obj.next_port
                            plan_obj.ship.port_in = now_port
                            title_id = plan_obj.title_id
                            if title_id in status_list:
                                plan_obj.ship.status = 1
                            elif title_id in status_list_two:
                                plan_obj.ship.status = 2
                plan_obj.boat_status_id = 6
                plan_obj.save()
                # 将船舶表的状态也改变过来
                plan_obj.ship.boat_status_id = 6
                plan_obj.ship.save()
    else:
        print('ok')
