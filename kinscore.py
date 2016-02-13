import csv
import re
import sys

import networkx as nx


INPUT_FILE = 'input.csv'
OUTPUT_FILE = 'output.csv'


def load_data(input_file):
    with open(input_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        input_data = [row for row in csvreader]
        return input_data


def save_edge_list(data):
    with open('data/edge_list.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(('Child', 'Parent'))
        for row in data:
            csvwriter.writerow((row[1], row[2]))


def save_synbreed_data(network, node_set):
    nodes = sorted(network.nodes())
    nodes_i = {node: i for i, node in enumerate(nodes, 1)}

    data = []
    for node in nodes:
        if len(network.predecessors(node)) == 2:
            data.append((nodes_i[node], nodes_i[network.predecessors(node)[0]], nodes_i[network.predecessors(node)[1]]))
        elif len(network.predecessors(node)) == 1:
            data.append((nodes_i[node], nodes_i[network.predecessors(node)[0]], 0))
        else:
            data.append((nodes_i[node], 0, 0))

    with open('data/synbreed_input.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(('id', 'par1', 'par2'))
        csvwriter.writerows(data)

    with open('data/synbreed_id.csv', 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(('id', 'name'))
        for node in nodes:
            if node in node_set:
                csvwriter.writerow((nodes_i[node], node))


def transform_data(data):
    patterns = {
        r'^([a-d]{3})\s*[xX]\s*([a-d]{3})$': transform_axb,
        r'^{([a-d]{3})\s*[xX]\s*([a-d]{3})}\s*[xX]\s*([a-d]{3})$': transform_IaxbIxc,
        r'^([a-d]{3})\s*[xX]\s*{([a-d]{3})\s*[xX]\s*([a-d]{3})}$': transform_axIbxcI,
        r'^{([a-d]{3})\s*[xX]\s*([a-d]{3})}\s*[xX]\s*{([a-d]{3})\s*[xX]\s*([a-d]{3})}$': transform_IaxbIxIcxdI,
    }

    transformed_data = []

    for i, entry in enumerate(data, 1):
        entry['id'] = str(i)
        parent_info = entry['parent_info'].strip()
        parents = []

        for pattern in patterns.keys():
            match = re.match(pattern, parent_info)
            if match:
                parents = patterns[pattern](match, entry)
                break

        transformed_data.extend(parents)

    return transformed_data


def create_graph(data):
    network = nx.DiGraph()
    node_set = set()

    for entry in data:
        from_node = entry[2]
        to_node = entry[1]
        if (not entry[0].endswith('x')) and (not entry[0].endswith('y')):
            node_set.add(to_node)
        network.add_edge(from_node, to_node)

    return network, node_set


def transform_axb(match, entry):
    id_axb = entry['id']
    strain_axb = get_self(entry)
    parent_a = get_parent(match.group(1), entry)
    parent_b = get_parent(match.group(2), entry)
    return [(id_axb, strain_axb, parent_a),
            (id_axb, strain_axb, parent_b)]


def transform_IaxbIxc(match, entry):
    id_IaxbIxc = entry['id']
    id_axb = id_IaxbIxc + 'x'
    strain_IaxbIxc = get_self(entry)
    parent_a = get_parent(match.group(1), entry)
    parent_b = get_parent(match.group(2), entry)
    parent_c = get_parent(match.group(3), entry)
    strain_axb = '{} x {}'.format(parent_a, parent_b)
    return [(id_IaxbIxc, strain_IaxbIxc, strain_axb),
            (id_IaxbIxc, strain_IaxbIxc, parent_c),
            (id_axb, strain_axb, parent_a),
            (id_axb, strain_axb, parent_b)]


def transform_axIbxcI(match, entry):
    id_axIbxcI = entry['id']
    id_bxc = id_axIbxcI + 'x'
    strain_axIbxcI = get_self(entry)
    parent_a = get_parent(match.group(1), entry)
    parent_b = get_parent(match.group(2), entry)
    parent_c = get_parent(match.group(3), entry)
    strain_bxc = '{} x {}'.format(parent_b, parent_c)
    return [(id_axIbxcI, strain_axIbxcI, parent_a),
            (id_axIbxcI, strain_axIbxcI, strain_bxc),
            (id_bxc, strain_bxc, parent_b),
            (id_bxc, strain_bxc, parent_c)]


def transform_IaxbIxIcxdI(match, entry):
    id_IaxbIxIcxdI = entry['id']
    id_axb = id_IaxbIxIcxdI + 'x'
    id_cxd = id_IaxbIxIcxdI + 'y'
    strain_IaxbIxIcxdI = get_self(entry)
    parent_a = get_parent(match.group(1), entry)
    parent_b = get_parent(match.group(2), entry)
    parent_c = get_parent(match.group(3), entry)
    parent_d = get_parent(match.group(4), entry)
    strain_axb = '{} x {}'.format(parent_a, parent_b)
    strain_cxd = '{} x {}'.format(parent_c, parent_d)
    return [(id_IaxbIxIcxdI, strain_IaxbIxIcxdI, strain_axb),
            (id_IaxbIxIcxdI, strain_IaxbIxIcxdI, strain_cxd),
            (id_axb, strain_axb, parent_a),
            (id_axb, strain_axb, parent_b),
            (id_cxd, strain_cxd, parent_c),
            (id_cxd, strain_cxd, parent_d)]


def get_self(entry):
    return entry['strain'].strip()


def get_parent(var, entry):
    return entry['parent_{}_name'.format(var)].strip()


def main(input_file=INPUT_FILE):
    data = load_data(input_file)
    transformed_data = transform_data(data)
    save_edge_list(transformed_data)
    network, node_set = create_graph(transformed_data)
    save_synbreed_data(network, node_set)


if __name__ == '__main__':
    main(sys.argv[1])
