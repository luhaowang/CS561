#!/usr/bin/python
import copy
import sys
from copy import deepcopy

# Debug Mode Switch
DEBUG = False
NEG_INF = -1e6
POS_INF = 1e6


class GameBoard:
    def __init__(self, vL, oL, player):
        self.ValueList=vL
        self.OccupList=oL
        self.player = player
        if self.player == 'X':
            self.opponent= 'O' 
        else:
            if self.player == 'O':
                self.opponent= 'X' 
        
    def setValueList(self, List):
        self.ValueList=List
    
    def getValueList(self):
        return self.ValueList
    
    def getOccupiedList(self):
        return self.OccupList
    
    def setOccupiedBy(self,x,y,arg):
        self.OccupList[(x-1)*5+y-1]=arg

        
    def getOccupiedBy(self,x,y):
        return self.OccupList[(x-1)*5+y-1]
    
    def printGameBoardValue(self):
        for i in range(5):
            s=''
            for j in range(5):
                s += str(self.ValueList[i*5+j])
                s = s+' '
            print s
        
    def printGameBoardOccupiedBy(self):
        for i in range(5):
            s=''
            for j in range(5):
                s += str(self.OccupList[i*5+j])
                s = s +' '
            print s
            
    def setPlayer(self, arg):
        self.player = arg
        if self.player == 'X':
            self.opponent= 'O' 
        else:
            if self.player == 'O':
                self.opponent= 'X' 
    
    def getPlayer(self):
        return self.player
    
    def getOpponent(self):
        return self.opponent
    
'''

Greedy Best-first Search Algorithm Ai

'''       
def GBF_ai(GB, Player, Next_state):
    GB.setPlayer(Player)
    BestMove = takeBestMove(getBestRaidAction(GB),getBestSneakAction(GB))
    print "Greedy Best-first Search AI Best Move for %s is %s" %(Player, printAction([BestMove]))
    next_state_file = open(Next_state,'w')
    if BestMove[2] == 0:
        gbnext = GBafterRaid(BestMove, GB)
    elif BestMove[2] == 1:
        gbnext = GBafterSneak(BestMove, GB)
    for i in range(len(gbnext.getOccupiedList())):
        next_state_file.write(str(gbnext.getOccupiedList()[i]))
        if (i%5 == 4 and i!=0):
            next_state_file.write('\n')
    next_state_file.close()

def GBF_Battle_ai(GB, Player):
    GB.setPlayer(Player)
    BestMove = takeBestMove(getBestRaidAction(GB),getBestSneakAction(GB))
    if BestMove[2] == 0:
        gbnext = GBafterRaid(BestMove, GB)
    elif BestMove[2] == 1:
        gbnext = GBafterSneak(BestMove, GB)
    return gbnext


def getActionsList(gb):
    List = []
    for i in range(1,6):
        for j in range(1,6):
            if checkIfCanRaid(gb, i, j):
                List.append([i,j,0]) # 0 represents raid
            elif checkIfCanSneak(gb, i, j):
                List.append([i,j,1]) # 1 represents sneak
    return List
                   
def getRaidActionList(gb):
    ActionList=[]
    for i in range(1,6):
        for j in range(1,6):
            if checkIfCanRaid(gb, i, j):
                ActionList.append([i,j])
    return ActionList
                
def getBestRaidAction(gb):
    ActionList=getRaidActionList(gb)
    BestRaidWithGain=[]
    RaidGainList= evaluateRaidAction(ActionList, gb)
    if DEBUG:
        print "\n \n Raid Actions can be %s \n \n " %(str(ActionList))
        print "\n \n Raid Gain can be %s \n \n " %(str(RaidGainList))
    maxValue=-1e6
    idx = -1
    for k in range(len(RaidGainList)):
        if RaidGainList[k] > maxValue:
            maxValue =  RaidGainList[k]
            idx = k
    if idx >= 0:
        BestRaidWithGain.append(ActionList[idx][0])
        BestRaidWithGain.append(ActionList[idx][1])
        BestRaidWithGain.append(RaidGainList[idx])
        return BestRaidWithGain

def getSneakActionList(gb):
    ActionList=[]
    for i in range(1,6):
        for j in range(1,6):
            if checkIfCanSneak(gb, i, j):
                ActionList.append([i,j])
    return ActionList    
    
def getBestSneakAction(gb):
    ActionList=getSneakActionList(gb)
    BestSneakWithGain=[]
    if DEBUG:
        print "\n \n Sneak Actions can be %s \n \n " %(str(ActionList))
    SneakGainList = evaluateSneakAction(ActionList, gb)
    if DEBUG:
        print "\n \n Sneak Gain can be %s \n \n " %(str(SneakGainList))
    maxValue=-1e6
    idx = -1
    for k in range(len(SneakGainList)):
        if SneakGainList[k] > maxValue:
            maxValue =  SneakGainList[k]
            idx = k
    if idx >= 0:
        BestSneakWithGain.append(ActionList[idx][0])
        BestSneakWithGain.append(ActionList[idx][1])
        BestSneakWithGain.append(SneakGainList[idx])
        return BestSneakWithGain
    
def takeBestMove(BestRaidWithGain,BestSneakWithGain):
    if BestSneakWithGain != None and BestRaidWithGain  != None:
        if (BestRaidWithGain[2] >= BestSneakWithGain[2]):
            if DEBUG:
                print "Best Move is Raid at (%d,%d)" %(BestRaidWithGain[0],BestRaidWithGain[1])
            return [BestRaidWithGain[0],BestRaidWithGain[1],0]
        elif BestRaidWithGain[2] < BestSneakWithGain[2]:
            if DEBUG:
                print "Best Move is Sneak at (%d,%d)" %(BestSneakWithGain[0],BestSneakWithGain[1]) 
            return [BestSneakWithGain[0],BestSneakWithGain[1],1] 
    else:
        if BestSneakWithGain == None:
            if DEBUG:
                print "Best Move is Raid at (%d,%d)" %(BestRaidWithGain[0],BestRaidWithGain[1])
            return [BestRaidWithGain[0],BestRaidWithGain[1],0]
        elif BestRaidWithGain == None:
            if DEBUG:
                print "Best Move is Sneak at (%d,%d)" %(BestSneakWithGain[0],BestSneakWithGain[1]) 
            return [BestSneakWithGain[0],BestSneakWithGain[1],1] 
        
    
def evaluateRaidAction(RaidActionList,gb):
    List=[]
    for action in RaidActionList:
        gbtemp = copy.deepcopy(gb)
        x = action[0]
        y = action[1]
        gbtemp.setOccupiedBy(x , y, gbtemp.getPlayer())
        for N in getNeighborsList(x, y):
            if gbtemp.getOccupiedBy(N[0] , N[1]) == gbtemp.getOpponent():
                gbtemp.setOccupiedBy(N[0] , N[1], gbtemp.getPlayer())
        List.append(evaluateAll(gbtemp))
        if DEBUG:
            gbtemp.printGameBoardOccupiedBy()
    return List
 
def GBafterRaid(RaidAction, gb):
    gbtemp = deepcopy(gb)
    x = RaidAction[0]
    y = RaidAction[1]
    gbtemp.setOccupiedBy(x , y, gbtemp.getPlayer())
    for N in getNeighborsList(x, y):
        if gbtemp.getOccupiedBy(N[0] , N[1]) == gbtemp.getOpponent():
            gbtemp.setOccupiedBy(N[0] , N[1], gbtemp.getPlayer()) 
    return gbtemp   
    
def evaluateSneakAction(SneakActionList,gb):
    List=[]
    for action in SneakActionList:
        gbtemp = copy.deepcopy(gb)
        x = action[0]
        y = action[1]
        gbtemp.setOccupiedBy(x , y, gbtemp.getPlayer())
        List.append(evaluateAll(gbtemp))
    return List

def GBafterSneak(SneakAction, gb):
    gbtemp = deepcopy(gb)
    x = SneakAction[0]
    y = SneakAction[1]
    gbtemp.setOccupiedBy(x , y, gbtemp.getPlayer())
    return gbtemp   
    
    
def evaluateAll(gb):
    playerValue = 0
    oppoValue = 0
    for i in range(5):
        for j in range(5):
            if gb.getOccupiedList()[i*5+j] == gb.getPlayer():
                playerValue += gb.getValueList()[i*5+j]
            else:
                if gb.getOccupiedList()[i*5+j] == gb.getOpponent():
                    oppoValue += gb.getValueList()[i*5+j]
    return (playerValue - oppoValue) 
                                                
def checkIfCanRaid(gb, x, y):
    pP=0
    oP=0
    if gb.getOccupiedBy(x,y)!= '*':
        if DEBUG:
            print "player %s cannot raid at  (%d , %d ) " %(gb.getPlayer(), x, y)
        return False
    else:
        for v in getNeighborsList(x, y):
            vx = v[0]
            vy = v[1]
            if gb.getOccupiedBy(vx,vy) == gb.getPlayer():
                pP += 1
            else:
                if gb.getOccupiedBy(vx,vy) == gb.getOpponent():
                    oP += 1
        if pP>0 and oP>0 :
            if DEBUG:
                print "player %s can raid at  (%d , %d ) " %(gb.getPlayer(), x, y)
            return True
        else:
            if DEBUG:
                print "player %s cannot raid at  (%d , %d ) " %(gb.getPlayer(), x, y)
            return False
 
def checkIfCanSneak(gb, i, j):
    if (gb.getOccupiedBy(i,j) == '*') and checkIfCanRaid(gb, i, j) == False:
        if DEBUG:
            print "player %s can sneak at  (%d , %d ) " %(gb.getPlayer(), i, j)
        return True
    else:
        if DEBUG:
            print "player %s cannot sneak at  (%d , %d ) " %(gb.getPlayer(), i, j)
        return False
     
def getNeighborsList(x, y):
    List = [moveUp(x, y), moveDown(x, y), moveRight(x, y), moveLeft(x, y)]
    if x == 1:
        List.remove(moveUp(x, y))
    if x == 5:
        List.remove(moveDown(x, y))
    if y == 1:
        List.remove(moveLeft(x, y))
    if y == 5:
        List.remove(moveRight(x, y))
    if DEBUG:
        print "Get NeighborList at  (%d , %d )" %(x, y)
        print  List
    return List

def moveRight(x,y):
    return [x , y + 1]
    
def moveLeft(x,y):
    return [x , y - 1]
    
def moveUp(x,y):
    return [(x - 1) , y]
    
def moveDown(x,y):
    return [(x + 1) , y]      

'''

 MinMax Algorithm Ai
 
'''

def  MinMax_ai(GB, Player, cuttoff, Output_log, Next_state):
    root = Node(GB, 0, Player, cuttoff, NEG_INF)
    log_file = open(Output_log,"w")
    log_file.write("Node,Depth,Value")
    log_file.write("\n")
    log_file.write("root,0,-Infinity")
    log_file.write("\n")
    targetValue = MinMaxDecision(root,Player,log_file)
    for i in range(len(root.children)):
        if root.children[i].val == targetValue :
            idx = i
            break
        #print root.children[i].val
    print "MinMax AI Best Move for %s is %s" %(Player, printAction(root.children[idx].actionFromPrev))
    next_state_file = open(Next_state,'w')
    for i in range(len(root.children[idx].gbcur.getOccupiedList())):
        next_state_file.write(str(root.children[idx].gbcur.getOccupiedList()[i]))
        if (i%5 == 4 and i!=0):
            next_state_file.write('\n')
    next_state_file.close()
    log_file.close()
            
def MinMax_Battle_ai(GB, Player, cuttoff):
    root = Node(GB, 0, Player, cuttoff, NEG_INF)
    targetValue = MinMaxDecision(root,Player,None)            
    for i in range(len(root.children)):
        if root.children[i].val == targetValue :
            idx = i
            break     
    return root.children[idx].gbcur
    
class Node():
    def __init__(self, GB, depth, player,cuttoff, val, action = [[0,0,0]]):
        self.depth = depth
        self.player = player
        self.cutoff = cuttoff
        self.actionFromPrev = action
        self.val = val
        self.children = []
        self.childrenAction = []
        self.gbcur = deepcopy(GB)
        self.gbcur.setPlayer(player)

        
    def CreateChildren(self):
        ActionList = getActionsList(self.gbcur)
        #print ActionList
        for k in range(len(ActionList)):
            action = [ActionList[k][0],ActionList[k][1]]
            self.childrenAction.append(ActionList[k])
            if ActionList[k][2] == 0: # Raid Action
                if self.depth == self.cutoff - 1:
                    v = evaluateRaidAction([action], self.gbcur )
                    if (self.depth + 1) % 2 == 1 :
                        self.children.append(Node(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, v[0], [ActionList[k]]))
                    if (self.depth + 1) % 2 == 0 :
                        self.children.append(Node(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, -1*v[0], [ActionList[k]]))
                elif (self.depth + 1) % 2 == 1 :
                    self.children.append(Node(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, POS_INF, [ActionList[k]]))
                elif (self.depth + 1) % 2 == 0 :
                    self.children.append(Node(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, NEG_INF, [ActionList[k]]))
            elif ActionList[k][2] == 1: # Sneak Action
                if self.depth == self.cutoff - 1:
                    v = evaluateSneakAction([action], self.gbcur )
                    if (self.depth + 1) % 2 == 1 :
                        self.children.append(Node(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, v[0], [ActionList[k]]))
                    if (self.depth + 1) % 2 == 0 :
                        self.children.append(Node(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, -1*v[0], [ActionList[k]]))
                elif (self.depth + 1) % 2 == 1 :
                    self.children.append(Node(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, POS_INF, [ActionList[k]]))
                elif (self.depth + 1) % 2 == 0 :
                    self.children.append(Node(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, NEG_INF, [ActionList[k]]))

def MinMaxDecision(node,maxPlayer,log_file):      
    if node.depth < node.cutoff:
        node.CreateChildren()
        for idx in range(len(node.children)):
            action = node.children[idx].actionFromPrev
            if(log_file != None):
                WriteALine(log_file,[printAction(action),node.children[idx].depth,node.children[idx].val])
            #print "%s, %d, %0.1f" %(printAction(action),node.children[idx].depth,node.children[idx].val)
            value = MinMaxDecision(node.children[idx],maxPlayer,log_file)
            if node.depth % 2 == 0:
                if value >= node.val:
                    node.val = value
            elif node.depth % 2 == 1:
                if value <= node.val:
                    node.val = value
            if(log_file != None):
                WriteALine(log_file,[printAction(node.actionFromPrev),node.depth,node.val])
            #print "%s, %d, %0.1f" %(printAction(node.actionFromPrev),node.depth,node.val)
        return node.val
                     
    elif node.depth == node.cutoff:
        return node.val
        
            
def printAction(action):
    ac = ""
    if (action[0][1]==1):
        ac += 'A'
    elif (action[0][1]==2):
        ac += 'B'
    elif (action[0][1]==3):
        ac += 'C'
    elif (action[0][1]==4):
        ac += 'D'
    elif (action[0][1]==5):
        ac += 'E'
    elif (action[0][0]==0 and action[0][1]==0 ):
        ac += "root"
        return ac   
    ac += str(action[0][0])
    return ac
            
                    
def MinValue(List): 
    minV = 1e6
    for i in range(len(List)):
        if List[i] <= minV:
            minV = List[i]
            idx = i
    return idx

def MaxValue(List):
    maxV = -1e6
    for i in range(len(List)):
        if List[i] >= maxV:
            maxV = List[i]
            idx = i
    return idx  


'''

Alpha-Beta Pruning Algorithm Ai


'''

def AlphaBetaPruning_ai (GB, Player, cuttoff, Output_log, Next_state): 
    root = Node_abp(GB, 0, Player, cuttoff, NEG_INF)
    log_file = open(Output_log,"w")
    log_file.write("Node,Depth,Value,Alpha,Beta")
    log_file.write("\n")
    log_file.write("root,0,-Infinity,-Infinity,Infinity")
    log_file.write("\n")
    targetValue = AlphaBetaPruningDecision(root,Player,log_file)
    for i in range(len(root.children)):
        if root.children[i].val == targetValue :
            idx = i
            break
        #print root.children[i].val
    print "AlphaBetaPruning AI Best Move for %s is %s" %(Player, printAction(root.children[idx].actionFromPrev))
    next_state_file = open(Next_state,'w')
    for i in range(len(root.children[idx].gbcur.getOccupiedList())):
        next_state_file.write(str(root.children[idx].gbcur.getOccupiedList()[i]))
        if (i%5 == 4 and i!=0):
            next_state_file.write('\n')
    next_state_file.close()
    log_file.close()

def AlphaBetaPruning_Battle_ai(GB, Player, cuttoff): 
    root = Node_abp(GB, 0, Player, cuttoff, NEG_INF)
    targetValue = AlphaBetaPruningDecision(root,Player,None)
    for i in range(len(root.children)):
        if root.children[i].val == targetValue :
            idx = i
            break
    return root.children[idx].gbcur
    
class Node_abp():
    def __init__(self, GB, depth, player,cuttoff,val, alpha = NEG_INF, beta = POS_INF, action = [[0,0,0]]):
        self.depth = depth
        self.player = player
        self.cutoff = cuttoff
        self.actionFromPrev = action
        self.alpha = alpha
        self.beta = beta
        self.val = val
        self.children = []
        self.gbcur = deepcopy(GB)
        self.gbcur.setPlayer(player)
        self.ChildIndex = 0
        self.childrenAction = []
        if self.depth < self.cutoff:
            self.CreateChildrenActionList()
            
        
    def GetNextChild(self):
        action = [self.childrenAction[self.ChildIndex][0], self.childrenAction[self.ChildIndex][1]]
        if self.childrenAction[self.ChildIndex][2] == 0: # Raid Action
            if self.depth == self.cutoff - 1:
                v = evaluateRaidAction([action], self.gbcur )
                if (self.depth + 1) % 2 == 1 :
                    self.children.append(Node_abp(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, v[0], NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
                if (self.depth + 1) % 2 == 0 :
                    self.children.append(Node_abp(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, -1*v[0],NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
            elif (self.depth + 1) % 2 == 1 :
                self.children.append(Node_abp(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, POS_INF, NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
            elif (self.depth + 1) % 2 == 0 :
                self.children.append(Node_abp(GBafterRaid(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, NEG_INF, NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
        elif self.childrenAction[self.ChildIndex][2] == 1: # Sneak Action
            if self.depth == self.cutoff - 1:
                v = evaluateSneakAction([action], self.gbcur )
                if (self.depth + 1) % 2 == 1 :
                    self.children.append(Node_abp(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, v[0], NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
                if (self.depth + 1) % 2 == 0 :
                    self.children.append(Node_abp(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, -1*v[0], NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
            elif (self.depth + 1) % 2 == 1 :
                self.children.append(Node_abp(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, POS_INF, NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
            elif (self.depth + 1) % 2 == 0 :
                self.children.append(Node_abp(GBafterSneak(action, self.gbcur), self.depth + 1, self.gbcur.getOpponent(), self.cutoff, NEG_INF, NEG_INF, POS_INF, [self.childrenAction[self.ChildIndex]]))
        self.ChildIndex = self.ChildIndex + 1
        return self.children[self.ChildIndex - 1]
        
    def HasNextChild(self):
        if (self.ChildIndex < len(self.childrenAction)):
            return True
        elif (self.ChildIndex >= len(self.childrenAction)):
            return False
    
    def CreateChildrenActionList(self):
        ActionList = getActionsList(self.gbcur)
        for i in range(len(ActionList)):
            self.childrenAction.append(ActionList[i])
        
                    
                    
                    
def AlphaBetaPruningDecision(node,maxPlayer,log_file):
    if node.depth < node.cutoff:
        while(node.HasNextChild()):
            node_child = node.GetNextChild()
            node_child.alpha = node.alpha
            node_child.beta = node.beta
            if node.depth % 2 == 0:
                if node.beta > node.alpha:
                    action = node_child.actionFromPrev
                    if log_file != None:
                        WriteALine(log_file,[printAction(action),node_child.depth,node_child.val, node_child.alpha, node_child.beta])
                    #print "%s, %d, %d, %d %d" %(printAction(action),node.children[idx].depth,node.children[idx].val, node.children[idx].alpha, node.children[idx].beta)
                    value = AlphaBetaPruningDecision(node_child,maxPlayer,log_file)
                    if value > node.val:
                        node.val = value
                        if value >= node.beta:
                            if log_file != None:
                                WriteALine(log_file,[printAction(node.actionFromPrev),node.depth, node.val, node.alpha, node.beta])
                            return node.val
                        if value > node.alpha:
                            node.alpha = value
                else:
                    return node.val
            if node.depth % 2 == 1:
                if node.beta > node.alpha:
                    action = node_child.actionFromPrev
                    if log_file != None:
                        WriteALine(log_file,[printAction(action),node_child.depth,node_child.val, node_child.alpha, node_child.beta])
                    #print "%s, %d, %d, %d %d" %(printAction(action),node.children[idx].depth,node.children[idx].val, node.children[idx].alpha, node.children[idx].beta)
                    value = AlphaBetaPruningDecision(node_child,maxPlayer,log_file)
                    if value < node.val:
                        node.val = value
                        if value <= node.alpha:
                            if log_file != None:
                                WriteALine(log_file,[printAction(node.actionFromPrev),node.depth, node.val, node.alpha, node.beta])
                            return node.val
                        if value <= node.beta:
                            node.beta = value
                else:
                    return node.val
            if log_file != None:
                WriteALine(log_file,[printAction(node.actionFromPrev),node.depth, node.val, node.alpha, node.beta])
            #print "%s, %d, %d, %d %d" %(printAction(node.actionFromPrev),node.depth, node.val, node.alpha, node.beta)
        return node.val                 
    elif node.depth == node.cutoff:
        return node.val
'''

Battle between Two AIs

'''
def Battlle(GB,player,alg_num,cuttoff,trace_state):
    trace_file = open(trace_state,'w')
    gb_temp = deepcopy(GB)
    while(True):
        if(alg_num[0] == 1):
            gb_temp = GBF_Battle_ai(gb_temp,player[0])
        elif (alg_num[0] == 2):
            gb_temp = MinMax_Battle_ai(gb_temp, player[0], cuttoff[0])
        elif (alg_num[0] == 3):
            gb_temp = AlphaBetaPruning_Battle_ai(gb_temp, player[0], cuttoff[0])
        for i in range(25):
            trace_file.write(str(gb_temp.getOccupiedList()[i]))
            if (i%5 == 4 and i!=0):
                trace_file.write('\n')
        if(HasTerminated(gb_temp) == True):
            gb_temp.setPlayer(player[0])
            result = evaluateAll(gb_temp)
            if result > 0:
                print "Player %s Wins %d ! \n" %(player[0],result)
            elif result < 0:
                print "Player %s Wins %d ! \n" %(player[1],-1*result)
            elif result == 0:
                print "Tie \n" 
            break
        if(alg_num[1] == 1):
            gb_temp = GBF_Battle_ai(gb_temp,player[1])
        elif (alg_num[1] == 2):
            gb_temp = MinMax_Battle_ai(gb_temp, player[1], cuttoff[1])
        elif (alg_num[1] == 3):
            gb_temp = AlphaBetaPruning_Battle_ai(gb_temp, player[1], cuttoff[1])
        for i in range(25):
            trace_file.write(str(gb_temp.getOccupiedList()[i]))
            if (i%5 == 4 and i!=0):
                trace_file.write('\n')
        if(HasTerminated(gb_temp) == True):
            gb_temp.setPlayer(player[0])
            result = evaluateAll(gb_temp)
            if result > 0:
                print "Player %s Wins %d ! \n" %(player[0],result)
            elif result < 0:
                print "Player %s Wins %d ! \n" %(player[1],-1*result)
            elif result == 0:
                print "Tie \n" 
            break
    trace_file.close()
        
            
def HasTerminated(GB):
    for i in range(len(GB.getOccupiedList())):
        if GB.getOccupiedList()[i] ==  '*':
            return False
    return True
        
                
    
def FileRead(filename):
    fo = open(str(filename),"r")
    TaskNumber = fo.readline()
    player = [] 
    ValueList = []
    OccupiedList = []
    alg_num = []
    cuttoff = [] 
    if(int(TaskNumber) == 1 or int(TaskNumber) == 2 or int(TaskNumber) == 3):
        player.append(str(fo.readline()[0]))
        alg_num.append(int(TaskNumber))
        cuttoff.append(int(fo.readline()[0]))
        for i in range(5):
            line = fo.readline().split()
            for j in range(len(line)):
                ValueList.append(int(line[j]))
        for i in range(5):
            line = fo.readline()
            for j in range(5):
                OccupiedList.append(line[j])

    elif (int(TaskNumber) == 4):
        player.append(str(fo.readline()[0]))
        alg_num.append(int(fo.readline()[0]))
        cuttoff.append(int(fo.readline()[0]))
        player.append(str(fo.readline()[0]))
        alg_num.append(int(fo.readline()[0]))
        cuttoff.append(int(fo.readline()[0]))
        for i in range(5):
            line = fo.readline().split()
            for j in range(len(line)):
                ValueList.append(int(line[j]))
        for i in range(5):
            line = fo.readline()
            for j in range(5):
                OccupiedList.append(line[j])        
    fo.close() 
    return [TaskNumber, alg_num, player, cuttoff, ValueList,OccupiedList]        
        
        
        

def WriteALine(log_file,List):
    s= ""
    for idx in range(len(List)):
        c = List[idx]
        if c == 1e6:
            s += "Infinity"
        elif c == -1e6:
            s += "-Infinity"
        else:
            s += str(c)
        if idx != len(List) - 1:
            s += ',' 
    log_file.write(s)
    log_file.write("\n")
        
               
         

if __name__ == '__main__':
    
    '''
    Input_file = "./3/input_1.txt"
    Output_log = "./3/trace_log_luhao.txt"
    Next_state = "./3/netx_state_luhao.txt"
    trace_state = "./3/trace_state_luhao.txt"
    '''
    
    '''
    Input_file = "./4/input.txt"
    Output_log = "./4/trace_log_luhao.txt"
    Next_state = "./4/netx_state_luhao.txt"
    trace_state = "./4/trace_state_luhao.txt"
    '''
    
    #'''
    Input_file = str(sys.argv[2])
    Output_log = "./traverse_log.txt"
    Next_state = "./next_state.txt"
    trace_state = "./trace_state.txt"
    #'''

    [TaskNumber, alg_num, player, cuttoff, ValueList,OccupiedList] = FileRead(Input_file)
    GB=GameBoard(ValueList,OccupiedList, player)
    print GB.getPlayer()
    GB.printGameBoardValue()
    GB.printGameBoardOccupiedBy()

    if (int(TaskNumber) == 1):
        GBF_ai(GB,player[0], Next_state)
    elif (int(TaskNumber) == 2):
        MinMax_ai(GB, player[0], cuttoff[0],Output_log, Next_state)
    elif (int(TaskNumber) == 3):
        AlphaBetaPruning_ai(GB, player[0], cuttoff[0], Output_log,Next_state)
    elif (int(TaskNumber) == 4):
        Battlle(GB,player,alg_num,cuttoff,trace_state)
        
