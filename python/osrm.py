'''

Helpers for reading .osrm files
===============================

Parse OSRM binary data into igraph format.

Author: Evan K. Friis

For more information, see:

https://github.com/DennisOSRM/Project-OSRM/wiki/OSRM-normalized-file-format

'''

import logging
import struct


_NODE_PACKING = struct.Struct('<iiIbbbb')
_EDGE_PACKING = struct.Struct('<IIihihIbbbb')

log = logging.getLogger(__name__)


def unpack_nodes(filepath):
    """Generates nodes contained in an .osrm file

    It first yields the total number of nodes,
    then each of the nodes, as a struct.Struct.

    :param filepath: path to .osrm file
    :returns: generator yielding first the number of nodes, then each node.

    """
    log.info("Unpacking nodes from %s", filepath)
    with open(filepath, 'rb') as fd:
        n_nodes = struct.unpack_from('<I', fd.read(4))[0]
        yield n_nodes
        log.info("Detected %i nodes in this file", n_nodes)
        report_every = n_nodes / 100
        for i in range(n_nodes):
            if i % report_every == 0:
                log.info("Finished %i/%i nodes", i, n_nodes)
            data = fd.read(_NODE_PACKING.size)
            yield _NODE_PACKING.unpack(data)
    log.info("Done unpacking nodes.")


def unpack_edges(filepath):
    """Generates edges contained in an .osrm file

    It first yields the total number of nodes,
    then each of the nodes, as a struct.Struct.

    :param filepath: path to .osrm file
    :returns: generator yielding first the number of edges, then each edge.

    """
    log.info("Unpacking edges from %s", filepath)
    with open(filepath, 'rb') as fd:
        n_nodes = struct.unpack_from('<I', fd.read(4))[0]
        # Seek to edge section
        fd.seek(n_nodes * _NODE_PACKING.size + 4, 0)
        n_edges = struct.unpack_from('<I', fd.read(4))[0]
        yield n_edges
        log.info("Detected %i edges in this file", n_edges)
        report_every = n_edges / 100
        for i in range(n_edges-1):
            if i % report_every == 0:
                log.info("Finished %i/%i edges", i, n_edges)
            data = fd.read(_EDGE_PACKING.size)
            if not data:
                # EOF
                break
            if len(data) < _EDGE_PACKING.size:
                raise IOError("edge #%i, expected length %i, got %i, (%s)" %
                              (i, _EDGE_PACKING.size, len(data), data))
            yield _EDGE_PACKING.unpack(data)
    log.info("Done unpacking edges.")


def construct_igraph(filepath, simplify=False, remove_disconnected=False):
    '''Construct an igraph.Graph from osrm binary format

    Optionally, the graph can be "simplify()-ied" to remove any
    duplicated edges between nodes.  The edge with the lower weight
    (travel time) is taken.

    Regions of the graph not connected to the largest strongly
    connected component and also optionally be removed.

    :param filepath: path to .osrm file
    :param simplify: if true, remove duplicated edges.
    :param remove_disconnected: if true, *remove* all nodes/edges which are
    note connected to the largest connected component.

    '''
    import igraph
    graph = igraph.Graph()
    node_infos = unpack_nodes(filepath)
    # returns number of nodes
    node_infos.next()
    # add vertices and map osrm node ID -> igraph vertex ID
    nodeid_2_idx = {}
    for idx, (lat, lon, id, _, _, _, _) in enumerate(node_infos):
        # the 'name' is the osrm node ID
        graph.add_vertex(id, lat=lat, lon=lon)
        nodeid_2_idx[id] = idx

    # build eges
    edge_infos = unpack_edges(filepath)
    # returns number of edges
    edge_infos.next()
    edges = []
    weights = []
    for edge in edge_infos:
        edges.append((nodeid_2_idx[edge[0]], nodeid_2_idx[edge[1]]))
        weights.append(edge[4])
    graph.add_edges(edges)
    graph.es['weight'] = weights
    if simplify:
        before_edges = len(graph.es)
        graph = graph.simplify(combine_edges='min')
        log.info("Simplified graph - removed %i/%i edges",
                 before_edges, len(graph.es))
    if remove_disconnected:
        components = graph.components()
        if len(components) > 1:
            max_nodes, max_comp_idx = max(
                ((len(comp), idx) for idx, comp in enumerate(components))
            )
            log.info("Found %i components.  The biggest carries %i "
                     " of total %i nodes",
                     len(components), max_nodes, len(graph.vs))
            # delete all but biggest component (component 0)
            vtx_to_delete = [vtxidx for vtxidx, compidx
                             in enumerate(components.membership)
                             if compidx != max_comp_idx]
            log.info("Deleting %i vertices", len(vtx_to_delete))
            graph.delete_vertices(vtx_to_delete)
    return graph
