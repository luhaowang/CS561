import sys
import copy


# -----------------------------------------------------
# init

SEP = '\n'
INF = 65536
output_file_name = 'output.txt'




class Node(object):
    def __init__(self, name='', parents=[], table=[]):
        self.name = name
        self.parents = parents
        self.table = table
        self.type = ''

    def p(self, v='', e={}):
        """
        :param v: '+' or '-'
        :param e: query like {'A':'+', 'B':'-'}
        :return: probability like P(C = + | A = +, B = -)
        """

        if self.type == 'decision':
            return 1.0

        for i in range(len(self.table)):
            matched = True
            for j in range(len(self.parents)):
                parent = self.parents[j]
                value = self.table[i][j+1]
                if e[parent] != value:
                    matched = False
                    break
            if matched:
                if v == '+': return self.table[i][0]
                elif v == '-': return 1.0 - self.table[i][0]

class Network(object):
    def __init__(self):
        self.vars = []
        self.nodes = []
        self.utility = None

    def add_node(self, node=Node()):
        self.vars.append(node.name)
        self.nodes.append(node)

    def get_node(self, name=''):
        """
        return node by name
        :param name: specific node name for getting the node
        :return: node
        """
        index = self.vars.index(name)
        return self.nodes[index]

    def is_decision_node(self, name=''):
        node = self.get_node(name)
        return node.type == 'decision'



# -----------------------------------------------------
# function

def output_line(q='', val=0.0, meu_values=[]):
    if q == 'P':
        output_file.write("%.2f" %round(val, 2))
    elif q == 'EU':
        output_file.write(str(int(round(val))))
    elif q == 'MEU':
        meu_str = ''
        for v in meu_values:
            meu_str += v + ' '
        output_file.write(meu_str + str(int(round(val))))



def ask(query='', bn=Network()):
    tmps = query.split('(')
    tmps[1] = tmps[1].strip(')')
    if tmps[0] == 'P':
        if ' | ' in tmps[1]:  # conditional probability
            tmps = tmps[1].split(' | ')
            ls = tmps[0].split(', ')
            X = {}
            for l in ls:
                t = l.split(' = ')
                X[t[0]] = t[1]
            vars = tmps[1]
            rs = vars.split(', ')
            e = {}
            for r in rs:
                t = r.split(' = ')
                e[t[0]] = t[1]
            p = enumeration_ask(X, e, bn)

        else:  # joint probability
            tmps = tmps[1].split(', ')
            e = {}
            for k in tmps:
                t = k.split(' = ')
                e[t[0]] = t[1]
            p = enumerate_all(bn.vars, e, bn)
        #print str(p) + ', ' + 'round = ' + str(round(p, 2))
        output_line('P', p)

    elif tmps[0] == 'EU':
        tmps = tmps[1].split(' | ')
        if(len(tmps) > 1):
            tmps[0] = tmps[0] + ', ' + tmps[1]
        vars = tmps[0].split(', ')
        e = {}
        for rs in vars:
            rs = rs.split(' = ')
            e[rs[0]] = rs[1]
        eu = eu_enumerate_all(e, bn)
        #print str(eu) + ', ' + 'round = ' + str(int(round(eu)))
        output_line('EU', eu)

    elif tmps[0] == 'MEU':
        tmps = tmps[1].split(' | ')
        x = []
        ls = tmps[0].split(', ')
        for l in ls:
            x.append(l)
        e = {}
        if(len(tmps) == 2):
            rs = tmps[1].split(', ')
            for rs in rs:
                t = rs.split(' = ')
                e[t[0]] = t[1]
        meu_values, meu = meu_enumerate_all(x, e, bn)
        output_line('MEU', meu, meu_values)


def get_tf_values(num, l):
    values = []
    for i in range(l):
        if (num >> i) & 1 == 0:
            values.append('+')
        else:
            values.append('-')
    return values


def enumeration_ask(X={}, e={} , bn=Network()):
    for x in X.keys():
        if e.__contains__(x):
            if e[x] != X[x]:
                return 0.0
            else:
                X.__delitem__(x)



    x_len = len(X)
    array = []
    index = 0
    for i in range(2 ** x_len):
        values = get_tf_values(i, x_len)
        ex = copy.deepcopy(e)
        matched = True
        for j in range(x_len):
            xj = X.keys()[j]
            ex[xj] = values[j]
            if values[j] != X[xj]:
                matched = False
        if matched:
            index = i
        enu = enumerate_all(bn.vars, ex, bn)
        array.append(enu)


    normalize = array[index] / sum(array)

    return normalize




def enumerate_all(vars=[], e={}, bn=Network()):
    if len(vars) == 0:
        return 1.0
    y = vars[0]
    node = bn.get_node(y)
    if y in e.keys():
        return node.p(e[y], e) * enumerate_all(vars[1:], e, bn)
    else:
        ey_true = copy.deepcopy(e)
        ey_true[y] = '+'
        ey_false = copy.deepcopy(e)
        ey_false[y] = '-'
        return node.p('+', e) * enumerate_all(vars[1:], ey_true, bn) + node.p('-', e) * enumerate_all(vars[1:], ey_false, bn)


def eu_enumerate_all(e={}, bn=Network()):
    u_node = bn.utility
    parents = u_node.parents
    sum = 0.0
    for t in u_node.table: # P(parents | e) * Utility(parents)
        X = {}
        for j in range(len(parents)):
            X[parents[j]] = t[j+1]
        sum += enumeration_ask(X, e, bn) * t[0]
    return sum



def meu_enumerate_all(x=[], e={}, bn=Network()):
    x_len = len(x)
    maxium = -INF
    max_values = []
    for i in range(2 ** x_len):
        values = get_tf_values(i, x_len)
        ei = copy.deepcopy(e)
        for j in range(x_len):
            ei[x[j]] = values[j]
        m = eu_enumerate_all(ei, bn)
        if(m > maxium):
            maxium = m
            max_values = values
    return max_values, maxium













# -----------------------------------------------------
# input

file_name = 'sample01.txt'
#file_name = sys.argv[2]
input_file = open(file_name, 'r')
output_file = open(output_file_name, 'w')

# -----------------------------------------------------
# input queries
queries = []
query = input_file.readline().strip(SEP)
while query != '******':
    queries.append(query)
    query = input_file.readline().strip(SEP)


# -----------------------------------------------------
# input Bayesian Nodes

bn = Network()
query = input_file.readline().strip(SEP)
while query != '':  # while it is not end file
    tmps = query.split(' ')
    name = tmps[0]
    parents = tmps[2:]
    table = []
    decision = False
    for i in range(2 ** len(parents)):
        tmps = []
        tmps = input_file.readline().strip(SEP).split(' ')
        if(tmps[0] == 'decision'):
            decision = True
        else:
            tmps[0] = float(tmps[0])
        table.append(tmps)


    node = Node(name, parents, table)
    if(decision == True): node.type = 'decision'
    bn.add_node(node)

    query = input_file.readline().strip(SEP)  # absorb '***'
    if query != '***':
        break  # now query == '' or '******'
    query = input_file.readline().strip(SEP)

if query == '******':
    tmps = input_file.readline().strip(SEP).strip(' ').split(' ')
    name = 'u_node'
    parents = tmps[2:]
    table = []
    for i in range(2 ** len(parents)):
        tmps = []
        tmps = input_file.readline().strip(SEP).split(' ')
        tmps[0] = float(tmps[0])
        table.append(tmps)


    node = Node(name, parents, table)
    node.type = 'utility'
    bn.utility = node

input_file.close()
# -----------------------------------------------------

first = True
for query in queries:
    if not first:
        output_file.write(SEP)
    first = False
    ask(query, bn)

output_file.close()