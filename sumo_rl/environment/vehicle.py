import logging
import random
from typing import Callable, Optional, Tuple, Union
import sumolib
import traci
import networkx

class Vehicle():
    def __init__(self, env,  vehicle_id, task: Union[str, list, None]):
        self.sumo = env.sumo
        self.Scheduler = env.Scheduler
        self.vehicle_id = vehicle_id
        self.priority = 2 # feature1 优先级

        ## ======== 任务状态
        self.start_task = False
        self.finish_task = False
        self.pause_ontask = False
        self.destination: dict = {}

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
            logging.warning(f"Fail to route {self.vehicle_id} to {start_edge, end_edge}: {ex}")
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
        todo: 如果设置的[delta_time较大/速度较快/threshold小]会捕捉不到到达终点附近
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
            self.Scheduler.tasks_ongoing[self.destination["type"]][self.destination["des_id"]].remove(self.vehicle_id)
            self.Scheduler.destination[self.destination["type"]][self.destination["des_id"]]["serlog"] = [self.sumo.simulation.getTime(), self.vehicle_id]
            logging.info(f"""{self.vehicle_id} finish task in {WaitingTime} steps at destination {self.destination["id"]} edge {self.sumo.vehicle.getRoadID(self.vehicle_id)}""")
        # if  WaitingTime:
        #     print(f"WaitingTime of {self.vehicle_id} = {WaitingTime}, "
        #       f"finish_task = {self.finish_task}, "
        #       f"pause_ontask = { self.pause_ontask} "
        #       f"start_task = {self.start_task}")
        return self.finish_task

    def _apply_task(self, task: Union[dict, None], invalid_task = None):
        """
        执行一次运输任务
        :param des:
        :return:
        """
        Task = task if task else self.Scheduler.dispatch_task(self, invalid_task)
        try:
            route = Task["edge"]  # todo: 从task中解析route（起）始点
            end_edge = self._route_vehicle(route)
            if end_edge:
                self.sumo.vehicle.setSpeed(self.vehicle_id, self.speed)
                # end_lanes = [lane_id for lane_id in self.sumo.lane.getIDList() if
                #              self.sumo.lane.getEdgeID(lane_id) == end_edge]
                # lane = self.sumo.lane.getShape(end_lanes[0])
                self.destination = {"id": 0,
                                    "type": Task["type"],
                                    "des_id": Task["des_id"],
                                    "edge": end_edge,
                                    "position": Task["position"]
                                    }
                # self.Scheduler.tasks_ongoing[Task["type"]].setdefault([Task["des_id"]], []).append(self.vehicle_id)
                if Task["des_id"] in self.Scheduler.tasks_ongoing[Task["type"]]:
                    self.Scheduler.tasks_ongoing[Task["type"]][Task["des_id"]].append(self.vehicle_id)
                else:
                    self.Scheduler.tasks_ongoing[Task["type"]][Task["des_id"]] = [self.vehicle_id]
                self.finish_task = False
            else:
                logging.warning(f"""Fail to dispatch {self.vehicle_id} to {Task["type"]}_{Task["des_id"]}, try to apply task again""")
                self.Scheduler.tasks_pending[Task["type"]].append(Task["des_id"])
                self._apply_task(task = None, invalid_task = Task["des_id"])
        except Exception as ex:
            logging.warning(f"Fail to apply_task {Task} to {self.vehicle_id}: {ex}")
            self.Scheduler.tasks_pending[Task["type"]].append(Task["des_id"])


    # 获取车辆距离路口的距离
    def get_vehicle_distance_to_junction(vehicle_id):
        return traci.vehicle.getDistanceToNextJunction(vehicle_id)

    def _get_observation_(self):
        destype_map = {"crane": 0, "gantry": 1, "other": 2} # todo
        self.cur_Lane = self.sumo.vehicle.getLaneID(self.vehicle_id)
        self.position = self.sumo.vehicle.getPosition(self.vehicle_id)
        self.cur_edge = self.sumo.vehicle.getRoadID(self.vehicle_id)
        next_junc = self.sumo.lane.getShape(self.cur_Lane)[-1] # todo
        vehicle_in_bridge = set([vehicle for edge in self.Scheduler.bridge_edge
                                 for vehicle in self.sumo.edge.getLastStepVehicleIDs(edge)]) # todo
        # ========= priority_feature
        cargo_precedence_feature = self.priority  # feature1 优先级

        # ========= target_feature
        target_waiting_feature = self.sumo.simulation.getTime() \
                                 - self.Scheduler.destination[self.destination["type"]][self.destination["des_id"]]["serlog"][0] # feature2 目标点处于空闲状态的时间 # todo
        vehicle_target_type = destype_map[self.destination["type"]]  # feature3 目的地类型  crane / gantry / other [0,1,2]

        # ========= crane_feature
        crane_related_vehicle_list = self.Scheduler.tasks_ongoing[self.destination["type"]][self.destination["des_id"]] # feature4 crane相关的vehlist # todo
        crane_related_igv_in_bridge = len(set(crane_related_vehicle_list).intersection(vehicle_in_bridge)) \
            if self.destination["type"] == "crane" else 0  # feature5 目标为当前crane在引桥上的车辆数 todo: 目的地是岸桥呢?

        # ========= vehicle_feature
        vehicle_current_road_length = self.sumo.lane.getLength(self.cur_Lane) # feature6 当前车辆所在车道的长度 # todo
        vehicle_is_valid = 1 # feature8 当前车辆是否有效
        vehicle_is_arrived_target = int(self._check_task_start(threshold = 10) ) # feature9 当前车辆是否到达目标点
        vehicle_waiting_time = self.sumo.vehicle.getWaitingTime(self.vehicle_id) # feature11 当前车辆处于等待的时长
        vehicle_current_speed = self.sumo.vehicle.getSpeed(self.vehicle_id) # feature12 当前车速
        vehicle_distance_to_junction = self.sumo.simulation.getDistance2D(self.position[0], self.position[1],
                                                                          next_junc[0], next_junc[1]) # feature13 当前车辆距离junc的dis
        vehicle_is_in_junction = 1 if vehicle_distance_to_junction < 2 else 0 # feature10 当前车辆是否在junc

        # ========= road/lane_feature
        road_vehicle_num = self.sumo.edge.getLastStepVehicleNumber(self.cur_edge)  # feature7 当前edge车辆数 # todo
        lane_vehicle_num = self.sumo.lane.getLastStepVehicleNumber(self.cur_Lane)  # feature14 当前lane车辆数 # todo
        lane_limit_speed = self.sumo.lane.getMaxSpeed(self.cur_Lane) # feature15 当前lane的限速 # todo
        road_length = vehicle_current_road_length # feature16 当前road的长度 = feature6

        feature = [cargo_precedence_feature,
                   target_waiting_feature,
                   vehicle_target_type,
                   crane_related_vehicle_list,
                   crane_related_igv_in_bridge,
                   vehicle_current_road_length,
                   road_vehicle_num,
                   vehicle_is_valid,
                   vehicle_is_arrived_target,
                   vehicle_is_in_junction,
                   vehicle_waiting_time,
                   vehicle_current_speed,
                   vehicle_distance_to_junction,
                   lane_vehicle_num,
                   lane_limit_speed,
                   road_length]
        print(self.vehicle_id, feature)
        return feature

    def _set_priority(self, priority):
        self.priority = priority
        logging.info(f"Set {self.vehicle_id} at priority {self.priority}")


class Truck(Vehicle):
    def __init__(self, env, vehicle_id, task):
        super(Truck, self).__init__(env, vehicle_id,task)


class Crane(Vehicle):
    def __init__(self, env, vehicle_id, task):
        super(Crane, self).__init__(env, vehicle_id, task)


    def _load_task(self):
        # todo: 载入装卸任务
        pass

    def _apply_task(self, worktime):
        # todo: 执行一次装/卸
        pass


class Gantry(Vehicle):
    def __init__(self, env, vehicle_id, task):
        super(Gantry, self).__init__(env, vehicle_id, task)

