class NodeTree:
    def __init__(self):
        self._id = ""
        self._ns = 0
        self._nodes = []
        pass

    def set_id(self, node_id):
        self._id = node_id

    def get_id(self) -> str:
        return self._id

    def set_ns(self, namespace):
        self._ns = namespace

    def get_ns(self) -> int:
        return self._ns

    def set_nodes(self, branches):
        self._nodes = branches

    def get_nodes(self) -> []:
        return self._nodes

    # def __str__(self):
    #     # String representation of the current node
    #     result = f"NodeTree ID: {self._id}, NodeTree Namespace: {self._ns}"
    #     # String representation of nested nodes
    #     if self._nodes:
    #         result += "\n  Subtrees:\n"
    #         for node in self._nodes:
    #             result += f"    {node}\n"
    #
    #     return result

