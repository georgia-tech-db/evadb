
# The query optimizer decide how to label the data points
# Load the series of queries from a txt file?

import socket
from time import sleep
import threading

class QueryOptimizer:


  def __init__(self, ip_str="127.0.0.1"):
    self.ip_str = ip_str
    #self.startSocket()


  def wrangler(self):
    """
    Different types of checks are performed
    1. not equals check (f(C) != v)
    2. comparison check (f(C) > v -> f(C) > t, for all t <= v
    3. Range check (v1 <= f(C) <= v2) - special type of comparison check
    4. No-predicates = when column in finite and discrete, it can still benefit
      ex) 1 <=> type = car U type = truck U type = SUV
    :return:
    """




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


  def selectFilterModels(self, trained_result):
    """
    TODO: select the filters based on c / r value where c refers to computation time, r refers to reduction rate
    :param trained_result: dict : {"label_name": {"model_name": {"accuracy": ___, "reduction_rate": ___}}}
    :return: dict : {"label_name": "model_name"}
    """
    pass


  def selectPPs(self, query_parsed):
    """

    :param query_parsed: format that is easy for the computer to understand ex) {"label": ___, "op": ___, "num": ___}
    :return: list : ["full_label_name"]

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
    """
    pass



