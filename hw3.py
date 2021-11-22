import sys
import random


def GetCoordinatesInput(s, count, lines):
    coordinates = []
    i = s
    end = s + count

    while i < end:
        c = lines[i].split(" ")
        coordinates.append((int(c[0]), int(c[1])))

        i += 1

    return coordinates, end


class ReinforcementLearning:
    def __init__(self, s, lines):
        dimensions = lines[s].split(" ")
        self.xDimension = int(dimensions[1])
        self.yDimension = int(dimensions[0])
        s += 1

        obstacleCount = int(lines[s])
        self.obstacles, i = GetCoordinatesInput(s + 1, obstacleCount, lines)

        pitfallCount = int(lines[i])
        self.pitfalls, i = GetCoordinatesInput(i + 1, pitfallCount, lines)

        goal = lines[i].split(" ")
        i += 1
        self.goal = (int(goal[0]), int(goal[1]))

        rewards = lines[i].split(" ")
        self.stepReward = float(rewards[0])
        self.obstacleReward = float(rewards[1])
        self.pitfallReward = float(rewards[2])
        self.goalReward = float(rewards[3])

    def WriteOutput(self, pi, path):
        f = open(path, "w+")
        for i in pi:
            f.write(str(i[0][0]) + " " + str(i[0][1]) + " " + str(i[1]) + "\n")

        f.close()

    def IsObstacle(self, state):
        if (state[0] <= 0 or state[0] > self.xDimension):
            return True

        if (state[1] <= 0 or state[1] > self.yDimension):
            return True

        if (state in self.obstacles):
            return True

        return False

    def GetActionResult(self, rawState, action):
        state = (abs(rawState[0]), abs(rawState[1]))

        if (action == 0):
            candidateState = (state[0], state[1] + 1)
            if (self.IsObstacle(candidateState)):
                return state, self.obstacleReward

            return candidateState, self.stepReward

        elif (action == 1):
            candidateState = (state[0] + 1, state[1])
            if (self.IsObstacle(candidateState)):
                return state, self.obstacleReward

            return candidateState, self.stepReward

        elif (action == 2):
            candidateState = (state[0], state[1] - 1)
            if (self.IsObstacle(candidateState)):
                return state, self.obstacleReward

            return candidateState, self.stepReward

        elif (action == 3):
            candidateState = (state[0] - 1, state[1])
            if (self.IsObstacle(candidateState)):
                return state, self.obstacleReward

            return candidateState, self.stepReward

        elif (action == 4):
            negatedState = (-1 * state[0], -1 * state[1])
            if (negatedState == self.goal):
                # -- is this okay?
                return (0, 0), self.goalReward

            nextState = (state[0] * -1, state[1] * -1)
            return nextState, self.pitfallReward

        return (0, 0)

    def GetValueOfState(self, state, values):
        for v in values:
            if (v[0] == state):
                return v[1]

        return 0


class ValueIteration(ReinforcementLearning):
    def __init__(self, lines):
        self.theta = float(lines[1])
        self.gamma = float(lines[2])

        super().__init__(3, lines)

    def InitializeStateFunctions(self):
        V = []

        for i in range(1, self.xDimension + 1):
            for j in range(1, self.yDimension + 1):
                candidateState = (i, j)
                if (not candidateState in self.obstacles):
                    negatedState = (-1 * i, -1 * j)
                    if (negatedState in self.pitfalls):
                        V.append([negatedState, 0])

                    V.append([candidateState, 0])

        VPrime = []
        q = []
        for v in V:
            copyState = (v[0][0], v[0][1])
            VPrime.append([copyState, float("inf")])

            actionCount = 4
            negatedState = (-1 * abs(v[0][0]), -1 * abs(v[0][1]))
            isBendable = negatedState in self.pitfalls or negatedState == self.goal
            if (isBendable):
                actionCount += 1

            q.append([])
            i = 0
            while i < actionCount:
                q[len(q) - 1].append(0)
                i += 1

        return V, VPrime, q

    def GetMaxValueDifference(self, V, Vprime):
        maxDifference = 0
        for i in range(len(V)):
            vValue = V[i][1]
            vPrimeValue = Vprime[i][1]

            difference = abs(vValue - vPrimeValue)
            if (difference > maxDifference):
                maxDifference = difference

        return maxDifference

    def GetValueFunction(self):
        v, vPrime, q = self.InitializeStateFunctions()

        while (self.GetMaxValueDifference(v, vPrime) > self.theta):
            for i in range(len(v)):
                vPrime[i][1] = v[i][1]

            for s_i in range(len(q)):
                state = v[s_i][0]
                for a_i in range(len(q[s_i])):
                    nextState, reward = self.GetActionResult(state, a_i)
                    nextValue = self.gamma * self.GetValueOfState(nextState, v)
                    q[s_i][a_i] = reward + nextValue

                maxValue = float('-inf')
                for a_i in range(len(q[s_i])):
                    if (q[s_i][a_i] > maxValue):
                        maxValue = q[s_i][a_i]

                v[s_i][1] = maxValue

        pi = []
        for s_i in range(len(q)):
            state = v[s_i][0]
            maxValue = float('-inf')
            maxValueAction = -1
            for a_i in range(len(q[s_i])):
                nextState, reward = self.GetActionResult(state, a_i)
                nextValue = self.gamma * self.GetValueOfState(nextState, v)
                totalValue = reward + nextValue

                if (totalValue > maxValue):
                    maxValue = totalValue
                    maxValueAction = a_i

            pi.append((state, maxValueAction))

        return pi

    def Debug(self):
        print(self.theta)
        print(self.gamma)
        print(str(self.xDimension) + " " + str(self.yDimension))
        print(self.obstacles)
        print(self.pitfalls)
        print(self.goal)
        print(self.stepReward)
        print(self.obstacleReward)
        print(self.pitfallReward)
        print(self.goalReward)


class QLearning(ReinforcementLearning):
    def __init__(self, lines):
        self.episodeCount = int(lines[1])
        self.alpha = float(lines[2])
        self.gamma = float(lines[3])
        self.epsilon = float(lines[4])

        super().__init__(5, lines)

    def InitializeStateFunctions(self):
        states = []

        for i in range(1, self.xDimension + 1):
            for j in range(1, self.yDimension + 1):
                candidateState = (i, j)
                if (not candidateState in self.obstacles):
                    negatedState = (-1 * i, -1 * j)
                    if (negatedState in self.pitfalls):
                        states.append(negatedState)

                    states.append(candidateState)

        q = []
        for s in states:
            actionCount = 4
            negatedState = (-1 * abs(s[0]), -1 * abs(s[1]))
            isBendable = negatedState in self.pitfalls or negatedState == self.goal
            if (isBendable):
                actionCount += 1

            q.append([])
            i = 0
            while i < actionCount:
                q[len(q) - 1].append(0)
                i += 1

        return states, q

    def SelectAction(self, actions):
        r = random.uniform(0, 1)
        if (r < self.epsilon):
            randomAction = random.randint(0, len(actions) - 1)
            return randomAction

        maxAction = float('-inf')
        maxActionIndex = 0
        for i in range(len(actions)):
            if (actions[i] > maxAction):
                maxAction = actions[i]
                maxActionIndex = i

        return maxActionIndex

    def GetStateIndex(self, s, states):
        for i in range(len(states)):
            if (states[i] == s):
                return i

        return -1

    def GetNextStateBestValue(self, ns_i, q):
        if (ns_i < 0 or ns_i >= len(q)):
            return 0

        maxValue = float('-inf')
        for v in q[ns_i]:
            if (v > maxValue):
                maxValue = v

        return maxValue

    def GetPolicy(self):
        states, q = self.InitializeStateFunctions()
        maxIterationCount = 10000

        e = 0
        while e < self.episodeCount:
            s_i = random.randint(0, len(states) - 1)
            j = 0
            while j < maxIterationCount:
                a_i = self.SelectAction(q[s_i])
                nextState, reward = self.GetActionResult(states[s_i], a_i)
                ns_i = self.GetStateIndex(nextState, states)

                conservation = (1 - self.alpha) * q[s_i][a_i]
                nextValue = self.GetNextStateBestValue(ns_i, q)
                learn = self.alpha * (reward + self.gamma * nextValue)

                q[s_i][a_i] = conservation + learn
                s_i = ns_i

                if (ns_i == -1):
                    break

                j += 1

            e += 1

        pi = []
        for s_i in range(len(q)):
            maxValue = float('-inf')
            maxValueIndex = 0

            for a_i in range(len(q[s_i])):
                if (q[s_i][a_i] > maxValue):
                    maxValue = q[s_i][a_i]
                    maxValueIndex = a_i

            pi.append((states[s_i], maxValueIndex))

        return pi

    def Debug(self):
        print(self.episodeCount)
        print(self.alpha)
        print(self.gamma)
        print(self.epsilon)
        print(str(self.xDimension) + " " + str(self.yDimension))
        print(self.obstacles)
        print(self.pitfalls)
        print(self.goal)
        print(self.stepReward)
        print(self.obstacleReward)
        print(self.pitfallReward)
        print(self.goalReward)


def QLearningMethod(qLearning):
    qLearning.Debug()
    pass


def ValueIterationMethod(valueIteration):
    valueIteration.Debug()
    pass


def main():
    if (len(sys.argv) != 3):
        return

    inputFile = sys.argv[1]
    with open(inputFile, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip()

        method = lines[0]
        if (method == "Q"):
            qLearning = QLearning(lines)
            pi = qLearning.GetPolicy()
            qLearning.WriteOutput(pi, sys.argv[2])
        elif (method == "V"):
            valueIteration = ValueIteration(lines)
            pi = valueIteration.GetValueFunction()
            valueIteration.WriteOutput(pi, sys.argv[2])

        f.close()


if __name__ == '__main__':
    main()
