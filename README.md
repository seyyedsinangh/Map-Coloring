# Map Coloring Solver

This project implements a map coloring solver using both a backtracking algorithm with constraint satisfaction techniques and an iterative improvement algorithm. It visualizes the process using OpenCV to display the map with regions colored according to the constraints.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Algorithms](#algorithms)
  - [Backtracking CSP Solver](#backtracking-csp-solver)
  - [Iterative Improvement Solver](#iterative-improvement-solver)
- [Utilities](#utilities)

## Installation

Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the solver with a map image and desired parameters:
```sh
python solver.py <map_image_path> <filtering_mode> <use_variable_ordering> <use_value_ordering>
```

- `map_image_path`: Path to the image file of the map.
- `filtering_mode`: Filtering mode for the algorithm. Options are `-n` (no filtering), `-fc` (forward checking), `-ac` (arc consistency), `-ii` (iterative improvement).
- `use_variable_ordering`: `-t` to use variable ordering heuristic, `-f` otherwise.
- `use_value_ordering`: `-t` to use value ordering heuristic, `-f` otherwise.

Example:
```sh
python solver.py my_map.png -fc -t -f
```

## Project Structure

- `solver.py`: Main script that runs the map coloring solver.
- `map.py`: Contains the `Map` class and related functions for handling map preprocessing and visualization.
- `utils.py`: Utility functions for constraint satisfaction and heuristic calculations.

## Algorithms

### Backtracking CSP Solver

The backtracking solver attempts to solve the map coloring problem by recursively assigning colors to regions, ensuring that no two adjacent regions share the same color. It uses different techniques to enhance the efficiency:

- **Forward Checking (`-fc`)**: Checks ahead to eliminate values that would lead to a conflict.
- **Arc Consistency (`-ac`)**: Maintains arc consistency during the search.
- **Variable Ordering (`-t` flag)**: Chooses the next variable based on a heuristic.
- **Value Ordering (`-t` flag)**: Chooses the next value based on a heuristic.

### Iterative Improvement Solver

The iterative improvement solver initializes the regions with random colors and then iteratively reduces conflicts until the problem is solved or the maximum number of steps is reached. This method can be useful for quickly finding a solution in practice.

## Utilities

The `utils.py` file contains helper functions to support the main algorithms:

- **is_consistent**: Checks if the current variable assignments are consistent.
- **is_solved**: Checks if the problem is solved.
- **get_next_variable**: Retrieves the next variable to assign a color.
- **get_chosen_variable**: Chooses the next variable based on heuristics.
- **get_ordered_domain**: Orders the domain values for a variable.
- **forward_check**: Performs forward checking to eliminate inconsistent values.
- **ac3**: Implements the AC-3 algorithm for maintaining arc consistency.
- **random_choose_conflicted_var**: Randomly selects a conflicting variable.
- **get_chosen_value**: Chooses a value for a variable based on heuristics.

## Acknowledgements

This project uses the OpenCV library for image processing and visualization. Special thanks to the contributors and maintainers of OpenCV.