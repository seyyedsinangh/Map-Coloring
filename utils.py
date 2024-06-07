import random


def is_consistent(graph, variable_value_pairs):
    """
        returns True if the variables that have been assigned a value so far are consistent with the constraints, 
        and False otherwise.
        
        variable_value_pairs can be used to access any value of any variable from the variable as a key
        you can use variable_value_pairs.items() to traverse it as (state, color) pairs
                    variable_value_pairs.keys() to get all the variables,         
                and variable_value_pairs.values() to get all the values
    """
    for variable, color in variable_value_pairs.items():
        if color is not None:
            for neighbor in graph[variable]:
                neighbor_color = variable_value_pairs[neighbor]
                if neighbor_color is not None and neighbor_color == color:
                    return False
    return True


def is_solved(graph, variable_value_pairs):
    """
        returns True if the CSP is solved, and False otherwise
    """
    for variable, color in variable_value_pairs.items():
        if color is not None:
            for neighbor in graph[variable]:
                neighbor_color = variable_value_pairs[neighbor]
                if neighbor_color is None or neighbor_color == color:
                    return False
        else:
            return False
    return True


def get_next_variable(variable_value_pairs, domains):
    """
        returns the index of the next variable from the default order of the unassigned variables
    """
    for variable, color in variable_value_pairs.items():
        if color is None:
            return variable


def get_chosen_variable(graph, variable_value_pairs, domains, mode):
    """
        returns the next variable that is deemed the best choice by the proper heuristic
        use a second heuristic for breaking ties from the first heuristic
    """
    least_len_domain = float('inf')
    least_domain_var = None
    for variable, color in variable_value_pairs.items():
        if color is None:
            temp_len_domain = len(domains[variable])
            if temp_len_domain < least_len_domain:
                least_domain_var = variable
                least_len_domain = temp_len_domain
            # degree heuristic
            elif temp_len_domain == least_len_domain:
                # Bonus: first if is the optimized ordering for non-filtering mode
                if mode == '-n':
                    degree_temp = 0
                    degree_least = 0
                    for neighbor in graph[variable]:
                        if variable_value_pairs[neighbor] is not None:
                            degree_temp += 1
                    for neighbor in graph[least_domain_var]:
                        if variable_value_pairs[neighbor] is not None:
                            degree_least += 1
                    if degree_temp > degree_least:
                        least_domain_var = variable
                        least_len_domain = temp_len_domain
                else:
                    degree_temp = 0
                    degree_least = 0
                    for neighbor in graph[variable]:
                        if variable_value_pairs[neighbor] is None:
                            degree_temp += 1
                    for neighbor in graph[least_domain_var]:
                        if variable_value_pairs[neighbor] is None:
                            degree_least += 1
                    if degree_temp > degree_least:
                        least_domain_var = variable
                        least_len_domain = temp_len_domain
    return least_domain_var


def count_constraint_for_value(graph, variable_value_pairs, domains, variable, color):
    count = 0
    for neighbor in graph[variable]:
        if variable_value_pairs[neighbor] is None and color in domains[neighbor]:
            count += 1
    return count


def get_ordered_domain(graph, variable_value_pairs, domains, variable):
    """
        returns the domain of the variable after ordering its values by the proper heuristic
        (you may use imports here)
    """
    domains[variable].sort(key=lambda color: count_constraint_for_value(graph, variable_value_pairs, domains, variable, color))
    return domains[variable]


def forward_check(graph, variable_value_pairs, domains, variable, value):
    """
        removes the value assigned to the current variable from its neighbors
        returns True if backtracking is necessary, and False otherwise
    """
    for neighbor in graph[variable]:
        if variable_value_pairs[neighbor] is None:
            if value in domains[neighbor]:
                domains[neighbor].remove(value)
            if not domains[neighbor]:
                return True
    return False


def ac3(graph, variable_value_pairs, domains):
    """
        maintains arc-consistency
        returns True if backtracking is necessary, and False otherwise
    """
    queue = []
    for variable, color in variable_value_pairs.items():
        if color is None:
            for neighbor in graph[variable]:
                queue.append((variable, neighbor))
    while queue:
        x1, x2 = queue.pop(0)
        if remove_inconsistent_values(domains, x1, x2):
            if not domains[x1]:
                return True
            for neighbor in graph[x1]:
                queue.append([neighbor, x1])
    return False


def remove_inconsistent_values(domains, x1, x2):
    removed = False
    for color in domains[x1]:
        flag = True
        for value in domains[x2]:
            if color != value:
                flag = False
                break
        if flag:
            domains[x1].remove(color)
            removed = True
    return removed


def random_choose_conflicted_var(graph, variable_value_pairs):
    """
        returns a random variable that is conflicting with a constraint
    """
    conflicted_vars = []
    for var, neighbors in graph.items():
        for neighbor in neighbors:
            if variable_value_pairs[var] == variable_value_pairs[neighbor]:
                conflicted_vars.append(var)
    return random.choice(conflicted_vars)


def get_chosen_value(graph, variable_value_pairs, domains, variable):
    """
        returns the value by using the proper heuristic
        NOTE: handle tie-breaking by random
    """
    min_conflicts = float('inf')
    chosen_value = None
    for color in domains[variable]:
        conflicts = 0
        for neighbor in graph[variable]:
            if variable_value_pairs[neighbor] == color:
                conflicts += 1
        if conflicts < min_conflicts:
            min_conflicts = conflicts
            chosen_value = color
        elif conflicts == min_conflicts:
            chosen_value = random.choice([chosen_value, color])
    return chosen_value
