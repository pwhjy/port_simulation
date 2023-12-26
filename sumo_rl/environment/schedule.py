import logging
import sumolib
import traci
import networkx
import random


def set_positions_on_edge(sumo, lane_id, num):
    """
    在某个lane上生成等间隔任务位点
    """
    points = sumo.lane.getShape(lane_id)
    interval_x = (points[-1][0] - points[0][0]) / (num + 1)
    interval_y = (points[-1][1] - points[0][1]) / (num + 1)
    positions = []

    for i in range(1, num + 1):
        position = ( points[0][0] + i * interval_x,
                     points[0][1] + i * interval_y)  # 获取位置坐标
        positions.append(position)
    return positions


class Scheduler():
    def __init__(self, env):
        self.sumo = env.sumo
        self.destination = {"crane": {},
                            "gantry": {},
                            "other": {} } # { id: { "edge": str_edgeid, "position": tuple_2Dpos } , "serlog":[end_simtime,vehid]}

        self.tasks_pending = {"crane": [],  # list of des_id
                              "gantry": [],
                              "other": []} # todo: 初步不考虑other的存在
        self.tasks_ongoing = {"crane": {}, # { des_id: [ vehicle_id ]}
                              "gantry": {},
                              "other": {} }
        self.generate_destinations()
        self.generate_tasks()

    def generate_destinations(self):
        """
        生成任务终点(装/卸/停...位点)
        """
        # edge_ids = self.sumo.edge.getIDList()
        # real_edges = [edge_id for edge_id in edge_ids if not edge_id.startswith(":")] # 全部非连接（辅助）边

        self.task_edge = {"crane": ["E1D1","E0D0","E2D2","D2D1","E5","C1C2","D2D3", "E2D2","D3D4","E6","D4E4","E4D4"],
                          "gantry": ["E1D1","E0D0","E2D2","D2D1","E5","C1C2"],
                          "other": [] } # todo: 根据实际路网填写edge（lane）, 在net/env处定义
        self.bridge_edge = ["D2D1"] # todo: 根据实际路网填写edge（lane）, 在net/env处定义

        des_id = 1
        all_lanes = self.sumo.lane.getIDList()
        for type, edges in self.task_edge.items():
            for edge in edges:
                lanes_in_edge = [lane_id for lane_id in all_lanes if self.sumo.lane.getEdgeID(lane_id) == edge]
                positions = set_positions_on_edge(self.sumo, lane_id = lanes_in_edge[0],  num = 3)
                for pos in positions:
                    self.destination[type][des_id] = { "edge": edge, "position": pos , "serlog":[-1,-1]}
                    logging.info(f"Generate destination {type}_{des_id}: {self.destination[type][des_id]}")
                    des_id += 1


    def generate_tasks(self, expand = 1, seed = None):
        """
        生成新任务
        """
        for type in self.tasks_pending:  # todo: 不绑定起始点之间的关系, 之后再考虑将任务形式变为 起点->终点 (每次执行任务先从当前位置去起点)\
            all_available_task = expand * list(self.destination[type].keys())
            newtask = random.sample(all_available_task, max(len(all_available_task) - len(self.tasks_pending[type]),0)) # todo: 定义其他任务生成机制
            self.tasks_pending[type].extend(newtask)
            logging.info(f"Generate {len(newtask)} tasks for {type} done")


    def dispatch_task(self, vehicle, invalid_task = None):
        """
        给特定车辆指派任务
        :param vehicle_id:
        :return:
        """
        lasttype = vehicle.destination.get("type", "gantry")
        # curtype = random.choice([type for type in self.destination.keys() if type != lasttype] )# todo: 把other考虑进来
        curtype = "gantry" if lasttype == "crane" else "crane"

        if len(self.tasks_pending[curtype]) == 0:
            self.generate_tasks()

        # todo：自定义其他任务分配机制
        # ======== 按序分配 FIFO
        # task = self.tasks_pending[type].pop(0)

        # ======== 随机指派
        # random_index = random.randrange(len(self.tasks_pending[type]))
        # task = self.tasks_pending[type].pop(random_index)

        # ======== 随机指派, 但是排除上次无效的任务
        tasks_pending = [task for task in self.tasks_pending[curtype] if task != invalid_task] if invalid_task else self.tasks_pending[curtype]
        if len(tasks_pending):
            task = random.choice(tasks_pending)
            self.tasks_pending[curtype].remove(task)
        else:
            # todo: 没有可执行任务时，也可以考虑指派到某些停车点等待（net待扩充）
            # 生成新的task供选择
            self.generate_tasks(expand = 2)
            task = self.dispatch_task(vehicle, invalid_task)
        destination = {"type": curtype,
                       "des_id": task,
                       "edge": self.destination[curtype][task]["edge"],
                       "position": self.destination[curtype][task]["position"]
                       }
        logging.info(f"Dispatch {vehicle.vehicle_id} to {curtype}_{task}: {len(self.tasks_pending[curtype])} tasks pending")
        return destination


    def set_route(self, vehicle_id, start_edge, end_edge):
        """
        为集卡规划任务路由
        todo: 自定义路由算法
        :param vehicle_id:
        :param start_edge:
        :param end_edge:
        :return:
        Route: tuple of edge_ids
        """
        # ======== sumo内置算法寻找最短路
        Route = self.sumo.simulation.findRoute(start_edge, end_edge)
        Route = Route.edges
        return Route

