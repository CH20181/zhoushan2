from web import models


obj_list = models.Plan.objects.filter(boat_status__in=[1, 2, 3, 4, 5, 9])

def test():
    if obj_list:
        for plan_obj in obj_list:
            plan_obj.boat_status_id = 7
            plan_obj.check_user_id = 16
            plan_obj.save()
            plan_obj.ship.boat_status_id = 7
            plan_obj.ship.save()
    else:
        print('已经审核所有工单')