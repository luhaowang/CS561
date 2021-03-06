#   python hw3cs561s16.py -i sample01.txt

import sys
import copy
import re
import collections
import decimal

op_file = open('output.txt', 'w')

true_1 = (True, False)
true_2 = [(True, True), (True, False), (False, True), (False, False)]
true_3 = [(True, True, True), (True, True, False),
          (True, False, True), (True, False, False),
          (False, True, True), (False, True, False),
          (False, False, True), (False, False, False)]



class BNet:
    def __init__(self, fname):
        self.net = collections.OrderedDict()
        # self.net = {}
        self.query = []  # list of tuples
        self.eu = {}
        self.meu = {}

        file_handle = open(fname, "r")

        lines = file_handle.readlines()
        file_handle.close()
        count = 0

        evidence = {}
        input1 = {}

        for line in lines:
            temp_line = line.strip('\n\r')  # simply append query here process later

            if temp_line[0:2] == 'P(':
                self.query.append(temp_line)
                count += 1

            elif temp_line[0:3] == 'EU(':
                self.query.append(temp_line)
                count += 1
                # print 'EU:', temp_line

            elif temp_line[0:4] == 'MEU(':
                self.query.append(temp_line)
                count += 1
                # print 'MEU:', temp_line

            elif temp_line == '******':
                count += 1
                self.parse_network(lines[count:])
                break

    def parse_network(self, lines):
        count = 0

        node_info = []
        for l in lines:
            line = l.strip('\n\r')
            if line == '***' or line == '******':
                self.add_node(node_info)
                node_info = []
            else:
                node_info.append(line)

        if len(node_info) != 0:
            self.add_node(node_info)

    def add_node(self, node_info):
        # print "Adding"
        # print node_info

        if len(node_info) == 2:  # single variable
            if node_info[1].strip() == 'decision':
                self.net[node_info[0].strip()] = {
                    'parents': [],
                    'children': [],
                    'prob': -9,
                    'condprob': {}
                }
            else:

                self.net[node_info[0].strip()] = {
                    'parents': [],
                    'children': [],
                    'prob': float(node_info[1]),
                    'condprob': {}
                }

        else:
            node_list = node_info[0].split()
            node_name = node_list.pop(0).strip()

            parents = node_list[1:]
            # print 'Node Name:', node_name
            # print "Parents", str(parents)

            for p in parents:
                self.net[p]['children'].append(node_name)

            self.net[node_name] = {
                'parents': parents,
                'children': [],
                'prob': -1,
                'condprob': {}
            }

            for cprob in node_info[1:]:
                t_line = cprob.split()
                prob = float(t_line.pop(0).strip())
                truth = t_line
                truth = tuple(True if x == '+' else False for x in truth)
                self.net[node_name]['condprob'][truth] = prob


def custom_round(prob):
    rounded = decimal.Decimal(str(prob)).quantize(decimal.Decimal('.01'))
    return rounded

def write_p(prob):

    final_p = custom_round(prob)
    op_file.write(str(final_p) + '\n')

def write_e(prob):

    final_p = decimal.Decimal(str(prob)).quantize(decimal.Decimal())
    op_file.write(str(final_p) + '\n')


def process_query(q, bnet):
    # print 'Processing Query: '
    # print q
    edict = {}

    cFlag = False
    if q[0:2] == 'P(':
        # print 'P:', q

        match = re.match(r'P\((.*)\|(.*)\)', q)
        if match:
            cFlag = False
            X_list = match.group(1).strip().split()

            # print '\nInside Processing |\n'
            # print X_list

            X = X_list[0].strip()  # get name of predicate
            if X_list[2] == '+':
                edict[X] = True
            else:
                edict[X] = False

            e = match.group(2).strip().split(', ')
            for elem in e:
                t = elem.split()
                # print t
                if t[2] == '+':
                    edict[t[0]] = True
                else:
                    edict[t[0]] = False
            # print 'X', X
            # print edict
            evidence = copy.deepcopy(edict)
            # Ask here

            prob = enumeration_ask(bnet, X, evidence, cFlag)
            print 'prob,', prob
            if edict[X]:
                result = prob[0]
                write_p(result)
            else:
                result = prob[1]
                write_p(result)
            # print 'FINAL RESULT:', result
            return result

        else:
            # result = 1.0
            cFlag = True
            input_X = collections.OrderedDict()

            match = re.match(r'P\((.*)\)', q)
            X_list = match.group(1).split(', ')

            # print '\nInside Else Processing ,:',
            # print X_list

            for y in X_list:
                t = y.split()
                # print y
                X = t[0]
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
                edict = copy.deepcopy(input_X)
                # print 'X:', input_X
                # print 'E:', edict

            for x in input_X:
                evidence = copy.deepcopy(edict)
                if x in evidence:
                    evidence.pop(x)

                prob = enumeration_ask(bnet, x, evidence, cFlag)

                if edict[x]:
                    result = prob[0]
                    write_p(result)
                else:
                    result = prob[1]
                    write_p(result)
                # print 'FINAL RESULT:', result

                break
            # print 'prob,', prob

            return result

    elif q[0:3] == 'EU(':
        input1 = collections.OrderedDict()
        input_X = collections.OrderedDict()

        print '_______________________________________________________\nEU:', q

        match = re.match(r'EU\((.*)\|(.*)\)', q)
        if match:
            cFlag = False
            X_list = match.group(1).strip().split()
            X = X_list[0].strip()  # get name of predicate
            if X_list[2] == '+':
                input_X[X] = True
            else:
                input_X[X] = False

            e = match.group(2).strip().split(', ')

            for elem in e:
                t = elem.split()
                # print t
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
        else:
            cFlag = True
            input_X = collections.OrderedDict()

            match = re.match(r'EU\((.*)\)', q)
            X_list = match.group(1).split(', ')

            # print '\nInside Else Processing ,:',
            # print X_list

            for y in X_list:
                t = y.split()
                # print y
                X = t[0]
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False
                    # edict = copy.deepcopy(input_X)
        allUtility = []
        for util in bnet['utility']['parents']:
            # print bnet['utility']['parents']
            if bnet[util]['prob'] != -9:
                # print util
                # print bnet[util]['prob']
                Q = enumeration_ask(bnet, util, input_X, cFlag)
                # print util
                # print input_X
                # print Q
            else:
                # print util
                # print bnet[util]['prob']
                if input_X[util]:
                    Q = [1, 0]
                else:
                    Q = [0, 1]
            allUtility.append(Q)
        dec_eu = calc_utility(allUtility, bnet['utility']['condprob'])
        # final_eu = custom_round(dec_eu)
        write_e(dec_eu)
        print dec_eu,'\n________________________________________________'
        return dec_eu

    elif q[0:4] == 'MEU(':
        print 'MEU:', q
        input_X = collections.OrderedDict()
        cFlag = False
        fin = -9999999999999999.99999
        match = re.match(r'MEU\((.*)\|(.*)\)', q)
        if match:
            cFlag = False

            X_list = match.group(1).strip().split()
            X = X_list[0].strip()  # get name of predicate

            e = match.group(2).strip().split(', ')

            for elem in e:
                t = elem.split()
                # print t
                if t[2] == '+':
                    input_X[t[0]] = True
                else:
                    input_X[t[0]] = False

        else:
            cFlag = True
            match = re.match(r'MEU\((.*)\)', q)

            X_list = match.group(1).split(', ')

        if len(X_list) == 1:
            MEU = {}

            for t_val in range(len(true_1)):
                input_X[X_list[0]] = true_1[t_val]
                MEU[calc_expected_util(input_X, bnet, cFlag)] = true_1[t_val]

            for i in MEU:
                if fin < i:
                    fin = i

            print MEU

            # print ' '.join(MEU[fin]), fin
            write_m(MEU)
            return
        elif len(X_list) == 2:
            MEU = {}

            for t_val in range(len(true_2)):
                input_X[X_list[0]] = true_2[t_val][0]
                input_X[X_list[1]] = true_2[t_val][1]
                MEU[calc_expected_util(input_X, bnet, cFlag)] = true_2[t_val]

            for i in MEU:
                if fin < i:
                    fin = i
            # print ' '.join(MEU[fin]), fin
            print MEU
            write_m(MEU)
            return

        else:
            MEU = {}

            for t_val in range(len(true_3)):
                input_X[X_list[0]] = true_3[t_val][0]
                input_X[X_list[1]] = true_3[t_val][1]
                input_X[X_list[2]] = true_3[t_val][2]
                MEU[calc_expected_util(input_X, bnet, cFlag)] = true_3[t_val]

            for i in MEU:
                if fin < i:
                    fin = i
            # print ' '.join(MEU[fin]), fin
            print MEU
            write_m(MEU)

            return

def write_m(MEU):
    max_key =  max(MEU.keys())
    final_m = decimal.Decimal(str(max_key)).quantize(decimal.Decimal())
    if isinstance(MEU[max_key], bool):
        temp_str = '+ ' if MEU[max_key] else '- '
    else:
        plus_minus = ['+ ' if x else '- ' for x in MEU[max_key]]
        temp_str = ''.join(map(str, plus_minus))

    op_file.write(str(temp_str) + str(final_m) + '\n')
    # if MEU[max_key]:

    # else:
    #     final_m = decimal.Decimal(str(max_key)).quantize(decimal.Decimal())
    #     op_file.write('- ' + str(final_m) + '\n')

def calc_expected_util(input_X, bnet, cFlag):

    allUtility = []
    for util in bnet['utility']['parents']:
        # print bnet['utility']['parents']
        if bnet[util]['prob'] != -9:
            # print util
            # print bnet[util]['prob']
            Q = enumeration_ask(bnet, util, input_X, cFlag)
            # print util
            # print input_X
            # print Q
        else:
            # print util
            # print bnet[util]['prob']
            if input_X[util]:
                Q = [1, 0]
            else:
                Q = [0, 1]
        allUtility.append(Q)
    return calc_utility(allUtility, bnet['utility']['condprob'])

def calc_utility(allUtility, cond_prob):
    # print '\n\nINSIDE CALC UTIL'
    sum = 0
    for row in cond_prob:
        # print 'Row'
        # print row
        prob = cond_prob[row]
        # print 'Prob'
        # print prob
        for x in range(len(row)):
            # print 'all util&&&&&&&'
            # print allUtility
            if row[x]:
                prob *= allUtility[x][0]
            else:
                prob *= allUtility[x][1]
        sum += prob
    # print '\n\nExit CALC UTIL'
    return sum


def normalize(Q):
    return [x * 1 / (sum(Q)) for x in Q]


def get_vars(bnet, X):
    variables = []
    for key in bnet:
        if bnet[key]['prob'] == -9 or key == 'utility':
            continue
        variables.append(key)
    return variables


def enumeration_ask(bnet, X, e, cFlag):
    dist = []

    # print '\n\nInside ASK'
    # print X
    # print e

    Q = [0, 0]
    for x_val in [True, False]:
        ev = copy.deepcopy(e)
        if x_val:

            ev[X] = x_val
            Q[0] = enumerate_all(get_vars(bnet, X), ev, bnet)
        else:
            ev[X] = x_val
            Q[1] = enumerate_all(get_vars(bnet, X), ev, bnet)
    if cFlag:
        return Q
    # normalize(Q)
    return normalize(Q)


def enumerate_all(var, e, bnet):
    # print '\n\nInside ALL'
    # print var
    # print e
    if not var:  # if empty object returned
        return 1.0
    Y = var[0]
    if Y in e:
        return calc_prob(Y, e, bnet) * enumerate_all(var[1:], e, bnet)
    else:
        sigma = []
        tmp_e = copy.deepcopy(e)
        for y_val in [True, False]:
            tmp_e[Y] = y_val
            sigma.append(calc_prob(Y, tmp_e, bnet) * enumerate_all(var[1:], tmp_e, bnet))
        return sum(sigma)


def calc_prob(Y, e, bnet):
    prob_result = 0.0
    # print '\n\nCalulating PROB'
    # print 'Y:', Y
    # print 'E:', e

    if bnet[Y]['prob'] != -1 and bnet[Y]['prob'] != -9:
        # print 'Inside Normal Prob'
        if e[Y]:

            prob_result = bnet[Y]['prob']
        else:
            prob_result = 1 - bnet[Y]['prob']
            # print bnet[Y]['prob']
    else:
        #   get the value of parents of Y
        # print bnet[Y]['parents']
        # print e
        # for p in bnet[Y]['parents']:
        #     print p
        #     print e[p]
        par_val = tuple(e[p] for p in bnet[Y]['parents'])

        if e[Y]:
            prob_result = bnet[Y]['condprob'][par_val]
        else:
            prob_result = 1 - bnet[Y]['condprob'][par_val]
    # print prob_result
    # print 'End PROB\n\n'
    return prob_result


def main():
    #file_name = sys.argv[2]
    file_name = "sample01.txt"
    Network = BNet(file_name)
    print '\n\n FINAL BAYESEAN NET'
    print Network.net
    # print '_____________________________________________________________________\nQUERIES'
    # print Network.query

    for q in Network.query:
        print 'Processing '
        print q
        process_query(q, Network.net)
        # for k in Network.net



    op_file.close()

    f = open('output.txt', 'r')

    lines = f.readlines()
    f.close()
    write = open('output.txt', 'w')
    write.writelines([item for item in lines[:-1]])
    item = lines[-1].rstrip()
    write.write(item)
    write.close()



if __name__ == '__main__':
    #   python hw3cs561s16.py -i sample01.txt
    main()