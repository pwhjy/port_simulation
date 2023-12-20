import logging
import sumolib
import traci
import networkx
import random

class Scheduler():
    def __init__(self, tracistart):
        self.sumo = tracistart
        self.tasks_pending = []
        self.tasks_ongoing = []
        self.generate_tasks()

    def generate_tasks(self, seed = None):
        """
        生成新任务
        todo: task 修改数据结构
        """

        # todo: 自定义其他任务生成机制
        # ======== 预先人工指定
        # self.tasks_pending.extend(["E1D1","E0D0","E2D2","D2D1","E5","C1C2","D2D3", "E2D2","D3D4","E6","D4E4","E4D4"] * 10)

        # ======== 全部非连接（辅助）边
        edge_ids = self.sumo.edge.getIDList()
        real_edges = [edge_id for edge_id in edge_ids if not edge_id.startswith(":")]
        self.tasks_pending.extend(real_edges * 5)
        logging.info(f"Generate {len( self.tasks_pending) } tasks done")


    def dispatch_task(self, vehicle_id, invalid_task = None):
        """
        给特定车辆指派任务
        :param vehicle_id:
        :return:
        """
        if len(self.tasks_pending) == 0:
            self.generate_tasks()

        # todo：自定义其他任务分配机制
        # ======== 按序分配 FIFO
        # task = self.tasks_pending.pop(0)

        # ======== 随机指派
        # random_index = random.randrange(len(self.tasks_pending))
        # task = self.tasks_pending.pop(random_index)

        # ======== 随机指派, 但是排除上次无效的任务
        tasks_pending = [task for task in self.tasks_pending if task != invalid_task] if invalid_task else self.tasks_pending
        if len(tasks_pending):
            task = random.choice(tasks_pending)
            self.tasks_pending.remove(task)
        else:
            # todo: 没有可执行任务时，也可以考虑指派到某些停车点等待（net待扩充）
            # 生成新的task供选择
            self.generate_tasks()
            task = self.dispatch_task(vehicle_id, invalid_task)

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
        # ======== sumo内置算法寻找最短路
        Route = self.sumo.simulation.findRoute(start_edge, end_edge)
        Route = Route.edges
        return Route
