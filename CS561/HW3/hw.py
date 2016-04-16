import sys, getopt
import itertools

from decimal import *


def main():
    input_file_name = 'sample02.txt'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:")
    except getopt.GetoptError:
        print 'Unexpected argument.'
        print 'Expected invocation in the form "python hw3cs561s16.py -i inputFile"'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            input_file_name = arg

    with open(input_file_name, 'r') as input_file, open("output.txt", 'w') as output_file:
        queries = []
        nodes = {}

        node_lines = []

        def create_node_and_clear_lines():
            node = parse_node(node_lines)
            nodes[node.name] = node
            del node_lines[:]

        # 1 is parsing query lines
        # 2 is parsing bayesian nodes
        # 3 is parsing utility nodes
        parsing_method = 1

        parsing_utility_node = False

        for line in input_file:
            line = line.strip()

            if line == "******":
                parsing_method += 1
                continue

            if parsing_method == 1:
                if line.startswith('P'):
                    query_type = QueryType.PROB
                elif line.startswith('EU'):
                    query_type = QueryType.EU
                else:
                    query_type = QueryType.MEU

                open_paren_index = line.find('(')
                inner_part = line[open_paren_index + 1: -1]
                parts = inner_part.split(" | ")
                query_vars_part = parts[0]
                query_vars, query_vars_assignment = parse_vars(query_vars_part)
                if len(parts) is 2:
                    evidence_vars, evidence_assignment = parse_vars(parts[1])
                else:
                    evidence_assignment = {}

                print query_type, query_vars_assignment, evidence_assignment

                queries.append(Query(query_type, query_vars, query_vars_assignment, evidence_assignment))

            elif parsing_method == 2:
                if line == "***":
                    create_node_and_clear_lines()
                else:
                    node_lines.append(line)

            elif parsing_method == 3:
                if not parsing_utility_node:
                    create_node_and_clear_lines()
                    parsing_utility_node = True
                node_lines.append(line)

        # Parse last remaining bayesian network node.
        create_node_and_clear_lines()

        for name in nodes:
            print
            print str(nodes[name])

        print
        for query in queries:
            if query.query_type == QueryType.PROB:
                print compute_probability(query, nodes).quantize(Decimal('0.01'))
            elif query.query_type == QueryType.EU:
                decision_vars = query.query_vars
                assignment = tuple(map(lambda v: query.query_assignments[v], decision_vars))
                print compute_utility(decision_vars, assignment, query.evidence_assignment, nodes)
            elif query.query_type == QueryType.MEU:
                decision_vars = query.query_vars
                num_decision_vars = len(decision_vars)

                best_assignment = None
                highest_utility = Decimal('-Infinity')

                for assignment in generate_assignments(num_decision_vars):
                    utility = compute_utility(decision_vars, assignment, query.evidence_assignment, nodes)
                    if utility > highest_utility:
                        best_assignment = assignment
                        highest_utility = utility
                print best_assignment, highest_utility


def compute_utility(decision_vars, assignment, evidence, nodes):
    evidence = evidence.copy()

    for var, i in zip(decision_vars, xrange(len(decision_vars))):
        evidence[var] = assignment[i]

    utility_node = nodes["utility"]
    parents = utility_node.parents
    unassigned_parents = [p for p in parents if p not in evidence]
    parent_query = Query(QueryType.PROB, parents, {}, evidence)
    parent_distribution = compute_probability_distribution(parent_query, nodes)

    total = sum(parent_distribution)

    utility = Decimal(0.0)
    # We only want to iterate over the subset of assignments where the parent nodes of the utility node are NOT
    # already known (i.e., not supplied in evidence). This is so we do not double-count them.
    for assignment in generate_assignments(len(unassigned_parents)):
        full_assignment = []
        i = 0
        for p in parents:
            if p in unassigned_parents:
                full_assignment.append(assignment[i])
                i += 1
            else:
                full_assignment.append(evidence[p])

        tuple_assignment = tuple(full_assignment)
        parent_prob = parent_distribution[assignment_to_index(assignment)]/total
        utility += utility_node.utility(tuple_assignment) * parent_prob
    return utility


def compute_probability(query, nodes):
    distribution = compute_probability_distribution(query, nodes)
    return normalize(distribution, query)


def compute_probability_distribution(query, nodes):
    print "query: \t"
    print "\t ", query.query_vars
    print "nodes: \t"
    print "\t", nodes
    unassigned_query_vars = [v for v in query.query_vars if v not in query.evidence_assignment]
    num_query_vars = len(unassigned_query_vars)
    query_var_assignments = generate_assignments(num_query_vars)
    distribution = [None] * 2**num_query_vars

    evidence = query.evidence_assignment.copy()
    for assignment in query_var_assignments:
        index = assignment_to_index(assignment)
        for query_var, i in zip(unassigned_query_vars, xrange(num_query_vars)):
            evidence[query_var] = assignment[i]
        distribution[index] = enumeration_ask(evidence, nodes)
    return distribution


def normalize(distribution, query):
    total = sum(distribution)
    assignment = tuple(map(lambda v: query.query_assignments[v], query.query_vars))
    return distribution[assignment_to_index(assignment)]/total


def enumeration_ask(evidence, network):
    print "evidence:"
    print evidence
    return enumerate_all(network.keys(), network, evidence)


def enumerate_all(network_vars, network, evidence):
    evidence = evidence.copy()

    if len(network_vars) == 0:
        return Decimal(1.0)

    first, rest = network_vars[0], network_vars[1:]
    node = network[first]

    # We can skip utility nodes (since they don't affect probability) and decision nodes (since they are in evidence).
    if not isinstance(node, EventNode):
        return enumerate_all(rest, network, evidence)

    parents = node.parents
    unassigned_parents = [p for p in parents if p not in evidence]
    num_unassigned = len(unassigned_parents)

    if num_unassigned is not 0:
        parents_assignment = generate_assignments(num_unassigned)
        total = Decimal(0.0)
        for assignment in parents_assignment:
            for parent, val in zip(unassigned_parents, assignment):
                evidence[parent] = val

            if first in evidence:
                possible_child_vals = [evidence[first]]
            else:
                possible_child_vals = [True, False]

            for val in possible_child_vals:
                subevidence = evidence.copy()
                subevidence[first] = val
                total += node.probability(val, subevidence) * enumerate_all(rest, network, subevidence)
        return total
    else:
        if first in evidence:
            possible_child_vals = [evidence[first]]
        else:
            possible_child_vals = [True, False]

        total = Decimal(0.0)
        for val in possible_child_vals:
                subevidence = evidence.copy()
                subevidence[first] = val
                total += node.probability(val, subevidence) * enumerate_all(rest, network, subevidence)
        return total


def extract_parents(node, evidence):
    parents = {}
    for parent in node.parents:
        if parent in evidence:
            parents[parent] = evidence[parent]
    return parents


# Computes an index by treating a tuple of assignments as a binary number.
# True is represented as a 1 bit, and False as a 0 bit.
def assignment_to_index(assignment):
    index = 0
    num_vars = len(assignment)
    for var, i in zip(assignment, xrange(num_vars)):
        if var:
            index += 2**(num_vars-1-i)
    return index


# Returns a list of tuples corresponding to assignments for the given number of variables.
def generate_assignments(num_vars):
    return itertools.product([True, False], repeat=num_vars)


# Parses a string in the form Var1, Var2 = + into a tuple consisting of two elements.
# The first element is a canonical ordering of the variables.
# The second element map of variable names and value assignment.
# If the variable has no assignment, then it will have a None assignment value in the tuple.
def parse_vars(s):
    s = s.strip()
    ordered_vars = []
    variables = {}
    vars_and_assignments = s.split(", ")
    for var_and_assignment in vars_and_assignments:
        var_and_assignment = var_and_assignment.split(" = ")
        name = var_and_assignment[0]
        ordered_vars.append(name)

        # No assignment
        if len(var_and_assignment) == 1:
            assignment = None
        elif var_and_assignment[1] == '+':
            assignment = True
        else:
            assignment = False

        variables[name] = assignment
    return ordered_vars, variables


# Parses a set of lines into a bunch of nodes.
def parse_node(lines):
    name, parents = parse_name_and_parents(lines[0])
    num_parents = 0 if parents is None else len(parents)

    if lines[1] == "decision":
        return DecisionNode(name, parents)
    else:
        values = parse_node_values(lines[1:], num_parents)

        if name == "utility":
            return UtilityNode(name, parents, values)
        else:
            return EventNode(name, parents, values)


def parse_name_and_parents(line):
    if " | " not in line:
        name = line
        parents = []
    else:
        name, parents = line.split(" | ")
        parents = parents.split(" ")
    return name, parents


# Parses a list of probabilities or into an array of 2^n decimal values
# where n is the number of parents for the node.
def parse_node_values(lines, num_parents):
    values = [None] * 2**num_parents
    for line in lines:
        value_and_parent_assignments = line.split(" ")
        value = Decimal(value_and_parent_assignments[0])

        parent_assignments = value_and_parent_assignments[1:]
        index = 0

        for assignment, i in zip(parent_assignments, xrange(num_parents)):
            if assignment == "+":
                index += 2**(num_parents-1-i)
        values[int(index)] = value
    return values


class QueryType:
    def __init__(self):
        pass

    # Probability Query
    PROB = 1

    # Expected Utility Query
    EU = 2

    # Maximum Expected Utility Query
    MEU = 3


# An object representing a query.
class Query:
    # query_type must be a [QueryType], representing the type of query.
    # query_vars is an ordered list of the variables we are querying about.
    # query_assignments is a map defining the assignment that we are querying.
    # evidence_assignment represents the assignment of variables we condition our probabilities on.
    def __init__(self, query_type, query_vars, query_assignments, evidence_assignment):
        self.query_type = query_type
        self.query_vars = query_vars
        self.query_assignments = query_assignments
        self.evidence_assignment = evidence_assignment


class NodeType:
    def __init__(self):
        pass
    EVENT = 1
    DECISION = 2
    UTILITY = 3


class Node:
    # Node type signifies the type of node.
    # Name is the name of the current node.
    # Parents is the name of the node's parents.
    def __init__(self, node_type, name, parents):
        self.node_type = node_type
        self.name = name
        self.parents = parents

    def __str__(self):
        ret = self.name
        if len(self.parents) != 0:
            ret += " |"
            for p in self.parents:
                ret += " " + p
        return ret


class EventNode(Node):
    def __init__(self, name, parents, probabilities):
        Node.__init__(self, NodeType.EVENT, name, parents)
        self.probabilities = probabilities

    # Returns the probability of a variable having a given value based upon evidence.
    def probability(self, value, evidence):
        index = assignment_to_index(tuple(map(lambda p: evidence[p], self.parents)))
        if value:
            return self.probabilities[index]
        else:
            return 1-self.probabilities[index]

    def __str__(self):
        ret = Node.__str__(self)
        ret += "\n"
        ret += ",".join(map(lambda d: str(d), self.probabilities))
        return ret


class DecisionNode(Node):
    def __init__(self, name, parents):
        Node.__init__(self, NodeType.DECISION, name, parents)

    def __str__(self):
        ret = Node.__str__(self)
        ret += "\n" + "decision"
        return ret


class UtilityNode(Node):
    def __init__(self, name, parents, values):
        Node.__init__(self, NodeType.UTILITY, name, parents)
        self.values = values

    def __str__(self):
        ret = Node.__str__(self)
        ret += "\n"
        ret += ",".join(map(lambda d: str(d), self.values))
        return ret

    # Returns the utility value of the node based upon a tuple of parent assignments.
    def utility(self, parent_assignment):
        index = assignment_to_index(parent_assignment)
        return self.values[index]

if __name__ == "__main__":
    main()