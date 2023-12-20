import logging
import random
from typing import Callable, Optional, Tuple, Union
import sumolib
import traci
import networkx

class Vehicle():
    def __init__(self, tracistart, Scheduler, vehicle_id, task: Union[str, list, None]):
        self.sumo = tracistart
        self.Scheduler = Scheduler
        self.vehicle_id = vehicle_id

        ## ======== 任务状态
        self.start_task = False
        self.finish_task = False
        self.pause_ontask = False
        self.destination: dict = {}  # todo: 用其他数据结构表示终点（岸桥/场吊位置）

        ## ======== 创建车辆
        self.sumo.vehicle.add(vehicle_id, "route_default")
        self.speed = self.sumo.vehicle.getSpeed(self.vehicle_id)
        self._apply_task(task)




    def _get_info(self):
        try:
            self.type = self.sumo.vehicle.getTypeID(self.vehicle_id)
            self.route = self.sumo.vehicle.getRoute(self.vehicle_id)
            self.cur_edge = self.sumo.vehicle.getRoadID(self.vehicle_id)
            self.cur_Lane = self.sumo.vehicle.getLaneID(self.vehicle_id)
            self.position = self.sumo.vehicle.getPosition(self.vehicle_id)
            # todo: 添加任务信息
            info = {
                "vehicle_id": self.vehicle_id,
                "type": self.type,
                "route": self.route,
                "cur_edge":self.cur_edge,
                "cur_Lane": self.cur_Lane,
                "position": self.position,
            }
            return info
        except:
            return None

    def _route_vehicle(self, route: Union[str, list]):
        """
        规划路由
        :param route:
         str 到达edge_id
         list 起始edge_id
        :return:
        """
        try:
            if isinstance(route, str):
                start_edge, end_edge = self.sumo.vehicle.getRoadID(self.vehicle_id), route
                start_edge = start_edge if start_edge else random.choice(self.sumo.route.getEdges("route_default"))
            else:
                start_edge, end_edge = route[0], route[1]
            if start_edge == end_edge: # 无效任务, 单载集卡不能执行多次装/卸
                logging.warning(f"ignore invalid task of {self.vehicle_id} ")
                return None
            Route = self.Scheduler.set_route(self.vehicle_id,  start_edge, end_edge)
            self.sumo.vehicle.setRoute(self.vehicle_id, Route)
            logging.info(f"""set {self.vehicle_id} from edge {start_edge} to edge {end_edge} along {Route}""")
            return end_edge
        except Exception as ex:
            logging.warning(f"Fail to set {self.vehicle_id} to {start_edge, end_edge}: {ex}")
            return None

    def _pause_vehicle(self):
        """
        暂停车辆
        :return:
        """
        self.sumo.vehicle.setSpeed(self.vehicle_id, 0) # todo: 车辆将会开始减速, 但是不能立马停下来
        self.pause_ontask = True
        logging.info(f"""{self.vehicle_id} pause at destination {self.destination["id"]} edge {self.sumo.vehicle.getRoadID(self.vehicle_id)} on schedule """)

    def _check_task_start(self, threshold = 10) -> bool:
        """
        判断是否到达路由终点
        todo: 如果设置的[delta_time较大/速度较快]会捕捉不到到达终点附近
        :param threshold:
        :return:
        """
        self.cur_edge = self.sumo.vehicle.getRoadID(self.vehicle_id)
        if self.finish_task == False and self.cur_edge == self.destination["edge"]:
            self.position = self.sumo.vehicle.getPosition(self.vehicle_id)
            distance = self.sumo.simulation.getDistance2D(self.position[0], self.position[1],
                                                          self.destination["position"][0],self.destination["position"][1])
            if distance < threshold:
                self.start_task = True # 车完全停下后distance可能超过了threshold范围, 但是依然 self.start_task = True
                self._pause_vehicle()
            # print(f"distance of {self.vehicle_id} = {distance}, "
            #           f"finish_task = {self.finish_task}, "
            #           f"pause_ontask = {self.pause_ontask} "
            #           f"start_task = {self.start_task}")
            return self.start_task

    def _check_task_finish(self, pause_steps = 10):
        """
        判断装卸任务是否完成
        :param pause_steps:
        :return:
        """
        WaitingTime = self.sumo.vehicle.getWaitingTime(self.vehicle_id) # todo: 车辆完全停止才开始计算, 不包括减速的时间
        if self.pause_ontask and self.start_task and  WaitingTime >= pause_steps:
            self.finish_task = True
            self.pause_ontask = False
            self.start_task = False
            self.Scheduler.tasks_ongoing.remove(self.destination["task"])
            logging.info(f"""{self.vehicle_id} finish task in {WaitingTime} steps at destination {self.destination["id"]} edge {self.sumo.vehicle.getRoadID(self.vehicle_id)}""")
        # if  WaitingTime:
        #     print(f"WaitingTime of {self.vehicle_id} = {WaitingTime}, "
        #       f"finish_task = {self.finish_task}, "
        #       f"pause_ontask = { self.pause_ontask} "
        #       f"start_task = {self.start_task}")
        return self.finish_task

    def _apply_task(self, task: Union[str, list, None]):
        """
        执行一次运输任务
        :param des:
        :return:
        """
        try:
            task = task if task else self.Scheduler.dispatch_task(self.vehicle_id)
            route = task  # todo: 从task中解析route（起）始点
            end_edge = self._route_vehicle(route)
            if end_edge:
                self.sumo.vehicle.setSpeed(self.vehicle_id, self.speed)
                end_lanes = [lane_id for lane_id in self.sumo.lane.getIDList() if
                             self.sumo.lane.getEdgeID(lane_id) == end_edge]
                lane = self.sumo.lane.getShape(end_lanes[0])
                self.destination = {"id": 0,
                                    "task": task,
                                    "edge": end_edge,
                                    "position": ((lane[0][0] + lane[-1][0]) / 2, (lane[0][1] + lane[-1][1]) / 2)
                                    # todo: 暂且把lane中点设置为路由终点
                                    }
                self.Scheduler.tasks_ongoing.append(task)
                self.finish_task = False
            else:
                logging.warning(f"Fail to route {self.vehicle_id} for task {task}")
        except Exception as ex:
            logging.warning(f"Fail to apply_task {task} to {self.vehicle_id}: {ex}")
            self.Scheduler.tasks_pending.append(task)
            return None



class Truck(Vehicle):
    def __init__(self, tracistart, Scheduler,vehicle_id, task):
        super(Truck, self).__init__(tracistart, Scheduler, vehicle_id,task)


class Crane(Vehicle):
    def __init__(self, tracistart, Scheduler, vehicle_id, task):
        super(Crane, self).__init__(tracistart,Scheduler, vehicle_id, task)


    def _load_task(self):
        # todo: 载入装卸任务
        pass

    def _apply_task(self, worktime):
        # todo: 执行一次装/卸
        pass


class Bridge(Vehicle):
    def __init__(self, tracistart, Scheduler, vehicle_id, task):
        super(Bridge, self).__init__(tracistart, Scheduler, vehicle_id, task)

