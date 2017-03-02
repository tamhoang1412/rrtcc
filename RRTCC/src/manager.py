from application import RTPAplication
from network import Network

'''=========================================================================='''

class Manager:
    def __init__(self):
        self.nodes = {'A': RTPAplication('A'), 'B': RTPAplication('B')}
        self.network = Network(self)

    def get_element_by_address(self, address):
        return self.nodes[str(address)]

    def add_node(self, node):
        self.nodes[node.address] = node
'''=========================================================================='''


