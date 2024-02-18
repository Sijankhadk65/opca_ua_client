class NodeTree:
    def __init__(self):
        self._id = ""
        self._nodes = []
        pass

    def set_id(self, node_id):
        self._id = node_id

    def get_id(self) -> str:
        return self._id

    def set_nodes(self, branches):
        self._nodes = branches

    def get_nodes(self) -> []:
        return self._nodes

    def print_tree(self):
        print(f'Identifier: {self._id}')
        print('Nodes:')
        if self._nodes:
            for node in self._nodes:
                node.print_tree()
        else:
            print("[]")

