# FlexATA

FlexATA is a Python package designed for automated test assembly (ATA). It provides a flexible and efficient way to assemble test forms from an item pool while satisfying various constraints, such as content balancing, information targets, item usage, and more. The package leverages linear programming to solve the test assembly problem and supports multiple solvers, including CBC and CPLEX.

## Features

- **Content Constraints**: Control the distribution of items based on attributes like domain, difficulty, etc.
- **Information Constraints**: Ensure forms meet specific information targets at given theta points.
- **Enemy Constraints**: Prevent specific pairs of items from appearing together in the same form.
- **Set Constraints**: Handle item sets and ensure a fixed number of items from each set are included.
- **Form Pair Constraints**: Control the overlap of items between forms.
- **Item Usage Constraints**: Limit the number of times an item can be used across forms.

## Installation

To install the package, clone the repository and install the dependencies:

```bash
git clone https://github.com/frankyanfu/FlexATA.git
cd FlexATA
pip install -r requirements.txt
```

## Getting Started

Example Usage
Here is a basic example of how to use the FlexATA package:

```python
import pandas as pd
from FlexATA.form_builder import FormBuilder
from FlexATA.utility import read_in_data

# Load the item pool
item_pool = read_in_data(data_name="pool")

# Initialize the FormBuilder
sp = FormBuilder(minimize=True)
sp.pool = item_pool.head(1000)

# create item by pool variables: 3 forms and 10 items per form
sp.create_item_by_form_variables(
    number_of_forms = 3,
    number_of_items_per_form = 10
)

# Add content constraints
domain_values_range = {"Domain_A":[7,7],
                    "Domain_B":[3,3]}
sp.add_content_constraints_by_column(
    column_name="Domain", 
    values_range=domain_values_range)


# Solve the problem
sp.solve_problem(timeLimit=60, solver="CBC")

# Check the solution status
print("Solution Status:", sp.status)
# print out the selected items
for r in range(sp.number_of_forms):
    item_combined = []
    for i in range(sp.pool_size):
        if sp.value(sp.items[i][r])==1:
            selected_item = item_pool.iloc[i]
            print(f"Form {r}: {selected_item.ItemID} is selected  with  and Domain of {selected_item.Domain}")
```

## Examples

The package includes several example scripts to demonstrate its functionality:

- `example_form_pair.py`: Demonstrates form pair constraints.
- `example_information_constraints.py`: Shows how to add information constraints.
- `example_parelle_information.py`: Show how to control the information across forms.
- `example_enemy.py`: Illustrates enemy constraints.
- `example_set.py`: Handles set constraints.
- `example_content.py`: Demonstrates content balancing.

You can find these examples in the `examples` directory.

## API Reference

Core Classes

`FormBuilder`

The main class for defining and solving the test assembly problem.

**Attributes**:

- `number_of_forms`: Number of forms to assemble.
- `number_of_items_per_form`: Number of items per form.
- `pool`: The item pool as a pandas DataFrame.
- `item_id_column`: Column name for item IDs.
- `irt_a_column`, `irt_b_column`, `irt_c_column`: Columns for IRT parameters.

**Methods**:

- `create_item_by_form_variables(number_of_forms,number_of_items_per_form)`: Creates decision variables for item selection.
- `add_content_constraints_by_column(column_name, values_range)`: Adds content constraints.
- `add_information_based_on_theta_points(theta_points, info_targets,as_objective)`: Adds information constraints or objectives.
- `add_weight_objective(weights)`: Add weights as objectives
- `add_weight_constraints(weights)`: Add weights constraints
- `add_enemy_constraints(enemy_pairs, itemid_column, enemyid_column)`: Adds enemy constraints.
- `solve_problem(timeLimit, solver)`: Solves the problem using the specified solver.

### Data Requirements

Item Pool

The item pool should be a pandas DataFrame with the following columns:

- `ItemID`: Unique identifier for each item.
- `Domain`(optional): Content domain of the item.
- `IRT_a`, `IRT_b`, `IRT_c` (optional): IRT parameters for the item.
- `SetID` (optional): Identifier for item sets.
- `Difficulty` (optional): Difficulty level of the item.

Enemy Pairs

A pandas DataFrame with two columns (one direction is ok):

- `ItemID`: Th item ID in the enemy pair.
- `EnemyID`: The enemy item in the enemy pair.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
