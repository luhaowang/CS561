
#===============================================================================
# Author:Luhao Wang
# Title: Bayesian Network inference
#===============================================================================

import sys, getopt
from decimal import *
import itertools
from copy import deepcopy


OUTPUT = False
DEBUG = False
LOCAL = True

"""
Input_file parser
"""
def read_input_txt_hw3_file(filename):
    ''' Given a input file of assumed format, return query_list, bayes network, and node network'''
    query_lines_type = 1
    node_lines_type = 2
    utility_lines_type = 3
    line_indicator = query_lines_type
    query_lists = []
    BayesNetwork = {}
    node_lines = [] 
    r_file_handle = open(filename,"r") 
    for line in r_file_handle:
        line  = line.strip()
        if line == "******":
            if len(node_lines) != 0:
                node_parser(node_lines,BayesNetwork)
                node_lines = []
            line_indicator += 1
            continue
        if line_indicator == query_lines_type:
            if line.startswith('P'):
                query_type = 1
            elif line.startswith('EU'):
                query_type = 2
            elif line.startswith('MEU'):
                query_type = 3
            query_vars, query_vars_assignment, evidence_assignment = query_parser(line)
            if DEBUG:
                print query_type, query_vars,query_vars_assignment, evidence_assignment
            query_lists.append(QueryClass(query_type,query_vars, query_vars_assignment, evidence_assignment))
        elif line_indicator == node_lines_type:
            if line != '***' and line != '******':
                node_lines.append(line)
            elif line == '***' or line == '******':
                node_parser(node_lines,BayesNetwork)
                node_lines = []
        elif line_indicator == utility_lines_type:
            if line != '***' and line != '******':
                node_lines.append(line)
            elif line == '***' or line == '******':
                node_parser(node_lines,BayesNetwork)
                node_lines = []
    # parse the last one
    node_parser(node_lines,BayesNetwork)
    if DEBUG:
        print query_lists      
        print BayesNetwork
    return query_lists,BayesNetwork       
     
def query_parser(line):
    bracket_l_indx = line.find('(')
    inside_bracket = line[bracket_l_indx + 1: -1]
    parts = inside_bracket.split(" | ")
    query_vars_part = parts[0]
    query_vars, query_vars_assignment = assignment_parser(query_vars_part)
    if len(parts) is 2:
        evidence_vars, evidence_assignment = assignment_parser(parts[1])
    else:
        evidence_assignment = {}
    return  query_vars, query_vars_assignment, evidence_assignment

def node_parser(lines,bn):
    if '|' in lines[0]:
        node_name, parents = lines[0].split('|')
        node_name = node_name.strip()
        parents = parents.strip()
        parents = parents.split(' ')
    else:
        node_name = lines[0]
        parents = []
    if lines[1] == "decision":
        bn[node_name] = ['decision', parents,{}]
    else:
        assignments = node_values_paser(lines[1:],len(parents))
        if node_name == "utility":
            bn[node_name] = ['utility',parents,assignments] 
        else:
            bn[node_name] = ['chance',parents,assignments] 
    
        
# def node_values_paser(lines, num_parents):
#     values = {}
#     for line in lines:
#         value_and_parent_assignments = line.split(" ")
#         value = float(value_and_parent_assignments[0])
#         parent_assignments = value_and_parent_assignments[1:]
#         assignment = []
#         if num_parents == 0:
#             assignment = (None)
#         elif num_parents == 1:
#             if parent_assignments[0] == "+":
#                 assignment = (True)
#             elif parent_assignments[0] == "-":
#                 assignment = (False)
#         elif num_parents >= 2 :
#             for i in range(num_parents):
#                 if parent_assignments[i] == "+":
#                     assignment.append(True)
#                 elif parent_assignments[i] == "-":
#                     assignment.append(False)
#             assignment = tuple(assignment)
#         values[assignment] = value
#     return values


def node_values_paser(lines, num_parents):
    values = {}
    for line in lines:
        value_and_parent_assignments = line.split(" ")
        value = float(value_and_parent_assignments[0])
        parent_assignments = value_and_parent_assignments[1:]
        assignment = []
        if num_parents == 0:
            assignment.append(None)
        else:
            for i in range(num_parents):
                if parent_assignments[i] == "+":
                    assignment.append(True)
                elif parent_assignments[i] == "-":
                    assignment.append(False)
        assignment = tuple(assignment)
        values[assignment] = value
    return values


def assignment_parser(vars_val):
    s = vars_val.strip()
    var_lists = []
    vars_vals_dict = {}
    vars_and_assignments = s.split(", ")
    for var_and_assignment in vars_and_assignments:
        var_and_assignment = var_and_assignment.split(" = ")
        name = var_and_assignment[0]
        var_lists.append(name)
        if len(var_and_assignment) == 1:
            assignment = None
        elif var_and_assignment[1] == '+':
            assignment = True
        elif var_and_assignment[1] == '-':
            assignment = False
        vars_vals_dict[name] = assignment
    return var_lists, vars_vals_dict



class QueryClass():
    def __init__(self,type1,vars_list,vars_val,evs_val):
        self.type = type1
        self.vars_list = vars_list
        self.vars_assignment = vars_val
        self.evs_assignment = evs_val
        
def orderedVars(bn):
    varss = []
    for name in bn:
        varss.append(name)
    numofvars = len(varss)
    count = 0
    varss = []
    while(count < numofvars) :
        for name in bn:
            parents_added = 1
            if len(bn[name][1]) == 0 and (name not in varss): # has no parents
                varss.append(name)
            elif len(bn[name][1]) >=1:
                for i in range(len(bn[name][1])):
                    if bn[name][1][i] not in varss:
                        parents_added = 0 
                if(parents_added == 1 and (name not in varss) ):
                    varss.append(name)
        count = len(varss)
    return varss
                    
"""

End of Parser

""" 

        
"""

Kernal Algorithms

"""

def extend(s, varibles, vals):
    "Copy the substitution s and extend it by setting var to val; return copy."
    s2 = s.copy()
    if isinstance(varibles, list):
        for i in range(len(varibles)):
            s2[varibles[i]] = vals[i]
    else:
        s2[varibles] = vals
    return s2

def valsof(X,e):
    unassigned_query_vars = [v for v in X if v not in e]
    num_query_vars = len(unassigned_query_vars)
    return itertools.product([True, False], repeat=num_query_vars)


def generate_assignments(unassigned_parents,evidence,bn):
    parents_tuple_list = []
    assignment_dict_list = []
    for unassigned_parents_assignment in itertools.product([True, False], repeat=len(unassigned_parents)):
        unassigned_parents_assign_dict = {}
        for i in range(len(unassigned_parents)):
            unassigned_parents_assign_dict[unassigned_parents[i]] = unassigned_parents_assignment[i]  
        parents_truth_tuple = []
        for v in bn['utility'][1]:
            if v in evidence:
                parents_truth_tuple.append(evidence[v])
            if v in unassigned_parents:
                parents_truth_tuple.append(unassigned_parents_assign_dict[v])
        assignment_dict_list.append(unassigned_parents_assign_dict)
        parents_tuple_list.append(tuple(parents_truth_tuple))
    print assignment_dict_list,parents_tuple_list
    return assignment_dict_list,parents_tuple_list
        
    
def Pr(var, val, e, bn):
    if DEBUG:
        print "inside Pr"
        print "var: ", var
        print "val: ", val
    parents = bn[var][1]
    if len(parents) == 0:
        truePr = bn[var][2][tuple([None])]
    else:
        parentVals = [e[parent] for parent in parents]
        truePr = bn[var][2][tuple(parentVals)]
    if val==True:
        if DEBUG:
            print "P: ", truePr
        return truePr
    else:
        if DEBUG:
            print "P: ",1.0-truePr  
        return 1.0-truePr
  

def normalize(QX):
    total = 0.0
    for val in QX.values():
        total += val
    for key in QX.keys():
        QX[key] /= total
    return QX

def enumerationAsk(X, e, bn,varss):
    if DEBUG:
        print "inside enumerationAsk "
        print "X: \t", X
        print "e: \t", e
        print "varss: \t", varss
    QX = {}
    for xi in valsof(X, e):
        QX[xi] = enumerateAll(deepcopy(varss),extend(e, X, xi),bn)
    return normalize(QX)


def enumerateAll(varss, e,bn):
    if DEBUG:
        print "inside enumerateAll "
        print "varss: \t", varss
        print "e: \t", e
    if len(varss) == 0: return 1.0
    Y = varss.pop(0)
    # only hand chance node, skip decision and utility nodes
    if bn[Y][0]!='chance':
        return enumerateAll(varss, e, bn)
    if DEBUG:
        print "Y: \t", Y
    if Y in e:
        val =  Pr(Y,e[Y],e,bn) * enumerateAll(varss,e,bn)
        varss.insert(0,Y)
        return val
    else:
        total = 0.0
        total += Pr(Y,True,e,bn) * enumerateAll(varss,extend(e, Y, True),bn)
        total += Pr(Y,False,e,bn) * enumerateAll(varss,extend(e, Y, False),bn)
        varss.insert(0,Y)
        return total

def Pquery_handler(query,varss,bn): 
    if len(query.evs_assignment) == 0:  # not conditional probability, all are evidences
        return enumerateAll(deepcopy(varss), query.vars_assignment, bn)   
    else: # conditional probability
        proDistri = enumerationAsk(query.vars_list, query.evs_assignment,bn, deepcopy(varss))
        vals = []
        for name in query.vars_list:
            vals.append(query.vars_assignment[name])
        return proDistri[tuple(vals)]
            
            
        
def EUquery_handler(query,varss,bn):
    decisionNodes = []
    # get decision nodes
    for name in bn:
        if bn[name][0] == 'decision':
            decisionNodes.append(name)
    # evidences
    evidence = {}
    for key in query.vars_assignment:
        evidence[key] = query.vars_assignment[key]
    for key in query.evs_assignment:
        evidence[key] = query.evs_assignment[key]
    utilily_parents = bn['utility'][1]
    unassigned_parents = [p for p in utilily_parents if p not in evidence]
    # calculate the probability for each parents assignment
    totalUtility = 0.0
    assignment_list, tupleVal_list = generate_assignments(unassigned_parents,evidence,bn)
    for assignment, tupleVal in zip(assignment_list, tupleVal_list):
        parent_query = QueryClass(1,unassigned_parents,assignment,evidence)
        # get the tuple key of the assignment
        totalUtility += Pquery_handler(parent_query, varss, bn) * bn['utility'][2][tupleVal]
    print totalUtility
    
def MEUquery_handler(query,varss,bn): 
        if len(query.evs_assignment) == 0:  # not conditional probability, all are evidences
            return enumerateAll(deepcopy(varss), query.vars_assignment, bn)   
        else: # conditional probability
            return enumerationAsk(query.vars_list, query.evs_assignment,bn, deepcopy(varss))
"""

End of Kernal Algorithms

"""

if __name__ == "__main__":
    global output_file_handle
    varss = []
    if LOCAL:
        Input_file = "sample05.txt"
    if OUTPUT:
        Input_file = str(sys.argv[2])
    query_list, bn = read_input_txt_hw3_file(Input_file)
    varss = orderedVars(bn)
    if DEBUG:
        print varss
    for query in query_list:
        if query.type == 1: # Probability Query
            val = Pquery_handler(query, varss, bn)
            print "outcome: \t", val
        elif query.type == 2: # EU Query
            EUquery_handler(query,varss,bn)
        elif query.type == 3: # MEU Query:
            pass
    Output_file = "output.txt"
    output_file_handle = open(Output_file,"w")
    output_file_handle.close()
    