from typing import Callable, Optional, Tuple, Union
import sumolib
import traci
import networkx

class vehicle():
    def __init__(self, vehicle_id, tracistart):
        self.sumo = tracistart
        self.vehicle_id = vehicle_id
        self._get_vehicle_info()

    def _get_vehicle_info(self):
        self.route = self.sumo.vehicle.getRoute(self.vehicle_id)
        self.curroute = self.sumo.vehicle.getRouteID(self.vehicle_id)
        self.position  = self.sumo.vehicle.getPosition(self.vehicle_id)
        self.type = self.sumo.vehicle.getTypeID(self.vehicle_id)
        info = {
            "vehicle_id": self.vehicle_id,
            "route": self.route,
            "type": self.type,
            "curroute": self.curroute,
            "position":self.position
        }
        print(info)
        return info


    def _pause_vehicle(self):
        self.sumo.vehicle.setSpeed(self.vehicle_id, 0)


    def _is_endroute(self) -> bool:
        # todo: 是否完成预先规划的路由
        pass

    def _route_vehicle(self, route: Union[int, list]):
        # todo: 重新规划路由
        pass

    def _get_vehicles_around(self, thre: float) -> list:
        # todo: 获取周围车辆
        pass


class truck(vehicle):
    def __init__(self, vehicle_id, tracistart):
        super(vehicle, self).__init__(vehicle_id, tracistart)


class crane(vehicle):
    def __init__(self, vehicle_id, tracistart):
        super(vehicle, self).__init__(vehicle_id, tracistart)


    def _load_task(self):
        # todo: 载入装卸任务
        pass

    def _apply_one_task(self, worktime):
        # todo: 执行一次装/卸
        pass


class bridge(vehicle):
    def __init__(self, vehicle_id, tracistart):
        super(vehicle, self).__init__(vehicle_id, tracistart)

