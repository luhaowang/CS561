# Author: Jeff Kinne
#
# This file implements the variable enumeration algorithm described in the
# Bayes Network chapter of the Russel/Norvig textbook.
# I have assumed throughout that all the variables are Boolean.  This makes
# the code slightly simpler because there are always only two possible
# values to consider.  


# start reading from the bottom of the file up.


# my debug print function.  if I want debug messages printed, then
# print(args), otherwise do nothing.  this is nice so I can leave my
# debug statements in and just have them print when I want them.
def debugprint(*args):
    pass
    #print(args)


# compute probability that var has the value val.  e are the list of
# variable values we already know, and bn has the conditional probability
# tables.
def Pr(var, val, e, bn):
    parents = bn[var][0]
    debugprint('Pr***', var, val, e, bn, parents)
    if len(parents) == 0:
        truePr = bn[var][1][None]
    else:
        debugprint('   Pr***')
        parentVals = [e[parent] for parent in parents]
        truePr = bn[var][1][tuple(parentVals)]
    if val==True: return truePr
    else: return 1.0-truePr


# QX is a dictionary that have probabilities for different values.  this
# function normalizes so the probabilities all add up to 1.
def normalize(QX):
    total = 0.0
    for val in QX.values():
        total += val
    for key in QX.keys():
        QX[key] /= total
    return QX


# The enumerate-ask function from the textbook that does the variable
# enumeration algorithm to compute probabilities in a Bayesian network.
# Remember this is exponential in the worst case!
#
# Note: in both this function and enumerateAll, I make sure to undo any
# changes to the dictionaries and lists after I am done with recursive
# calls.  This is needed because dictionaries and lists are passed by
# reference in python.  Instead of the undoing, I could use deep copy.
def enumerationAsk(X, e, bn,varss):
    QX = {}
    for xi in [False,True]:
        e[X] = xi
        QX[xi] = enumerateAll(varss,e,bn)
        del e[X]
    #return QX
    return normalize(QX)


# Helper function for enumerateAsk that does the recursive calls,
# essentially following the tree that is in the book.
def enumerateAll(varss, e,bn):
    debugprint('EnumerateAll***', varss, e, bn)
    if len(varss) == 0: return 1.0
    Y = varss.pop()
    if Y in e:
        val = Pr(Y,e[Y],e,bn) * enumerateAll(varss,e,bn)
        varss.append(Y)
        return val
    else:
        total = 0
        e[Y] = True
        total += Pr(Y,True,e,bn) * enumerateAll(varss,e,bn)
        e[Y] = False
        total += Pr(Y,False,e,bn) * enumerateAll(varss,e,bn)
        del e[Y]
        varss.append(Y)
        return total


# put the conditional probability tables for the Bayesian network into
# a dictionary.  The key is a string describing the node.
#
# The value for the key has the information about its parents and the
# conditional probabilities.  It is a list with two things.  The first
# thing is a list of the nodes parents (an empty list if there are no
# parents).  The second thing is the conditional probability table in a
# dictionary; the key to this dictionary is values for the parents, and the
# value is the probability of being True given these values for the parents.
bn = {'Burglary':[[],{None:.001}],
      'Earthquake':[[],{None:.002}],
      'Alarm':[['Burglary','Earthquake'],
               {(False,False):.001,(False,True):.29,
                (True,False):.94,(True,True):.95}],
      'JohnCalls':[['Alarm'],
                   {(False,):.05,(True,):.90}], #note: (False,) is a tuple with just the value False.  (False) would not be, python makes that just False, and that would not be good because the code above assumes it is a tuple.
      'MaryCalls':[['Alarm'],
                   {(False,):.01,(True,):.70}]}

# a list of the variables, starting "from the bottom" of the network.
# in the enumerationAsk algorithm, it will look at the variables from
# the end of this list first.
varss = ['MaryCalls','JohnCalls','Alarm','Burglary','Earthquake']

# call the enumerationAsk function to figure out a probability.
print(enumerationAsk('Burglary',{'JohnCalls':True,'MaryCalls':True},bn,varss))
print(enumerationAsk('Burglary',{},bn,varss))
