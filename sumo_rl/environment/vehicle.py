from typing import Callable, Optional, Tuple, Union
import sumolib
import traci
import networkx

class Vehicle():
    def __init__(self, tracistart, vehicle_id, route):
        self.sumo = tracistart
        self.vehicle_id = vehicle_id
        self.sumo.vehicle.add(vehicle_id, route)

    def _get_info(self):
        try:
            self.route = self.sumo.vehicle.getRoute(self.vehicle_id)
            self.curroute = self.sumo.vehicle.getRouteID(self.vehicle_id)
            self.position = self.sumo.vehicle.getPosition(self.vehicle_id)
            self.type = self.sumo.vehicle.getTypeID(self.vehicle_id)
            info = {
                "vehicle_id": self.vehicle_id,
                "route": self.route,
                "type": self.type,
                "curroute": self.curroute,
                "position": self.position
            }
            return info
        except:
            return None

    def _pause_vehicle(self):
        self.sumo.vehicle.setSpeed(self.vehicle_id, 0)


    def _is_endroute(self) -> bool:
        # todo: 是否完成预先规划的路由(任务)
        pass

    def _route_vehicle(self, route: Union[str, list]):
        # todo: 规划路由
        self.sumo.vehicle.setRoute(self.vehicle_id, route)

    def _get_vehicles_around(self, thre: float) -> list:
        # todo: 获取周围车辆
        pass


class Truck(Vehicle):
    def __init__(self, tracistart, vehicle_id, route):
        super(Truck, self).__init__(tracistart, vehicle_id, route)


class Crane(Vehicle):
    def __init__(self, tracistart, vehicle_id, route):
        super(Crane, self).__init__(tracistart, vehicle_id, route)


    def _load_task(self):
        # todo: 载入装卸任务
        pass

    def _apply_one_task(self, worktime):
        # todo: 执行一次装/卸
        pass


class Bridge(Vehicle):
    def __init__(self, tracistart, vehicle_id, route):
        super(Bridge, self).__init__(tracistart, vehicle_id, route)

