
import pandas as pd
import numpy as np
from FlexATA.form_builder import FormBuilder
from FlexATA.utility import read_in_data

if __name__ == "__main__":
    ## read in the item pool data
    item_pool = read_in_data(data_name="pool").head(1000)

    sp = FormBuilder()
    sp.pool = item_pool

    sp.create_item_by_form_variables(
        number_of_forms=3,
        number_of_items_per_form=10
    )
    #### 
    sp.create_delta_variables()
    sp.item_id_column = "ItemID"
    sp.irt_a_column="IRT_a"
    sp.irt_b_column="IRT_b"
    sp.irt_c_column="IRT_c"


    #### add content constraints to the problem
    domain_column = "Domain"
    domain_values_range = {"Domain_A":[4,4],
                        "Domain_B":[6,6]}


    ## add the domain constraints to the problem
    sp.add_content_constraints_by_column(
        column_name=domain_column,
        values_range=domain_values_range)


    ### specify the difficulty level for each form
    difficulty_column = "Difficulty"
    # Here we assume the difficulty levels are "Easy", "Medium", and "Hard"
    #  we want to have at least 3 Easy items, 4 Medium items, and 3 Hard items in each form
    #  we want to have at most 3 Easy items, 4 Medium items, and 3 Hard items in each form
    # Note: The values in the range are inclusive, so [3,3] means exactly 3 items
    # If you want to allow more flexibility, you can change the range to [3,5] for example
    difficulty_values_range = {"Easy":[3,3],
                        "Medium":[4,4],
                        "Hard":[3,3]
    }

    ### add the difficulty constraints for each form
    sp.add_content_constraints_by_column(
        column_name=difficulty_column,
        values_range=difficulty_values_range)

    ### make sure the item is only used at most once in each form
    sp.add_item_usage_constraints(
        min_usage=0,
        max_usage=2)

    ## add set constraints
    sp.add_set_constraints(
        set_id_column="SetID",
        number_of_items_per_set=3)

    ### add the information constraints for each form
    sp.add_information_based_on_theta_points(
        theta_points= [
            -0.6,
            -0.4,
            0.2,
            0.4],
        info_targets=[
            [2.7,3],
            [4,4.3],
            [4,4.3],
            [2.7,3]
            ],
        as_objective=True)

    sp.add_form_pair_constraints(
        min_overlap_prop=0.2,
        max_overlap_prop=0.2
    )

    sp.solve_problem(        
        timeLimit=120,  # 2 minutes time limit
        gapRel=0.01, # relative gap of 1%
        gapAbs=0.01, # absolute gap of 1%
        msg=True,   # print the solver messages
        warmStart=False,    # do not use warm start
        solver="CBC")


    ## check if there is an optimal solution found
    print("Optimal solution found: ", sp.status)



    items_selected = {}
    information_sum_form ={}
    for r in range(sp.number_of_forms):
        information_per_form_per_theta_point = [0 for i in range(len(sp.theta_points))]
        item_combined = []
        for i in range(sp.pool_size):
            if sp.value(sp.items[i][r])==1:
                selected_item = item_pool.iloc[i]
                item_combined.append(selected_item)
                for k in range(len(sp.theta_points)):
                    information_per_form_per_theta_point[k] += sp.information_all[k][i]
        items_selected[r]=pd.concat(item_combined,axis=1).T
        information_sum_form[r]=information_per_form_per_theta_point

    delta_value = sp.value(sp.delta)    
    for r in range(sp.number_of_forms):
        for k in range(len(sp.theta_points)):
            print(np.round(information_sum_form[r][k],8) >= np.round(sp.info_targets[k][0]-delta_value,8))
            print(np.round(information_sum_form[r][k],8) <= np.round(sp.info_targets[k][0]+delta_value,8))


    for r in range(sp.number_of_forms):
        for c in range(sp.number_of_forms):
                if r < c:
                    # Ensure no item is repeated across forms
                    selected_items_r = items_selected[r]["ItemID"].tolist()
                    selected_items_c = items_selected[c]["ItemID"].tolist()
                    ## check if the two forms' common items are 2
                    common_items = set(selected_items_r) & set(selected_items_c)
                    print(f"Common items between form {r} and form {c}: {len(common_items)}")


    ### Check the set constraints
    for r in range(sp.number_of_forms):
        set_count = items_selected[r].groupby("SetID").count()
        for set_id in set_count.index:
            print(f"Form{r}: SetID: {set_id}, Item Count: {set_count.loc[set_id]['ItemID']}")
        

