def build_hierarchical_tree(nodes_list):
    """
    Converts a flat node list like:

    [
        {"id": 0, "label": "E", "children": [1, 2]},
        ...
    ]

    into a nested JSON structure for D3.js.
    """

    if not nodes_list:
        return {}

    node_map = {
        node['id']: node
        for node in nodes_list
    }

    # Find root node
    child_ids = set()

    for node in nodes_list:
        child_ids.update(
            node.get("children", [])
        )

    root_nodes = [
        node
        for node in nodes_list
        if node['id'] not in child_ids
    ]

    def build_tree(node_id):

        node = node_map.get(node_id)

        if not node:
            return None

        tree_node = {
            "name": node["label"]
        }

        children = []

        for child_id in node.get("children", []):

            child_tree = build_tree(child_id)

            if child_tree:
                children.append(child_tree)

        if children:
            tree_node["children"] = children

        return tree_node

    # Use last detected root
    if root_nodes:
        return build_tree(root_nodes[-1]['id'])

    return {}