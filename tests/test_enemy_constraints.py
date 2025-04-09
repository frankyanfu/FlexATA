import unittest
import pandas as pd
from FlexATA.form_builder import FormBuilder
from FlexATA.utility import read_in_data

class TestEnemyConstraints(unittest.TestCase):

    def test_enemy_constraints(self):
        ## read in the item pool data
        item_pool = read_in_data(data_name="pool").head(2000)

        sp = FormBuilder()
        sp.pool = item_pool

        sp.create_item_by_form_variables(
            number_of_forms=20,
            number_of_items_per_form=10
        )
        sp.item_id_column = "ItemID"

        #### add content constraints to the problem
        domain_column = "Domain"
        domain_values_range = {"Domain_A":[7,7],
                          "Domain_B":[3,3]}
    

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
            max_usage=1)
        
        enemy_pairs = read_in_data(data_name="enemy") # Read enemy pairs data

        ## add enemy constraints to the problem

        sp.add_enemy_constraints(
            enemy_pairs=enemy_pairs,
            itemid_column="ItemID",
            enemyid_column="EnemyID"
        )
    
        

        sp.solve_problem(        
            timeLimit=60,  # 2 minutes time limit
            gapRel=0.01, # relative gap of 1%
            gapAbs=0.01, # absolute gap of 1%
            msg=True,   # print the solver messages
            warmStart=False,    # do not use warm start
            solver="CBC")


        ## check if there is an optimal solution found

        self.assertEqual(sp.number_of_forms, 20)
        self.assertEqual(sp.status, "Optimal")


        items_selected = {}
        for r in range(sp.number_of_forms):
            
            item_combined = []
            for i in range(sp.pool_size):
                if sp.value(sp.items[i][r])==1:
                    selected_item = item_pool.iloc[i]
                    item_combined.append(selected_item)
            items_selected[r]=pd.concat(item_combined,axis=1).T

        ### check if there are overlapping items across forms
        for r in range(sp.number_of_forms):
            for c in range(sp.number_of_forms):
                    if r < c:
                        # Ensure no item is repeated across forms
                        selected_items_r = items_selected[r]["ItemID"].tolist()
                        selected_items_c = items_selected[c]["ItemID"].tolist()

                        ## check if the two lists have any common items
                        common_items = set(selected_items_r) & set(selected_items_c)
                        print(f"Common items between form {r} and form {c}: {common_items}")
                        self.assertEqual(len(common_items), 0)

        ### check if there are any enemy pairs in the same form
        for r in range(sp.number_of_forms):
            selected_items = items_selected[r]["ItemID"].tolist()
            enemy_pairs_in_form = enemy_pairs[enemy_pairs["ItemID"].isin(selected_items)&enemy_pairs["EnemyID"].isin(selected_items)]
            self.assertEqual(len(enemy_pairs_in_form), 0)

        for r in range(sp.number_of_forms):
            self.assertEqual(len(items_selected[r]), sp.number_of_items_per_form)
            ### Check the domains
            domain_count = items_selected[r].groupby(domain_column).count()
            self.assertTrue(domain_count["ItemID"].Domain_A >= domain_values_range["Domain_A"][0])
            self.assertTrue(domain_count["ItemID"].Domain_A <= domain_values_range["Domain_A"][1])
            self.assertTrue(domain_count["ItemID"].Domain_B >= domain_values_range["Domain_B"][0])
            self.assertTrue(domain_count["ItemID"].Domain_B <= domain_values_range["Domain_B"][1])        

            ### Check the difficulty levels
            difficulty_count = items_selected[r].groupby(difficulty_column).count()
            self.assertTrue(difficulty_count["ItemID"].Easy >= difficulty_values_range["Easy"][0])
            self.assertTrue(difficulty_count["ItemID"].Easy <= difficulty_values_range["Easy"][1])
            self.assertTrue(difficulty_count["ItemID"].Medium >= difficulty_values_range["Medium"][0])
            self.assertTrue(difficulty_count["ItemID"].Medium <= difficulty_values_range["Medium"][1])
            self.assertTrue(difficulty_count["ItemID"].Hard >= difficulty_values_range["Hard"][0])
            self.assertTrue(difficulty_count["ItemID"].Hard <= difficulty_values_range["Hard"][1])





