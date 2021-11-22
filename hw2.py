from copy import deepcopy

DebugMode = False


def Debug(message, condition):
    if (DebugMode and condition):
        print(message)


def FindIndex(word, element, isReverse):
    index = len(word) - 1 if isReverse else 0
    direction = -1 if isReverse else 1

    while (index >= 0 and index < len(word)):
        if (word[index] == element):
            return index

        index += direction

    Debug("Error in FindIndex", True)
    return -1


def IsPredicate(e):
    return e.__contains__("(")


def IsConstant(e):
    if (len(e) == 0):
        return False

    return e[0].isupper()


def IsVariable(e):
    if (len(e) == 0):
        return False

    return not IsPredicate(e) and e[0].islower()


def TrimNegation(e):
    index = 0
    while (len(e) > index and e[index] == "!"):
        index += 1

    if (len(e) <= index):
        Debug("Error in TrimNegation", True)
        return ("", False)

    return e[index:], False if index % 2 == 0 else True


def IsIdentical(e1, e2):
    if (type(e1) != type(e2)):
        return False

    return e1 == e2


class Node:
    def __init__(self, word, parentOne, parentTwo, isLeaf, isRoot):
        self.word = word
        self.parentOne = parentOne
        self.parentTwo = parentTwo
        self.isLeaf = isLeaf
        self.isRoot = isRoot

    def GetSummary(self):
        return self.parentOne.word + "$" + self.parentTwo.word + "$" + self.word

    def __eq__(self, other):
        if (self.word == other.word):
            if (self.parentOne.word == other.parentOne.word and self.parentTwo.word == other.parentTwo.word):
                return True

            if (self.parentOne.word == other.parentTwo.word and self.parentTwo.word == other.parentOne.word):
                return True

        return False

    def SetRoot(self, isRoot):
        self.isRoot = isRoot

    def GetSolution(self, solution):
        if (self.isLeaf):
            return

        self.parentOne.GetSolution(solution)
        self.parentTwo.GetSolution(solution)
        solution.append(self.parentOne.word + "$" +
                        self.parentTwo.word + "$" + self.word)


class Variable:
    def __init__(self, word):
        self.word = word

    def __eq__(self, other):
        return self.word == other.word


class Constant:
    def __init__(self, word):
        self.word = word

    def __eq__(self, other):
        return self.word == other.word


class Predicate:
    def __init__(self, word, isNegated):
        self.isNegated = isNegated
        self.structure = []

        opening = FindIndex(word, "(", False)
        closing = FindIndex(word, ")", True)

        # might want to check if there is anything between opening and closing
        if (opening != -1 and closing != -1):
            self.structure.append(word[0:opening])
            parameters = word[opening+1:closing].split(",")

            for rawParameter in parameters:
                parameter, negation = TrimNegation(rawParameter)
                if (IsConstant(parameter)):
                    self.structure.append(Constant(parameter))
                elif (IsVariable(parameter)):
                    self.structure.append(Variable(parameter))
                else:
                    self.structure.append(Predicate(parameter, negation))

    def ContainsVariable(self, variable):
        index = 1

        while index < len(self.structure):
            parameter = self.structure[index]

            if (type(parameter) == Predicate):
                if (parameter.ContainsVariable(variable)):
                    return True

            elif (type(parameter) == Variable):
                if (parameter == variable):
                    return True

            index += 1

        return False

    def ReplaceVariable(self, r):
        index = 1

        while index < len(self.structure):
            parameter = self.structure[index]

            if (IsIdentical(parameter, r[0])):
                r1 = deepcopy(r[1])
                del self.structure[index]
                self.structure.insert(index, r1)

            if (type(parameter) == Predicate):
                parameter.ReplaceVariable(r)

            index += 1

    def MakeReplacements(self, replacement):
        for r in replacement:
            self.ReplaceVariable(r)

    def ToString(self):
        result = "!" if self.isNegated else ""
        parameters = []
        for p in self.structure:
            if (type(p) == Predicate):
                parameters.append(p.ToString())
            elif (type(p) == Variable or type(p) == Constant):
                parameters.append(p.word)
            else:
                result += p + "("

        for i in range(len(parameters)):
            if (i != 0):
                result += ","

            result += parameters[i]

        result += ")"
        return result


def IsAtom(e):
    return type(e) == Constant or type(e) == Variable


def MGU(e1, e2, replacements):
    if (IsAtom(e1)):
        if (IsIdentical(e1, e2)):
            return True

        if (type(e1) == Variable):
            if (type(e2) == Predicate):
                if (e2.ContainsVariable(e1)):
                    return False

            replacements.append((e1, e2))
            return True

        if (type(e2) == Variable):
            replacements.append((e2, e1))
            return True

        return False

    if (IsAtom(e2)):
        if (IsIdentical(e1, e2)):
            return True

        if (type(e2) == Variable):
            if (type(e1) == Predicate):
                if (e1.ContainsVariable(e2)):
                    return False

            replacements.append((e2, e1))
            return True

        if (type(e1) == Variable):
            replacements.append((e1, e2))
            return True

        return False

    if (e1.structure[0] != e2.structure[0]):
        return False

    if (len(e1.structure) != len(e2.structure)):
        return False

    for i in range(len(e1.structure)):
        if (i == 0):
            continue

        r = []
        isUnifiable = MGU(e1.structure[i], e2.structure[i], r)

        if (not isUnifiable):
            return False

        if (len(r) != 0):
            e1.MakeReplacements(r)
            e2.MakeReplacements(r)
            replacements.extend(r)

    return True


def IsTautology(sentence):
    words = sentence.split("+")

    i = 0
    while i < len(words):
        j = i + 1
        while j < len(words):
            p, pNeg = TrimNegation(words[i])
            q, qNeg = TrimNegation(words[j])

            if (p == q and pNeg != qNeg):
                return True

            j += 1

        i += 1

    return False


def IsSubset(s1, s2):
    wordsOne = s1.split("+")
    wordsTwo = s2.split("+")

    titlesOne = []
    titlesTwo = []

    for w in wordsOne:
        titlesOne.append(w[:w.index("(")])

    for w in wordsTwo:
        titlesTwo.append(w[:w.index("(")])

    if (not all(x in titlesTwo for x in titlesOne)):
        return False

    for p in wordsOne:
        couldConvert = False
        for q in wordsTwo:
            pTrimmed, pNeg = TrimNegation(p)
            qTrimmed, qNeg = TrimNegation(q)

            pPredicate = Predicate(pTrimmed, pNeg)
            qPredicate = Predicate(qTrimmed, qNeg)

            if (MGU(pPredicate, qPredicate, [])):
                couldConvert = True
                break

        if (not couldConvert):
            return False

    return True


def IsThereSubset(node, lst):
    for x in lst:
        if (IsSubset(x.word, node.word)):
            return True

    return False


def GetResolventPart(kp, replacement):
    kpTrimmed, kpNeg = TrimNegation(kp)
    kpPredicate = Predicate(kpTrimmed, kpNeg)
    kpPredicate.MakeReplacements(replacement)
    resolventPart = kpPredicate.ToString()
    return resolventPart


def TryToResolve(leftNode, rightNode):
    left = leftNode.word
    right = rightNode.word
    leftParts = left.split("+")
    rightParts = right.split("+")

    resolvents = []
    for i in range(len(leftParts)):
        for j in range(len(rightParts)):
            lp = leftParts[i]
            rp = rightParts[j]

            lpTrimmed, lpNeg = TrimNegation(lp)
            lpPredicate = Predicate(lpTrimmed, lpNeg)

            rpTrimmed, rpNeg = TrimNegation(rp)
            rpPredicate = Predicate(rpTrimmed, rpNeg)

            replacement = []
            isUnified = MGU(lpPredicate, rpPredicate, replacement)

            if (isUnified and lpPredicate.isNegated != rpPredicate.isNegated):
                resolventParts = []
                for k in range(len(leftParts)):
                    if (k == i):
                        continue

                    kp = leftParts[k]
                    resolventPart = GetResolventPart(kp, replacement)
                    resolventParts.append(resolventPart)

                for k in range(len(rightParts)):
                    if (k == j):
                        continue

                    kp = rightParts[k]
                    resolventPart = GetResolventPart(kp, replacement)
                    resolventParts.append(resolventPart)

                resolvent = ""
                for k in range(len(resolventParts)):
                    resolvent += resolventParts[k]
                    if (k != len(resolventParts) - 1):
                        resolvent += "+"

                if (resolvent == ""):
                    resolvent = "empty"

                resolventNode = Node(resolvent, leftNode,
                                     rightNode, False, True)
                resolvents.append(resolventNode)

    return resolvents


def IsEliminated(node, parentOne, parentTwo):
    if (node.word == "empty"):
        return False

    tautologyFailed = IsTautology(node.word)
    subsetFailed = IsSubset(parentOne.word, node.word) or IsSubset(
        parentTwo.word, node.word)

    return tautologyFailed or subsetFailed


def theorem_prover(argOne, argTwo):
    basePool = []
    for knowledge in argOne:
        node = Node(knowledge, None, None, True, False)
        basePool.append(node)

    for goal in argTwo:
        node = Node(goal, None, None, True, False)
        basePool.append(node)

    resolvents = []
    rawResolvents = []

    alpha = argTwo
    solutions = []
    isSuccessful = False
    while True:
        couldResolve = False

        for r in resolvents:
            if (r.word == "empty" or couldResolve):
                continue

            for b in basePool:
                if (couldResolve):
                    continue

                resolution = TryToResolve(r, b)
                for x in resolution:
                    isEliminated = IsEliminated(x, r, b)

                    if (x not in rawResolvents):
                        rawResolvents.append(x)

                    if (x not in resolvents and not isEliminated):
                        r.SetRoot(False)
                        resolvents.insert(0, x)
                        couldResolve = True

        i = 0
        while i < len(basePool) and not couldResolve:
            j = i + 1
            while j < len(basePool) and not couldResolve:
                resolution = TryToResolve(basePool[i], basePool[j])
                for x in resolution:
                    isEliminated = IsEliminated(x, basePool[i], basePool[j])

                    if (x not in rawResolvents):
                        rawResolvents.append(x)

                    if (x not in resolvents and not isEliminated):
                        resolvents.insert(0, x)
                        couldResolve = True

                j += 1

            i += 1

        if (not couldResolve):
            break

        for r in resolvents:
            if (r.word == "empty"):
                if (r.parentOne.word in alpha):
                    solutions.append(r)
                    alpha.remove(r.parentOne.word)
                elif (r.parentTwo.word in alpha):
                    solutions.append(r)
                    alpha.remove(r.parentTwo.word)

        if (len(alpha) == 0):
            isSuccessful = True
            break

    if (isSuccessful):
        solutionList = []
        for s in solutions:
            partialSolution = []
            s.GetSolution(partialSolution)
            solutionList.extend(partialSolution)

        return ("yes", solutionList)

    unsuccessfulList = []
    for r in rawResolvents:
        unsuccessfulList.append(r.GetSummary())

    return ("no", unsuccessfulList)
