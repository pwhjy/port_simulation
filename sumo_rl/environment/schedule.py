import logging
import sumolib
import traci
import networkx

class Scheduler():
    def __init__(self, tracistart):
        self.sumo = tracistart
        self.tasks_pending = []
        self.tasks_ongoing = []
        self.generate_tasks()

    def generate_tasks(self):
        # todo: task id
        # todo: 自定义任务生成机制
        # edge_ids = self.sumo.edge.getIDList()
        # self.tasks_pending = [edge_id for edge_id in edge_ids if self.sumo.edge.getEdgeType()!= "internal"]
        self.tasks_pending.extend(["E1D1","E0D0","E2D2","D2D1","E5","C1C2","D2D3", "E2D2","D3D4","E6","D4E4","E4D4"] * 10)
        logging.info(f"Generate {len( self.tasks_pending) } tasks done")


    def dispatch_task(self, vehicle_id):
        """
        给特定车辆指派任务
        :param vehicle_id:
        :return:
        """
        if len(self.tasks_pending):
            self.generate_tasks()
        # todo：自定义任务分配机制
        task = self.tasks_pending.pop(0)
        logging.info(f"dispatch task {task} to {vehicle_id}: {len(self.tasks_pending)} tasks pending, {1 + len(self.tasks_ongoing)} tasks ongoing ")
        return task


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
        Route = self.sumo.simulation.findRoute(start_edge, end_edge) # sumo内置算法寻找最短路
        Route = Route.edges
        return Route
