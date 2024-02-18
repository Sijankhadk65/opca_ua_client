from asyncua import Client
from models import NodeTree


async def list_all_nodes(server_endpoint):
    # Create a client and connect to the OPC UA server
    client = Client(url=server_endpoint)
    await client.connect()

    try:
        # Browse the server's address space to discover available nodes
        root = client.get_root_node()
        var = await print_nodes_recursive(root)
    finally:
        # Disconnect the client when done
        await client.disconnect()
    return var


async def print_nodes_recursive(node):
    nodes = []
    node_tree = NodeTree()
    node_tree.set_id(node.nodeid.Identifier)

    # Recursively print children
    child_nodes_num = await node.get_children()
    if child_nodes_num != 0:
        for child_node in await node.get_children():
            nodes.append(await print_nodes_recursive(child_node))
    node_tree.set_nodes(nodes)
    return node_tree


async def server_main():
    server_endpoint = "opc.tcp://192.168.1.100:4840/freeopcua/server/"
    var = await list_all_nodes(server_endpoint)
    return var
