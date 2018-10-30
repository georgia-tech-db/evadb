
# The query optimizer decide how to label the data points
# Load the series of queries from a txt file?

import socket
from time import sleep
import threading
import constants
from itertools import product

class QueryOptimizer:


  def __init__(self, ip_str="127.0.0.1"):
    self.ip_str = ip_str
    #self.startSocket()
    self.operators = ["=", "!=", "<", "<=", ">", ">="]
    self.separators = ["||", "&&"]



  def startSocket(self):
    thread = threading.Thread(target=self.inputQueriesFromSocket)
    thread.daemon = True
    thread.start()
    while True:
      input = raw_input('Type in your query in the form of __label__ > __number__\n')
      self.parseInput(input)


  def parseInput(self, input):
    """
    TODO: Need to provide query formats that can be used
    :param input: string to be parsed
    :return: something that the Load() class can understand
    """
    pass


  def inputQueriesFromTxt(self, input_path):
    """
    TODO: Read the file line by line, use self.parseInput to give back commands
    :param input_path: full directory + file name
    :return: method of training the pps
    """
    pass


  def inputQueriesFromSocket(self):
    sock = socket.socket()
    sock.bind(self.ip_str, 123)
    sock.listen(3)
    print "Waiting on connection"
    conn = sock.accept()
    print "Client connected"
    while True:
      m = conn[0].recv(4096)
      conn[0].send(m[::-1])

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()

  def parseQuery(self, query):
    """
    Each sub query will be a list
    There will be a separator in between
    :param query:
    :return:
    """
    query_parsed = []
    query_subs = [query.split(" ")]
    for query_sub in query_subs:
      assert(any(operator in self.operators for operator in query_sub))
      for operator in self.operators:
        query_sub_list = query_sub.split(operator)
        if type(query_sub_list) is list and \
          len(query_sub_list) > 1:
          query_parsed.append(query_sub_list)
          break
    return query_parsed


  def logic_reverse(self, str):
    if str == "=":
      return "!="
    elif str == "!=":
      return "="
    elif str == ">":
      return "<="
    elif str == ">=":
      return "<"
    elif str == "<":
      return ">="
    elif str == "<=":
      return ">"


  def wrangler(self, query, label_desc):
    """
    import itertools
    iterables = [ [1,2,3,4], [88,99], ['a','b'] ]
    for t in itertools.product(*iterables):
      print t

    Different types of checks are performed
    1. not equals check (f(C) != v)
    2. comparison check (f(C) > v -> f(C) > t, for all t <= v)
    3. Range check (v1 <= f(C) <= v2) - special type of comparison check
    4. No-predicates = when column in finite and discrete, it can still benefit
      ex) 1 <=> type = car U type = truck U type = SUV
    :return: transformed query
    """
    #TODO: Need to implement range check
    query_sorted = sorted(query)
    query_parsed = self.parseQuery(query_sorted)
    query_transformed = []
    equivalences = []

    for query_sub_list in query_parsed:
      subject = query_sub_list[0]
      operator = query_sub_list[1]
      object = query_sub_list[2]

      assert(subject in label_desc) # Label should be in label description dictionary
      l_desc = label_desc[subject]
      if l_desc[0] == constants.DISCRETE:
        equivalence = [query_sub_list]
        assert(operator == "=" or operator == "!=")
        alternate_string = ""
        for category in l_desc:
          if category != object:
            alternate_string += subject + self.logic_reverse(operator) + category + " && "
        alternate_string = alternate_string[:-len(" && ")] #must strip the last ' || '
        equivalence.append(self.parseQuery(alternate_string))

      elif l_desc[0] == constants.CONTINUOUS:
        #TODO: Need to compute the equivalence classes for continuous instances

        equivalence = [query_sub_list]
        assert(operator == "=" or operator == "!=" or operator == "<"
               or operator == "<=" or operator == ">" or operator == ">=")
        alternate_string = ""
        if operator == "!=":
          alternate_string += subject + ">" + object + " && " + subject + "<" + object
          equivalence.append(self.parseQuery(alternate_string))
        if operator == "<" or operator == "<=":
          object_num = eval(object)
          for number in l_desc[1]:
            if number > object_num:
              alternate_string += subject + operator + str(number)
              equivalence.append(self.parseQuery(alternate_string))
        if operator == ">" or operator == ">=":
          object_num = eval(object)
          for number in l_desc[1]:
            if number < object_num:
              alternate_string += subject + operator + str(number)
              equivalence.append(self.parseQuery(alternate_string))


      equivalences.append(equivalence)

    possible_queries = product(*equivalences)
    for q in possible_queries:
      query_transformed.append( q )

    return query_transformed



  def compute_expression(self, query_transformed, pp_list, k):
    """
    Clarification: "full_label_name": ex) "speed>50"
                   "label": ex) speed
                   "full_label_name" must be a PP name

    def QueryOptimizer(P, {trained PPs}):
      P = wrangler(P)
      {E} = compute_expressions(P,{trained PP},k)        #k is a fixed constant which limits number of individual PPs
      in the final expression
      for E in {E}:
      Explore_PP_accuracy_budget(E)  # Paper says dynamic program
      Explore_PP_Orderings(E)        #if k is small, any number of orders can be explored
      Compute_cost_vs_red_rate(E)   #arithmetic over individual c,a and r[a] numbers
      return E_with_max_c/r


    1. p ^ (P/p) -> PPp
    2. PPp^q -> PPp ^ PPq
    3. PPpvq -> PPp v PPq
    4. p^(P/p) -> ~PP~q
    :param query_transformed:
    :param pp_list:
    :param k:
    :return:
    """
    pass











  def run(self, query, pp_list, pp_stats, label_desc, k = 3):
    """

    :param query: query of interest ex) TRAF-20
    :param pp_list: list of pp_descriptions - queries that are available
    :param pp_stats: this will be dictionary where keys are "pca/ddn",
                     it will have statistics saved which are R (reduction_rate), C (cost_to_train), A (accuracy)
    :param k: number of different PPs that are in any expression E
    :return: selected PPs to use for reduction
    """
    query_transformed = self.wrangler(query, label_desc)
    #query_transformed is a comprehensive list of transformed queries
    return self.compute_expressions(query_transformed, pp_list, pp_stats, k)


if __name__ == "__main__":
  query_list = ["t=suv", "s>60",
                "c=white", "c!=white", "o=pt211", "c=white && t=suv",
                "s>60 && s<65", "t=sedan || t=truck", "i=pt335 && o=pt211",
                "t=suv && c!=white", "c=white && t!=suv && t!=van",
                "t=van && s>60 && s<65", "c!=white && (t=sedan || t=truck)",
                "i=pt335 && o!=pt211 && o!=pt208", "t=van && i=pt335 && o=pt211",
                "t!=sedan && c!=black && c!=silver && t!=truck",
                "t=van && s>60 && s<65 && o=pt211", "t!=suv && t!=van && c!=red && t!=white",
                "(i=pt335 || i=pt342) && o!=pt211 && o!=pt208",
                "i=pt335 && o=pt211 && t=van && c=red"]

  query_list_short = ["t=van && s>60 && s<65 && o=pt211"]

  synthetic_pp_list = ["t=suv", "t=van", "t=sedan", "t=truck",
                       "c=red", "c=white", "c=black", "c=silver",
                       "s>50", "s>60", "s>65", "s>70",
                       "i=pt335", "i=pt211", "i=pt342", "i=pt208",
                       "o=pt335", "o=pt211", "o=pt342", "o=pt208"]

  synthetic_pp_stats = { "none/dnn": {"R": 0.1, "C": 0.1, "A": 0.9},
                         "pca/dnn": {"R": 0.2, "C": 0.15, "A": 0.92},
                         "none/kde": {"R": 0.15, "C": 0.05, "A": 0.95} }

  label_desc = {"t": [constants.DISCRETE, ["sedan", "suv", "truck", "van"]],
                "s": [constants.CONTINUOUS, [50, 60, 65, 70]],
                "i": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]],
                "o": [constants.DISCRETE, ["pt335", "pt342", "pt211", "pt208"]]}

  qo = QueryOptimizer()
  for query in query_list_short:
    qo.run(query, synthetic_pp_list, synthetic_pp_stats, label_desc)



