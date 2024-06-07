import sys
import cv2
import random
from map import Map
import utils
import copy

ESCAPE_KEY_CHARACTER = 27
SLEEP_TIME_IN_MILLISECONDS = 1

GRAPH = {}
COLORED_STATES = {}
N_COLORS = 4
COLORING_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
NONE_COLOR = (0, 0, 0)
BACKTRACK_COUNT = 0

MAP = None
FILTERING_MODE = None
USE_VARIABLE_ORDERING = None
USE_VALUE_ORDERING = None


def colorize_map(manual=False):
    for i in range(len(MAP.nodes)):
        if COLORED_STATES[i] is None:
            MAP.change_region_color(MAP.nodes[i], NONE_COLOR)
        else:
            MAP.change_region_color(MAP.nodes[i], COLORING_COLORS[COLORED_STATES[i]])
    cv2.imshow('Colorized Map', MAP.image)
    if not manual:
        key = cv2.waitKey(SLEEP_TIME_IN_MILLISECONDS)
    else:
        key = cv2.waitKey()
    if key == ESCAPE_KEY_CHARACTER:
        cv2.destroyAllWindows()
        exit()


'''BACKTRACKING CSP SOLVER'''


def backtrack_solve(domains):
    """
        returns True when the CSP is solved, and False when backtracking is necessary
        
        you will need to use the global variables GRAPH and COLORED_STATES, refer to preprocess() and try to see what they represent
        use FILTERING_MODE, USE_VARIABLE_ORDERING, and USE_VALUE_ORDERING for branching into each mode
        FILTERING_MODE is either "-n", "-fc", or "-ac", and the other two are booleans
        
        HINT: you may want to import deepcopy to generate the input to the recursive calls
        NOTE: remember to call colorize_map() after each value assignment for the graphical update
              use colorize_map(True) if you want to manually progress by pressing any key
        NOTE: don't forget to update BACKTRACK_COUNT on each backtrack
    """
    global BACKTRACK_COUNT
    if utils.is_solved(GRAPH, COLORED_STATES):
        print("solved")
        print(f"backtrack count: {BACKTRACK_COUNT}")
        colorize_map(True)
        exit(0)
    if not utils.is_consistent(GRAPH, COLORED_STATES):
        BACKTRACK_COUNT += 1
        return
    if FILTERING_MODE == '-ac':
        if utils.ac3(GRAPH, COLORED_STATES, domains):
            BACKTRACK_COUNT += 1
            return
    if USE_VARIABLE_ORDERING:
        next_variable = utils.get_chosen_variable(GRAPH, COLORED_STATES, domains, FILTERING_MODE)
    else:
        next_variable = utils.get_next_variable(COLORED_STATES, domains)
    if USE_VALUE_ORDERING:
        value_list = utils.get_ordered_domain(GRAPH, COLORED_STATES, domains, next_variable)
    else:
        value_list = domains[next_variable]
    copy_domains = copy.deepcopy(domains)
    for value in value_list:
        if FILTERING_MODE == '-fc':
            if utils.forward_check(GRAPH, COLORED_STATES, copy_domains, next_variable, value):
                BACKTRACK_COUNT += 1
                copy_domains = copy.deepcopy(domains)
                continue
        COLORED_STATES[next_variable] = value
        colorize_map()
        copy_domains[next_variable] = [value]
        backtrack_solve(copy_domains)
        copy_domains = copy.deepcopy(domains)
        COLORED_STATES[next_variable] = None
        colorize_map()
    BACKTRACK_COUNT += 1
    return


'''ITERATIVE IMPROVEMENT SOLVER'''


def iterative_improvement_solve(domains, max_steps=100):
    """
        you will need to use the global variables GRAPH and COLORED_STATES, refer to preprocess() and try to see what they represent
        don't forget to call colorize_map()
        1. initialize all the variables randomly,
        2. then change the conflicting values until solved, use max_steps to avoid infinite loops
    """
    "*** YOUR CODE HERE ***"
    for var in COLORED_STATES.keys():
        COLORED_STATES[var] = random.choice(domains[var])
    colorize_map()
    steps = 0
    while not utils.is_solved(GRAPH, COLORED_STATES) and steps < max_steps:
        chosen_var = utils.random_choose_conflicted_var(GRAPH, COLORED_STATES)
        chosen_color = utils.get_chosen_value(GRAPH, COLORED_STATES, domains, chosen_var)
        COLORED_STATES[chosen_var] = chosen_color
        colorize_map()
        steps += 1
    print('Steps: ', steps)
    "*** YOUR CODE ENDS HERE ***"
    print("solved")
    colorize_map(True)


def preprocess():
    MAP.initial_preprocessing()
    for vertex in range(len(MAP.nodes)):
        GRAPH[vertex], COLORED_STATES[vertex] = set(), None
    for v in MAP.nodes:
        for adj in v.adj:
            GRAPH[v.id].add(adj)
            GRAPH[adj].add(v.id)


def assign_boolean_value(argument):
    if argument == "-t":
        return True
    elif argument == "-f":
        return False
    else:
        return None


if __name__ == "__main__":
    try:
        MAP_IMAGE_PATH = sys.argv[1]
        FILTERING_MODE = sys.argv[2]
        is_ii_mode = FILTERING_MODE == "-ii"
        if not is_ii_mode:
            USE_VARIABLE_ORDERING = assign_boolean_value(sys.argv[3])
            USE_VALUE_ORDERING = assign_boolean_value(sys.argv[4])
            if USE_VARIABLE_ORDERING is None or USE_VALUE_ORDERING is None:
                print("invalid ordering flags")
                exit(1)
    except IndexError:
        print("Error: invalid arguments.")
        exit(1)

    try:
        MAP = Map(cv2.imread(MAP_IMAGE_PATH, cv2.IMREAD_COLOR))
    except Exception as e:
        print("Could not read the specified image")
        exit(1)

    preprocess()
    domains = [list(range(N_COLORS)) for _ in range(len(GRAPH.keys()))]
    if not is_ii_mode:
        print(
            f"filtering mode: {FILTERING_MODE}, use variable ordering: {USE_VARIABLE_ORDERING}, use value ordering: {USE_VALUE_ORDERING}")
        backtrack_solve(domains)
    else:
        iterative_improvement_solve(domains)
