import copy

IntMax = 999999999
IsIterative = False
MaxCost = 0
DiskCount = 0
Goal = ''


class HanoiRod:
    def __init__(self, rodID, disksString):
        self.rodID = rodID
        self.disks = []

        if (disksString == '\r' or disksString == '\n' or disksString == ''):
            return

        disks = disksString.split(',')
        for i in range(len(disks)):
            self.disks.append(int(disks[i]))

    def __eq__(self, other):
        if (len(self.disks) != len(other.disks)):
            return False

        for i in range(len(self.disks)):
            if (self.disks[i] != other.disks[i]):
                return False

        return True

    def ContainsBiggerDisk(self, disk):
        for rodDisk in self.disks:
            if (rodDisk > disk):
                return True

        return False

    def Debug(self):
        print((self.rodID, self.disks))


class HanoiTower:
    def __init__(self, rods, parent):
        self.rods = rods
        self.hValue = -9999
        self.gValue = -9999
        self.fValue = -9999
        self.parent = parent
        self.isRoot = False

    def __eq__(self, other):
        for i in range(len(self.rods)):
            if (self.rods[i] != other.rods[i]):
                return False

        return True

    def IsGoal(self):
        for rod in self.rods:
            if (rod.rodID == Goal and len(rod.disks) != DiskCount):
                return False
            elif (rod.rodID != Goal and len(rod.disks) != 0):
                return False

        return True

    def Expand(self):
        expandedList = []
        for srcRod in self.rods:
            if (len(srcRod.disks) == 0):
                continue

            for dstRod in self.rods:
                if (srcRod.rodID == dstRod.rodID):
                    continue

                srcRodTop = srcRod.disks[len(srcRod.disks) - 1]
                dstRodTop = IntMax
                if (len(dstRod.disks) > 0):
                    dstRodTop = dstRod.disks[len(dstRod.disks) - 1]

                if (srcRodTop < dstRodTop):
                    node = copy.deepcopy(self)
                    del node.GetRodWithID(srcRod.rodID).disks[-1]
                    node.GetRodWithID(dstRod.rodID).disks.append(srcRodTop)

                    if (self.isRoot or (node != self.parent)):
                        node.parent = self
                        node.SetRoot(False)

                        node.CalculateDistances(self.gValue + 1)
                        expandedList.append(node)

        return expandedList

    def Heuristic(self):
        x = 0
        y = 0
        for rod in self.rods:
            if (rod.rodID == Goal):
                for disk in rod.disks:
                    for checkRod in self.rods:
                        if (checkRod.rodID != Goal and checkRod.ContainsBiggerDisk(disk)):
                            y += 1
                            break

            else:
                x += len(rod.disks)

        return x + (y * 2)

    def CalculateDistances(self, gValue):
        self.hValue = self.Heuristic()
        self.gValue = gValue
        self.fValue = self.hValue + gValue

    def GetRodWithID(self, id):
        if (id == 'A'):
            return self.rods[0]
        elif (id == 'B'):
            return self.rods[1]

        return self.rods[2]

    def PrintState(self):
        template = "\nA->{}\tB->{}\tC->{}\n"
        return template.format(self.rods[0].disks, self.rods[1].disks, self.rods[2].disks)

    def PrintSolution(self):
        node = self
        output = []
        while (not node.isRoot):
            output.append(node.PrintState())
            node = node.parent

        print(node.PrintState())
        i = len(output) - 1
        while i >= 0:
            print(output[i])
            i -= 1

    def SetRoot(self, isRoot):
        self.isRoot = isRoot

    def Debug(self):
        for i in range(len(self.rods)):
            self.rods[i].Debug()

        print("Heuristic: " + str(self.hValue))


def LimitedSearch(OPEN, fmax):
    node = OPEN[-1]
    if (node.fValue > fmax):
        return node.fValue

    if (node.IsGoal()):
        if (node.gValue > MaxCost):
            print('FAILURE')
            return 'SUCCESS'

        print('SUCCESS')
        node.PrintSolution()
        return 'SUCCESS'

    minResult = IntMax
    expandedList = node.Expand()
    for expanded in expandedList:
        isInOpen = False
        for opened in OPEN:
            if (opened == expanded):
                isInOpen = True
                break

        if (not isInOpen):
            OPEN.append(expanded)
            result = LimitedSearch(OPEN, fmax)
            if (result == 'SUCCESS'):
                return 'SUCCESS'

            if (result < minResult):
                minResult = result

            OPEN.pop()

    return minResult


def IDAAlgorithm(initialState):
    OPEN = [initialState]
    fmax = initialState.fValue

    while True:
        result = LimitedSearch(OPEN, fmax)
        if (result == 'SUCCESS'):
            return

        fmax = result


def AStarAlgorithm(initialState):
    OPEN = [initialState]
    CLOSED = []

    while True:
        if (len(OPEN) == 0):
            print('FAILURE')
            return

        minF = IntMax
        minFIndex = 0
        for i in range(len(OPEN)):
            if (OPEN[i].fValue < minF):  # equality?
                minF = OPEN[i].fValue
                minFIndex = i

        node = OPEN[minFIndex]
        CLOSED.append(node)
        del OPEN[minFIndex]

        if (node.IsGoal()):
            if (node.gValue > MaxCost):
                print('FAILURE')
                return

            print('SUCCESS')
            node.PrintSolution()
            return

        expandedList = node.Expand()
        for expanded in expandedList:
            isInOpen = False
            isInClosed = False
            openedIndex = -1
            closedIndex = -1

            for i in range(len(OPEN)):
                if (expanded == OPEN[i]):
                    isInOpen = True
                    openedIndex = i
                    break

            for i in range(len(CLOSED)):
                if (expanded == CLOSED[i]):
                    isInClosed = True
                    closedIndex = i
                    break

            if ((not isInOpen) and (not isInClosed)):
                OPEN.append(expanded)
            elif (isInOpen and expanded.gValue < OPEN[openedIndex].gValue):
                OPEN[openedIndex].parent = node
            elif (isInClosed and expanded.gValue < CLOSED[closedIndex].gValue):
                del CLOSED[closedIndex]
                OPEN.append(expanded)


def main():
    global IsIterative, MaxCost, Goal, DiskCount

    problemType = input().rstrip()
    IsIterative = 'IDA*' in problemType

    maxCost = input().rstrip()
    MaxCost = int(maxCost)

    DiskCount = int(input().rstrip())
    Goal = input().rstrip()

    rodALine = input().rstrip()
    rodA = HanoiRod('A', rodALine)

    rodBLine = input().rstrip()
    rodB = HanoiRod('B', rodBLine)

    rodCLine = input().rstrip()
    rodC = HanoiRod('C', rodCLine)

    hanoiTower = HanoiTower([rodA, rodB, rodC], None)
    hanoiTower.CalculateDistances(0)
    hanoiTower.SetRoot(True)

    if (IsIterative):
        IDAAlgorithm(hanoiTower)
    else:
        AStarAlgorithm(hanoiTower)


if __name__ == '__main__':
    main()
