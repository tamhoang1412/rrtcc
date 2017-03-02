from application import application

'''=========================================================================='''

class manager:
    def __init__(self):
        self.nodes = {'A': application('A'), 'B': application('B')}


    def get_element_by_address(self, address):
        return self.nodes[str(address)]

'''=========================================================================='''


