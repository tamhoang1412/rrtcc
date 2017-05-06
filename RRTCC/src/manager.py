from application import RTPAplication
from network import Network

'''=========================================================================='''

class Manager:
    def __init__(self, network_coef):
        self.nodes = {'A': RTPAplication('A'), 'B': RTPAplication('B')}
        self.network = Network(self, network_coef)

    def get_element_by_address(self, address):
        return self.nodes[str(address)]

    def add_node(self, node):
        self.nodes[node.address] = node
'''=========================================================================='''


