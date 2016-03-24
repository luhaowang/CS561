#!/usr/bin/python

import sys
import re
import copy

OUTPUT = False
DEBUG2 = True

class KBase:
	''' The Knowledge base class.
	    Contains all DS & methods to build & use a full KB.
		It will contain a List of sentences.
		It will contain a inverted index on those sentences, so that we can identify unifyable sentences fast.
		Also contains a method: fetch_rules_for_goal(sentence)
	'''
	def __init__(self):
		''' constructor initializing the members '''
		self.KB = [] 
		self.sentence_index = dict([("1", dict()),("2", dict()),("3", dict())])
	def append_kb(self,sentence):
		''' add the given sentence at the end of KB'''
		self.insert_at(sentence,len(self.KB))

	def insert_at(self,sentence, index):
		''' insert the sentence at given index in KB '''
		sentence_object = Sentence(sentence)
		self.KB.insert(index, sentence_object)
		target_dict = self.sentence_index[str(sentence_object.RHS.numargs)]
		if(target_dict.get(sentence_object.RHS.name)):
			target_dict[sentence_object.RHS.name].append(index)
		else:
			target_dict[sentence_object.RHS.name] = [index]

	def fetch_rules_for_goal(self,goal):
		''' return list of sentences that can unify with the input predicate'''
		target_dict = self.sentence_index[str(goal.numargs)]
		goal_list = []
		if(target_dict.get(goal.name)):
			index_list = target_dict[goal.name]
			for i in index_list:
				Unifiable = True
				for j in range(3):
					if (is_constant(self.KB[i].RHS.args[j]) and is_constant(goal.args[j]) and (self.KB[i].RHS.args[j]!=goal.args[j])):
						Unifiable = False
				if  Unifiable:
					goal_list.append(self.KB[i])
		return goal_list

	def extend_kb(self,list_sentences):
		''' extend the KB by appending each of the list_sentences '''
		for sentence in list_sentences:
			self.append_kb(sentence)

	def to_string(self):
		''' a helper method to dump the KB in a human readable format '''
		sentence_strings = [] 
		for x in self.KB:
			sentence_strings.append(x.to_string())
		return (sentence_strings, self.sentence_index)

class Sentence:
	''' defines a sentence as a LHS & RHS for Horn clauses.
		
	'''
	horn_pattern = re.compile(r'(.*)=>(.*)')
	lhs_split_pattern = re.compile(r'\&\&')
	def __init__(self,sentence_string):
		self.RHS = None
		self.LHS = [] 
		self.convert_to_sentence(sentence_string)

	def is_atomic(self,sentence_string):
		''' tells you if it is a atomic sentence'''
		if(self.horn_pattern.match(sentence_string)):
			return False 
		else:
			return True

	def split_horn_string(self,sentence_string):
		''' splits string at => into 2 '''
		return self.horn_pattern.match(sentence_string).groups()		

	def make_lhs(self,lhs_sentence_string):
		''' splits the and's & makes a list out of each predicate '''
		lhs_predicates = self.lhs_split_pattern.split(lhs_sentence_string)
		for predicate in lhs_predicates:
			self.LHS.append(Predicate(predicate))


	def convert_to_sentence(self,sentence_string):
		''' convert the string to a sentence & return the sentence'''
		if(self.is_atomic(sentence_string)):
			self.RHS = Predicate(sentence_string)
		else:
			lhs_string,rhs_string = self.split_horn_string(sentence_string)
			self.RHS = Predicate(rhs_string)
			self.make_lhs(lhs_string)

	def to_string(self):
		''' helper class to visualize sentence object '''
		lhs_strings = [] 
		for lhs in self.LHS:
			lhs_strings.append(lhs.to_string())
		rhs_strings = self.RHS.to_string()
		return (lhs_strings, rhs_strings)

class Predicate:
	''' defines the structre of a predicate '''
	one_arg_pattern = re.compile(r"^\s*(\w+)\s*\(\s*(\w+)\s*\)\s*$")
	two_arg_pattern = re.compile(r"^\s*(\w+)\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)\s*$")
	three_arg_pattern = re.compile(r"^\s*(\w+)\s*\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\)\s*$")
	def __init__(self,predicate_string):
		self.name = ""
		self.numargs = 0
		self.arg1 = ""
		self.arg2 = ""
		self.arg3 = ""
		self.args = []
		self.make_predicate(predicate_string)
		self.getargs()

	def make_predicate(self,predicate_string):
		''' given a string, populate the predicate'''
		#print predicate_string
		matching = self.one_arg_pattern.match(predicate_string)
		if(matching):
			self.numargs = 1
			self.name, self.arg1 = matching.groups()
		else:
			matching = self.two_arg_pattern.match(predicate_string)
			if(matching):
				self.numargs = 2
				self.name, self.arg1, self.arg2 = matching.groups()
			else:
				matching = self.three_arg_pattern.match(predicate_string)
				if(matching):
					self.numargs = 3
					self.name, self.arg1, self.arg2,self.arg3 = matching.groups()


	def to_string(self):
		return (self.name,self.numargs,self.arg1,self.arg2,self.arg3)
	
	def getargs(self):
		self.args = []
		self.args.append(self.arg1)
		self.args.append(self.arg2)
		self.args.append(self.arg3)
		return self.args

	def updateargs(self):
		self.arg1 = self.args[0]
		self.arg2 = self.args[1]
		self.arg3 = self.args[2]

def read_input_txt_hw2_file(filename):
	''' Given a input file of assumed format, read & populate the KB'''
	r_file_handle = open(filename,"r") 
	query_strings = r_file_handle.readline().rstrip()
	query_strings_list = query_strings.split(' && ')
	num_sentences = int(r_file_handle.readline().rstrip())
	sentence_string = [] 
	for x in range(0,num_sentences):
		sentence_string.append( r_file_handle.readline().rstrip())
	KB = KBase()
	KB.extend_kb(sentence_string)
	query_list = []
	for query_string in query_strings_list:
		query_list.append(Predicate(query_string))
	return KB,query_list

class BackwardChaining:
	def __init__(self):
		self.varcounter = 0
			
	def unify(self,x,y, theta):
		#print "unify:" + str(x) + " " + str(y)# + " " + str(theta)
		if theta is None:
			return None
		elif equal(x,y):
			return theta
		elif is_var(x):	
			return self.unifyVar(x, y, theta)
		elif is_var(y):
			return self.unifyVar(y, x, theta)
		elif is_predicate(x) and is_predicate(y):
			return self.unify(x.getargs(),y.getargs(), self.unify(x.name, y.name, theta))
		elif is_list(x) and is_list(y):
			return self.unify(x[1:], y[1:], self.unify(x[0], y[0], theta))
		else:
			return None
	
	def unifyVar(self,var,x,theta):
		'''
		 theta : dict  key:variable value: constant value
		'''
		if var in theta:
			return self.unify(theta[var], x, theta)
		elif x in theta:
			return self.unify(var, theta[x], theta)
		thetabak = theta.copy()
		thetabak[var] = x
		return thetabak
	
	def standardize_var(self,lhs,rhs):
		lhs = copy.deepcopy(lhs)
		rhs = copy.deepcopy(rhs)	
		for lhs_predicate in lhs:
			for i in range(lhs_predicate.numargs):
				if is_var(lhs_predicate.args[i]):
					lhs_predicate.args[i] = lhs_predicate.args[i] + str(self.varcounter)
			lhs_predicate.updateargs()
		for i in range(rhs.numargs):
			if is_var(rhs.args[i]):
				rhs.args[i] = rhs.args[i] + str(self.varcounter)
		rhs.updateargs()

		self.varcounter += 1
		return (lhs, rhs)
	
	def fol_bc_ask(self,KB,query):
		''' do backward chaining & return true or false
			This is FOL-BC-ASK
		'''
		if DEBUG2:
			print "Ask:",
			print self.print_predicate(query)
		if OUTPUT:
			write_output_to(output_file_handle, "Ask: " + self.print_predicate(query) )
			write_output_to(output_file_handle,"\n")
		return self.fol_bc_or(KB,query,{})
		
	
	
	def fol_bc_or(self,KB,goal,theta):
		''' return  actual subsitutions'''
		goal_rules = KB.fetch_rules_for_goal(goal)
		count = 0
		for sentence in goal_rules:
			Proved = False
			count +=1
			lhs,rhs = self.standardize_var(sentence.LHS, sentence.RHS)
			if ~is_fact(rhs):
				if count!=1 :
					if DEBUG2:
						print "Ask:",
						print self.print_predicate(goal)
					if OUTPUT:
						write_output_to(output_file_handle, "Ask: " + self.print_predicate(goal) )
						write_output_to(output_file_handle,"\n")
			for theta_or in self.fol_bc_and(KB,lhs,self.unify(rhs,goal,theta)):
				if theta_or is not None:
					if DEBUG2:
						print "True:",
						print self.print_predicate(goal, theta_or)
					if OUTPUT:
						write_output_to(output_file_handle, "True: " + self.print_predicate(goal, theta_or) )
						write_output_to(output_file_handle,"\n")
					Proved = True
				yield theta_or
				
		if len(goal_rules)==0:
			Proved = False
		if DEBUG2:
			if Proved==False:		
				print "False:",
				print self.print_predicate(self.substitude(theta, goal))
		if OUTPUT:
			if Proved==False:	
				write_output_to(output_file_handle, "False: " + self.print_predicate(self.substitude(theta, goal)) )
				write_output_to(output_file_handle,"\n")	
	
	
	def fol_bc_and(self,KB,goals,theta):
		''' return suitable substitutions '''
		if theta == None:
			return 
		else:
			if(len(goals) == 0):
				yield theta
			else:
				first, rest = goals[0],goals[1:]
				if DEBUG2:
					print "Ask:",
					print self.print_predicate(self.substitude(theta, first),theta)
				if OUTPUT:
					write_output_to(output_file_handle, "Ask: " + self.print_predicate(self.substitude(theta, first),theta) )
					write_output_to(output_file_handle,"\n")
				for theta1 in self.fol_bc_or(KB,self.substitude(theta,first),theta):
					for theta2 in self.fol_bc_and(KB,rest,theta1):
						yield theta2
						
	def substitude(self,theta,predicate):
		predicate = copy.deepcopy(predicate)
		needIter = True
		while needIter:
			needIter = False
			for target, substitution in theta.iteritems():
				if predicate.arg1 == target:
					predicate.arg1 = substitution
					needIter = True 
				if predicate.arg2 == target:
					predicate.arg2 = substitution
					needIter = True
				if predicate.arg3 == target:
					predicate.arg3 = substitution
					needIter = True
				predicate.getargs()
		return predicate
	
	def print_predicate(self,p, theta= {}):
		if len(theta)==0:
			str = ""
			str = str + p.name + "("
			predicate = p
			numargs = p.numargs
			for i in range(numargs):
				if is_var(p.args[i]):
					str = str + "_" + ", "
				if is_constant(p.args[i]):
					str = str + p.args[i] + ", "
			str = str.rstrip(', ')
			str +=")"
		else:
			pp = self.substitude(theta, p)
			str = ""
			str = str + pp.name + "("
			predicate = pp
			numargs = pp.numargs
			for i in range(numargs):
				if is_var(pp.args[i]):
					str = str + "_" + ", "
				if is_constant(pp.args[i]):
					str = str + pp.args[i] + ", "
			str = str.rstrip(', ')
			str +=")"
		return str

	def print_predicate_no(self,p):
		str = ""
		str = str + p.name + "("
		predicate = p
		numargs = p.numargs
		for i in range(numargs):
			str = str + p.args[i] + ", "
		str = str.rstrip(', ')
		str +=")"
		return str


def is_var(symbol):
	if isinstance(symbol, str):
		return symbol[0].islower()
	return False

def is_predicate(symbol):
	return isinstance(symbol, Predicate)

def is_fact(symbol):
	if is_predicate(symbol):
		for i in range(symbol.numargs):
			if is_constant(symbol.args[i])==False:
				return False
		return True
	else:
		return False
def is_sentence(symbol):
	return isinstance(symbol, Sentence)

def is_list(symbol):
	return isinstance(symbol, list)

def is_constant(symbol):
	if len(symbol)==0:
		return False
	if isinstance(symbol, str):
		return symbol[0].isupper()
	
def equal(x,y):
	if ((is_var(x) and is_var(y)) or (is_predicate(x) and is_predicate(y)) or (is_list(x) and is_list(y)) or (is_constant(x) and is_constant(y)) or (is_sentence(x) and is_sentence(y))):
		if(is_var(x) and is_var(y)):
			return x == y
		elif (is_predicate(x) and is_predicate(y)):
			return (x.name == y.name and x.arg1 == y.arg1 and x.arg2 == y.arg2 and x.arg3 == y.arg3) 
		elif (is_list(x) and is_list(y)):
			if len(x)!=len(y):
				return False
			for i in range(len(x)):
				if (x[i]!=y[i]):
					return False
			return True
		elif (is_constant(x) and is_constant(y)):
			return str(x)==str(y)
		elif (is_sentence(x) and is_sentence(y)):
			if len(x.RHS)!=len(y.RHS)or len(x.LHS)!=len(y.LHS):
				return False
			else:
				for i in range(len(x.RHS)):
					if(not equal(x.RHS[i], y.RHS[i])):
						return False
					if(not equal(x.LHS[i], y.LHS[i])):
						return False
				return True
				
	else:
		return False
	



def write_output_to(file_handle,strs):
	file_handle.write(strs)

if __name__ == "__main__":
	global output_file_handle
	if DEBUG2:
		Input_file = "sample03.txt"
	if OUTPUT:
		Input_file = str(sys.argv[2])
	Output_file = "output.txt"
	output_file_handle = open(Output_file,"w")
	KB,querylist = read_input_txt_hw2_file(Input_file)
	
	bc = BackwardChaining()
	finalAnswer = True
	for query in querylist:
		x= bc.fol_bc_ask(KB,query)
		try:
			substitutionList = next(x)
		except StopIteration:
			finalAnswer = False
	if finalAnswer:
		if DEBUG2:
			print True
		if OUTPUT:
			write_output_to(output_file_handle,"True")
	else:
		if DEBUG2:
			print False
		if OUTPUT:
			write_output_to(output_file_handle,"False")
	output_file_handle.close()
	
