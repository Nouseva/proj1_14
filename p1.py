from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush


def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.
    Returns:x
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """

    pathcost = 0
    shortest_path = []
    tracking = {}
    tracking[initial_position] = (0, None)

    queue = [(0, initial_position)]
    while queue:
        currCost, currNode = heappop(queue)
        if currNode == destination:
            while tracking[currNode][1]:
                shortest_path.append(currNode)
                currNode = tracking[currNode][1]
            shortest_path.append(currNode)
            return shortest_path

        else:
            for cost, node in adj(graph, currNode):
                pathcost = cost + tracking[currNode][0]
                if node not in tracking:
                    tracking[node] = (pathcost, currNode)
                    heappush(queue, (pathcost, node))
                elif pathcost < tracking[node][0]:
                    tracking.pop(node)
                    tracking[node] = (pathcost, currNode)
                    heappush(queue, (pathcost, node))
    return None


def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    tracking = {}
    tracking[initial_position] = 0
    queue = [(0, initial_position)]
    while queue:
        currCost, currNode = heappop(queue)
        for cost, node in adj(graph, currNode):
            pathcost = cost + tracking[currNode]
            if node not in tracking:
                tracking[node] = pathcost
                heappush(queue, (pathcost, node))
            elif pathcost < tracking[node]:
                tracking.pop(node)
                tracking[node] = pathcost
                heappush(queue, (pathcost, node))
    return tracking


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.
    
    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and 
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """

    wall = level['walls']
    spaces = level['spaces']
    wayp = level['waypoints']

    diag = sqrt(2)

    # assume that a cell in a wall has no path anywhere
    if cell in wall:
        return []

    weig = spaces.get(cell)
    if weig is None:
    # cell is not a regular space, it must be a waypoint
        weig = wayp.get(cell)

    # list of cardinal directions
    adj  = [
        ((-1,-1), diag), ((-1, 0), 1), ((0, -1), 1), ((-1, 1), diag),
        ((1, -1), diag), ((1, 0) , 1), ((0, 1) , 1), ((1, 1) , diag)
    ]
    # build list of points that are adjacent to cell, regardless if they are valid
    adj_points = [ ((x + cell[0], y + cell[1]), w) for (x, y), w in adj ]

    result = []

    for point, dist in adj_points:
        point_weight = None
        if point in wall:
            continue
        point_weight = spaces.get(point)
        if point_weight is None:
            point_weight = wayp.get(point)

        # cost of the edge between the two cells
        cost = dist * (point_weight + weig) / 2
        result.append((cost, point))

    return result


def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path)
    else:
        print("No path possible!")


def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from 
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]
    
    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'example.txt', 'a','e'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')
