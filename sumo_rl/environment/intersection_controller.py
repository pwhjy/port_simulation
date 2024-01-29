class IntersectionController:
    def __init__(self, sumo):
        self.sumo = sumo
        self.edgeIDList = [
            "D2D3", "E6", "-E6", "D3D4", "D4D3", "-E3", "E3", "D3D2"
        ]
        self.edgeID2Idx = {
            "D2D3": 0, "E6": 1, "-E6": 2, "D3D4": 3, "D4D3": 4, "-E3": 5, "E3": 6, "D3D2": 7
        }
        self.conflictIdxList = set()
        for i in [0, 2, 4, 6]:
            self.conflictIdxList.add(((0 + i) % 8, (7 + i) % 8, (0 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (7 + i) % 8, (2 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (7 + i) % 8, (4 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (7 + i) % 8, (6 + i) % 8, (7 + i) % 8))

            self.conflictIdxList.add(((0 + i) % 8, (1 + i) % 8, (0 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (1 + i) % 8, (2 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (1 + i) % 8, (4 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (1 + i) % 8, (6 + i) % 8, (1 + i) % 8))

            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (0 + i) % 8, (3 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (2 + i) % 8, (3 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (2 + i) % 8, (5 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (2 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (4 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (4 + i) % 8, (3 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (6 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (3 + i) % 8, (6 + i) % 8, (3 + i) % 8))

            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (0 + i) % 8, (5 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (2 + i) % 8, (5 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (2 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (4 + i) % 8, (5 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (4 + i) % 8, (7 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (6 + i) % 8, (1 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (6 + i) % 8, (3 + i) % 8))
            self.conflictIdxList.add(((0 + i) % 8, (5 + i) % 8, (6 + i) % 8, (5 + i) % 8))

        self.occupyingIdxpairDict = {}
        self.priorityIdxpairDict = {}

    def getVehicleIDInCircle(self, x, y, radius):
        ids = self.sumo.vehicle.getIDList()
        vehicles = []
        dis = []
        for id in ids:
            pos = self.sumo.vehicle.getPosition(id)
            speedMode = self.sumo.vehicle.getSpeedMode(id)
            if (pos[0] - x) ** 2 + (pos[1] - y) ** 2 <= radius ** 2:
                vehicles.append(id)
                dis.append((pos[0] - x) ** 2 + (pos[1] - y) ** 2)
            else:
                assert speedMode == 31
        vehicles = [x for _, x in sorted(zip(dis, vehicles))]
        return vehicles

    def getEdgeIdxPair(self, vehicleID):
        route = self.sumo.vehicle.getRoute(vehicleID)
        edgeID = self.sumo.vehicle.getRoadID(vehicleID)
        if edgeID not in route:
            return None, None
        assert edgeID in route
        # assert route[-1] != edgeID
        if route[-1] == edgeID:
            nextEdgeID = None
        else:
            nextEdgeID = route[route.index(edgeID) + 1]
        edgeIdx = self.edgeID2Idx[edgeID]
        if nextEdgeID is None:
            nextEdgeIdx = None
        else:
            nextEdgeIdx = self.edgeID2Idx[nextEdgeID]
        return edgeIdx, nextEdgeIdx

    def step(self):
        print("len(self.priorityIdxpairDict):", len(self.priorityIdxpairDict))
        print("len(self.occupyingIdxpairDict):", len(self.occupyingIdxpairDict))
        print("self.priorityIdxpairDict:", self.priorityIdxpairDict)
        print("self.occupyingIdxpairDict:", self.occupyingIdxpairDict)

        ids = self.getVehicleIDInCircle(300, 300, 30)
        for i in ids:
            edgeID = self.sumo.vehicle.getRoadID(i)
            if edgeID not in self.edgeIDList:
                continue
            edgeIdx = self.edgeID2Idx[edgeID]
            if edgeIdx % 2 == 0:
                if i in self.occupyingIdxpairDict.keys():
                    continue
                if i in self.priorityIdxpairDict.keys():
                    continue
                edgeIdx, nextEdgeIdx = self.getEdgeIdxPair(i)
                self.priorityIdxpairDict[i] = (edgeIdx, nextEdgeIdx)
                self.sumo.vehicle.setSpeed(i, 0)
            # else:
            #     if i not in self.occupyingIdxpairDict.keys():
            #         continue
            #     self.occupyingIdxpairDict.pop(i)
            #     self.sumo.vehicle.setSpeedMode(i, 31)
        remove_occ = []
        for i in self.occupyingIdxpairDict.keys():
            if i not in self.sumo.vehicle.getIDList() or i not in self.priorityIdxpairDict.keys():
                remove_occ.append(i)
        for i in remove_occ:
            self.occupyingIdxpairDict.pop(i)

        candidates = []
        for i in self.priorityIdxpairDict.keys():
            assert i not in self.occupyingIdxpairDict.keys()
            # edgeID = self.sumo.vehicle.getRoadID(i)
            # if edgeID not in self.edgeIDList:
            #     print("edgeID:", edgeID)
            #     pass
            # assert edgeID in self.edgeIDList

            edgeIdx, nextEdgeIdx = self.priorityIdxpairDict[i]
            assert edgeIdx % 2 == 0
            if nextEdgeIdx is not None:
                assert nextEdgeIdx % 2 == 1

            conflict = False
            for j in self.occupyingIdxpairDict.keys():
                edgeIdx2, nextEdgeIdx2 = self.occupyingIdxpairDict[j]
                if (edgeIdx, nextEdgeIdx, edgeIdx2, nextEdgeIdx2) in self.conflictIdxList:
                    conflict = True
                    break
            for j in candidates:
                edgeIdx2, nextEdgeIdx2 = self.getEdgeIdxPair(j)
                if (edgeIdx, nextEdgeIdx, edgeIdx2, nextEdgeIdx2) in self.conflictIdxList:
                    conflict = True
                    break

            if conflict:
                continue

            candidates.append(i)

        for i in candidates:
            self.priorityIdxpairDict.pop(i)
            edgeIdx, nextEdgeIdx = self.getEdgeIdxPair(i)
            if nextEdgeIdx is not None:
                self.occupyingIdxpairDict[i] = (edgeIdx, nextEdgeIdx)
            # self.sumo.vehicle.setSpeedMode(i, 55)
            self.sumo.vehicle.setSpeed(i, -1)

        return
