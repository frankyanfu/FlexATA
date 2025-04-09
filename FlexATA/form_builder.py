import pulp as pl
import pandas as pd
from FlexATA.utility import *
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)



##TODO make it a plot for information and SE
##TODO add more solvers from the Pulp Package


class FormBuilder:
    """
    form_builder
    =====================
    A class to define and solve a linear programming problem for form assembly. This class is designed to handle 
    various constraints and objectives related to assembling forms from a pool of items, including information 
    constraints, content constraints, enemy constraints, set constraints, and item usage constraints.
    Attributes:
    -----------
    - number_of_items_per_form (int): Number of items per form.
    - number_of_forms (int): Number of forms to be created.
    - pool_size (int): Size of the item pool.
    - items (LpVariable): Binary decision variables representing item-by-form assignments.
    - delta (LpVariable): Continuous variable for deviation in constraints.
    - sets (LpVariable): Binary decision variables representing set-by-form assignments.
    - form_pair (LpVariable): Binary decision variables for form pair overlaps.
    - pool (DataFrame): The item pool containing item metadata.
    - item_id_column (str): Column name for item IDs in the pool.
    - set_id_column (str): Column name for set IDs in the pool.
    - irt_a_column (str): Column name for IRT 'a' parameter in the pool.
    - irt_b_column (str): Column name for IRT 'b' parameter in the pool.
    - irt_c_column (str): Column name for IRT 'c' parameter in the pool.
    - theta_points (list): List of theta points for information constraints.
    - info_targets (list): List of information targets corresponding to theta points.
    - information_all (list): List of information values for all items at different theta points.
    Methods:
    --------
    - create_item_by_form_variables(): Creates binary decision variables for item-by-form assignments.
    - create_set_by_form_variables(number_of_sets): Creates binary decision variables for set-by-form assignments.
    - create_delta_variables(): Creates a continuous variable for deviation in constraints.
    - create_form_pair_variables(form_pairs): Creates binary decision variables for form pair overlaps.
    - add_information_based_on_theta_points(theta_points, info_targets): Adds information constraints based on theta points.
    - add_information_constraints(information, target, name): Adds information constraints for a specific theta point.
    - add_content_constraints(constraints, target, direction, name): Adds content constraints for a specific form.
    - add_enemy_constraints(enemy_pairs, itemid_column, enemyid_column): Adds constraints to ensure enemy items do not appear together.
    - add_set_constraints(set_id_column, number_of_items_per_set): Adds constraints to ensure the number of items in a set is consistent.
    - add_content_constraints_by_column(column_name, values_range): Adds content constraints based on a column in the pool.
    - add_item_usage_constraints(min_usage, max_usage): Adds constraints to control the minimum and maximum usage of items across forms.
    - create_form_pairs(): Creates all possible pairs of forms for overlap constraints.
    - add_form_pair_constraints(min_overlap_prop, max_overlap_prop): Adds constraints to control the overlap between form pairs.
    - add_objective(): Adds the objective function to minimize the deviation (delta).
    - solve_problem(timeLimit, gapRel, gapAbs, msg, warmStart, solver): Solves the linear programming problem using the specified solver.
    - write_problem(full_file_path): Writes the linear programming problem to a file.
    """

    # init method or constructor
    def __init__(self, minimize=True):
        if minimize:
            self.__prob = pl.LpProblem("Form_Assembly_Minimize",pl.LpMinimize)
        else:
            self.__prob = pl.LpProblem("Form_Assembly_Maximize",pl.LpMaximize)
        
        self.__number_of_items_per_form = 0
        self.__number_of_forms = 0
        self.__pool_size = 0
        #### LP variables
        self.__items = None
        self.__delta = None
        self.__sets=None
        self.__form_pair=None

        #### value
        self.__value = None


        #### define variable names in the input files
        self.__pool=None
        self.__item_id_column = None
        self.__set_id_column = None
        self.__irt_a_column = None
        self.__irt_b_column = None
        self.__irt_c_column = None
        self.__information_all = []
        self.__theta_points=[]
        self.__info_targets=[]
        

    ##### get number of items per form
    @property
    def number_of_items_per_form(self):
        return self.__number_of_items_per_form
    
    ##### set number of items per form
    @number_of_items_per_form.setter
    def number_of_items_per_form(self,number_of_items_per_form):
        self.__number_of_items_per_form=number_of_items_per_form
    
    ##### get number_of_forms
    @property
    def number_of_forms(self):
        return self.__number_of_forms
    
    ##### set number_of_forms
    @number_of_forms.setter
    def number_of_forms(self,number_of_forms):
        self.__number_of_forms=number_of_forms
    
    ##### get the pool of the items
    @property
    def pool_size(self):
        return self.__pool_size
    
    ##### set pool_size
    @pool_size.setter
    def pool_size(self,pool_size):
        self.__pool_size=pool_size


    ##### get the item variables
    @property
    def items(self):
        return self.__items
    
    ##### get the delta variables
    @property
    def delta(self):
        return self.__delta
    
    ### get pool
    @property
    def pool(self):
        return self.__pool
    
    ##### set 
    @pool.setter
    def pool(self,pool):
        self.__pool=pool
        self.__pool_size = pool.shape[0]

    ### get item_id_column
    @property
    def item_id_column(self):
        return self.__item_id_column
    
    ##### set  item_id_column
    @item_id_column.setter
    def item_id_column(self,item_id_column):
        self.__item_id_column=item_id_column

    ### get set_id_column
    @property
    def set_id_column(self):
        return self.__set_id_column
    
    ##### set set_id_column
    @pool.setter
    def set_id_column(self,set_id_column):
        self.__set_id_column=set_id_column
    
    ### get irt_a_column
    @property
    def irt_a_column(self):
        return self.__irt_a_column  
    
    ##### set irt_a_column
    @irt_a_column.setter
    def irt_a_column(self,irt_a_column):
        if irt_a_column not in self.__pool.columns:
            raise Exception(f"The irt_a_column {irt_a_column} doesn't exist in the item pool")
        self.__irt_a_column=irt_a_column
    
    ### get irt_b_column
    @property
    def irt_b_column(self):
        return self.__irt_b_column
    
    ##### set irt_b_column
    @irt_b_column.setter
    def irt_b_column(self,irt_b_column):
        if irt_b_column not in self.__pool.columns:
            raise Exception(f"The irt_b_column {irt_b_column} doesn't exist in the item pool")
        self.__irt_b_column=irt_b_column
        
    
    ### get irt_c_column
    @property
    def irt_c_column(self):
        return self.__irt_c_column
    
    ##### set irt_c_column
    @irt_c_column.setter 
    def irt_c_column(self,irt_c_column):
        if irt_c_column not in self.__pool.columns:
            raise Exception(f"The irt_c_column {irt_c_column} doesn't exist in the item pool")
        # fill na values with 0 for irt_c
        self.__pool[irt_c_column]=self.__pool[irt_c_column].fillna(0)
        # self.__pool[irt_c_column].fillna(0,inplace=True)  # fill NaN values with 0
        self.__irt_c_column=irt_c_column
        

    ### get set_id_column
    @property
    def set_id_column(self):
        return self.__set_id_column
    
    ##### set set_id_column
    @pool.setter
    def set_id_column(self,set_id_column):
        self.__set_id_column=set_id_column

    ### get theta_points
    @property
    def theta_points(self):
        return self.__theta_points
    
    ##### set theta_points
    @theta_points.setter
    def theta_points(self,theta_points):
        self.__theta_points=theta_points
    
    ### get info_targets
    @property
    def info_targets(self):
        return self.__info_targets
    
    ##### set info_targets
    @info_targets.setter
    def info_targets(self,info_targets):
        self.__info_targets=info_targets
    

    ##### get information_all
    @property
    def information_all(self):
        return self.__information_all

    ### creating item by form variables
    def create_item_by_form_variables(self,
                                      number_of_items_per_form=None,
                                      number_of_forms=None):
        if number_of_items_per_form:
            self.__number_of_items_per_form = number_of_items_per_form
        if number_of_forms:
            self.__number_of_forms = number_of_forms
        self.__items = pl.LpVariable.dicts("Item", 
                                           (range(self.__pool_size),range(self.__number_of_forms)), 
                                           cat="Binary")
    
    ### creating set by form variables
    def create_set_by_form_variables(self,number_of_sets):
        self.__sets = pl.LpVariable.dicts("Set", 
                                          (range(number_of_sets),range(self.__number_of_forms)), 
                                          cat="Binary")
    
    ### creating delta variables for min and max method
    def create_delta_variables(self):
        self.__delta = pl.LpVariable("Delta", 
                                     0, 
                                     None, 
                                     pl.LpContinuous)
    
    ### create form pair variables
    def create_form_pair_variables(self,form_pairs):
        number_of_pairs = len(form_pairs)
        self.__form_pair = pl.LpVariable.dicts("FormPair", 
                                               (range(self.__pool_size),range(number_of_pairs)), 
                                               cat="Binary")

    ### add information constraints based on theta points
    def add_information_based_on_theta_points(self,theta_points,info_targets,as_objective=True):
        self.__theta_points=theta_points
        self.__info_targets=info_targets
        if len(theta_points)!=len(info_targets):
            raise Exception("The length of theta_points and info_targets are different")
        if not self.__irt_a_column:
            raise Exception("Please set the irt_a_column in the item pool before adding information constraints")
        if not self.__irt_b_column:
            raise Exception("Please set the irt_b_column in the item pool before adding information constraints")
        if not self.__irt_c_column:
            raise Exception("Please set the irt_c_column in the item pool before adding information constraints")

        if as_objective:
            ### first create delta variable
            self.create_delta_variables()
            ### add delta as objective
            self.add_delta_as_objective()

        for i,theta in enumerate(theta_points):
            information = [fisher_info(x[0],x[1],x[2],theta,D=1.702) for x in self.__pool[[self.__irt_a_column,self.__irt_b_column,self.__irt_c_column]].values]
            self.__information_all.append(information)
            if as_objective:
                self.add_information_objective(
                    information=information,
                    target=info_targets[i],
                    name=f"theta_{str(theta)}")
            else:
                self.add_information_constraints(
                    information=information,
                    target=info_targets[i],
                    name=f"theta_{str(theta)}")                

            
    ##### add 
    def add_delta_as_objective(self):
        self.__prob += pl.lpSum(self.__delta)

    ### add information constraints based on information values
    ### add delta variables to control the information difference
    def add_information_objective(self,information,target,name):
        if len(information)!=self.__pool_size:
            raise Exception("The information length is different from the item pool size")
        
        for r in range(self.__number_of_forms):
            self.__prob += (pl.lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]+self.__delta) >= target[0],f"form{r}_{name}_plus_delta")
            self.__prob += (pl.lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]-self.__delta) <= target[0],f"form{r}_{name}_minus_delta")


    ### purely constrol the information
    def add_information_constraints(self,information,target,name):
        if len(information)!=self.__pool_size:
            raise Exception("The information length is different from the item pool size")
        
        for r in range(self.__number_of_forms):
            self.__prob += (pl.lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]) >= target[0],f"form{r}_{name}_minimum")
            self.__prob += (pl.lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]) <= target[1],f"form{r}_{name}_maximum")

    ### add weight to the objective
    def add_weights_objective(self,weights):
        if len(weights)!=self.__pool_size:
            raise Exception("The weights length is different from the item pool size")
        self.__prob += pl.lpSum([self.__items[i][r]*weights[i] for i in range(self.__pool_size) for r in range(self.__number_of_forms)])
           

    ### add weights as constraints
    def add_weights_constraints(self,weights,weight_target):
        if len(weights)!=self.__pool_size:
            raise Exception("The weights length is different from the item pool size")
        
        for r in range(self.__number_of_forms):
            self.__prob += (pl.lpSum([self.__items[i][r]*weights[i] for i in range(self.__pool_size)]) >= weight_target[0],f"form{r}_weights_minimum")
            self.__prob += (pl.lpSum([self.__items[i][r]*weights[i] for i in range(self.__pool_size)]) <= weight_target[1],f"form{r}_weights_maximum")

    ##### add content constraints
    def add_content_constraints(self,constraints,target,direction,name):
        if len(constraints)!=self.__pool_size:
            raise Exception("The content constraints length is different from the pool size")
        direction_selection={
            "==":pl.LpConstraintEQ,
            ">=":pl.LpConstraintGE,
            "<=":pl.LpConstraintLE
        }
        for r in range(self.__number_of_forms):
            self.__prob += pl.LpConstraint(
                e = pl.lpSum([self.__items[i][r]*constraints[i] for i in range(self.__pool_size)]),
                sense=direction_selection[direction],
                rhs=target,
                name=f"form{r}:{name}_direction{direction_selection[direction]}")
    
    ### add enemy constraints
    def add_enemy_constraints(self,enemy_pairs,itemid_column,enemyid_column):
        ## Check if the itemID and enemyID columns exist in the enemy_pairs
        if itemid_column not in enemy_pairs.columns:
            raise Exception(f"The itemid_column {itemid_column} doesn't exist in the enemy_pairs")
        
        if enemyid_column not in enemy_pairs.columns:
            raise Exception(f"The enemyid_column {enemyid_column} doesn't exist in the enemy_pairs")

        if not self.__item_id_column:
            raise Exception("Please set the item_id_column in the item pool before adding enemy constraints")

        ## For enemy_pairs dataset, order ItemID and EnemyID based on the alphabetical order and combine them to create pairs
        all_item_ids = self.__pool[self.__item_id_column].to_list()
        ### only keep the pairs that are in the item pool
        enemy_pairs = enemy_pairs[enemy_pairs[itemid_column].isin(all_item_ids) & enemy_pairs[enemyid_column].isin(all_item_ids)]
        all_enemy_pairs = enemy_pairs.apply(lambda x: sorted([x[itemid_column],x[enemyid_column]]) , axis=1).tolist()

        ### Get unique pairs
        all_enemy_pairs_unique = {}
        for enemy_pair in all_enemy_pairs:
            new_pair = list(set(enemy_pair))
            pair="&".join(new_pair)
            if not pair in all_enemy_pairs_unique.keys():
                all_enemy_pairs_unique[pair]=new_pair
    

        for pair_name,enemy_pair in all_enemy_pairs_unique.items():
            enemy_pair_constraint = [1 if x in enemy_pair else 0 for x in self.__pool[self.__item_id_column]]
            if sum(enemy_pair_constraint)>1:
                for r in range(self.__number_of_forms):
                    self.__prob += (pl.lpSum([self.__items[i][r]*enemy_pair_constraint[i] for i in range(self.__pool_size)]) <= 1,f"Form{r}:Enemy_pairs_{pair_name}_constraints")
        

    #### constrain number of items within a set
    def add_set_constraints(self,set_id_column,number_of_items_per_set):
        if set_id_column not in self.__pool.columns:
            raise Exception(f"The set_id_column {set_id_column} doesn't exist in the item pool")
        
        set_ids = self.__pool[set_id_column].unique()
        set_ids = [x for x in set_ids if not pd.isna(x)]

        self.create_set_by_form_variables(number_of_sets=len(set_ids))

        for k,set_id in enumerate(set_ids):
            set_constraint = [1 if x==set_id else 0 for x in self.__pool[set_id_column]]
            for r in range(self.__number_of_forms):
                self.__prob += (pl.lpSum([self.__items[i][r]*set_constraint[i] for i in range(self.__pool_size)]-self.__sets[k][r]*number_of_items_per_set) == 0,f"Form{r}:SetID_{set_id}_constraints")
    



    ##### add content constraints by using column name and values
    def add_content_constraints_by_column(self,column_name,values_range):
        # self.__pool = self.__pool[[self.__item_id_column,column_name]]
        if column_name not in self.__pool.columns:
            raise Exception(f"The set_id_column {column_name} doesn't exist in the item pool")
        
        for key,value in values_range.items():
            constraint = [1 if x==key else 0 for x in self.__pool[column_name]]
            self.add_content_constraints(constraint,value[0],">=",key)
            self.add_content_constraints(constraint,value[1],"<=",key)
     


    def add_item_usage_constraints(self,min_usage,max_usage):
        for i in range(self.__pool_size):
            self.__prob += (pl.lpSum([self.__items[i][r] for r in range(self.__number_of_forms)]) >= min_usage,f"Item{i}_usage_minimum")
            self.__prob += (pl.lpSum([self.__items[i][r] for r in range(self.__number_of_forms)]) <= max_usage,f"Item{i}_usage_maximum")
    

    ### create form pairs
    def create_form_pairs(self):
        if self.__number_of_forms < 2:
            raise Exception("Number of forms must be at least 2 to create pairs")
        return [(i, j) for i in range(self.__number_of_forms) for j in range(i + 1, self.__number_of_forms)]

    ### Create form pair constraints
    def add_form_pair_constraints(self,min_overlap_prop,max_overlap_prop):
        form_pairs = self.create_form_pairs()
        self.create_form_pair_variables(form_pairs)

        for k in range(self.__pool_size):
            for v,(i, j) in enumerate(form_pairs):
                self.__prob  += (pl.lpSum([self.__items[k][i] + self.__items[k][j]-1*self.__form_pair[k][v]])<=1,f"forms_{i}_and_{j}_item{k}_overlap_lower_bound") # ensure that the overlap is at most 1 for each pair of forms
                self.__prob  += (pl.lpSum([self.__items[k][i] + self.__items[k][j]-2*self.__form_pair[k][v]])>=0,f"forms_{i}_and_{j}_item{k}_overlap_upper_bound")
        for v,(i, j) in enumerate(form_pairs):
            self.__prob  += (pl.lpSum([self.__form_pair[k][v] for k in range(self.__pool_size)]) >= min_overlap_prop*self.__number_of_items_per_form,f"forms_{i}_and_{j}_min_overlap")
            self.__prob  += (pl.lpSum([self.__form_pair[k][v] for k in range(self.__pool_size)]) <= max_overlap_prop*self.__number_of_items_per_form,f"forms_{i}_and_{j}_max_overlap")



    ##### solve
    def solve_problem(self,
                      timeLimit=360,
                      gapRel=0.01,
                      gapAbs=0.01,
                      msg=True,
                      warmStart=False,
                      solver="CBC"):
        if solver not in ["CBC", "CPLEX"]:
            raise Exception(f"Solver {solver} is not supported. Please use 'CBC' or 'CPLEX'.")
        if solver == "CBC":
            self.__prob.solve(pl.pulp.PULP_CBC_CMD(
                timeLimit=timeLimit,
                gapRel=gapRel,
                gapAbs=gapAbs,
                msg=msg,
                warmStart=warmStart))
        
        if solver == "CPLEX":
            self.__prob.solve(pl.CPLEX_PY(
                timeLimit=timeLimit,
                gapRel=gapRel,
                msg=msg,
                warmStart=warmStart))

        print("Status:", pl.LpStatus[self.__prob.status])
    
    #### write out the LP function
    def write_problem(self,full_file_path):
        self.__prob.writeLP(full_file_path)

    #### get the solution status
    @property
    def status(self):
        return pl.LpStatus[self.__prob.status]
    
    #### return the value of an variable

    def value(self,var):
        if isinstance(var, pl.LpVariable):
            return pl.value(var)
        else:
            raise ValueError("The variable must be an instance of LpVariable.")
        

## Ensure the module is importable and can read in data correctly
if __name__ == "__main__":
    ### Sample code to demonstrate the usage of form_assembly class
    ### read in the item pool data
    ### Each row represent an item
    ### Each column represent an attribute of the item
    item_data = read_in_data(data_name="pool")  



    #### Create builder object

    sp = FormBuilder()

    ### 
    sp.pool = item_data.head(2000)
    sp.number_of_forms = 2
    sp.number_of_items_per_form=10
    sp.create_item_by_form_variables()
    sp.item_id_column="ItemID"
    sp.irt_a_column = "IRT_a"
    sp.irt_b_column = "IRT_b"
    sp.irt_c_column = "IRT_c"


    ### speficy the column in the item pool data that you want to control the content for each form
    ### for example, we want to control the Domain
    domain_column = "Domain"
    ### For Domain A, we want to have at least 7 items and at most 7 items in each form
    ### For Domain B, we want to have at least 3 items and at most 3 items in each form
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



    #### add set items constraints to each form
    #### the set_id_column is the column in the item pool that specifies set information of the items
    #### number_of_items_per_set specifies how many items should be selected from each set

    sp.add_set_constraints(
        set_id_column="SetID",
        number_of_items_per_set=3)
    
    ### add enemy constraints
    # Note: enemy_pairs should be a DataFrame with two columns: "ItemID" and "EnemyID"
    # Each row represents a pair of items that cannot be selected together in the same form.

    enemy_pairs = read_in_data(data_name="enemy") # Read enemy pairs data

    ## add enemy constraints to the problem

    sp.add_enemy_constraints(
        enemy_pairs=enemy_pairs,
        itemid_column="ItemID",
        enemyid_column="EnemyID"
    )
    

    sp.add_information_based_on_theta_points(
        theta_points= [
            -0.6,
            -0.4,
            0.2,
            0.4],
        info_targets=[
            [2.5, 3],
            [3.6, 4.3],
            [3.6, 4.3],
            [2.5, 3]
            ],

        as_objective=False
            )
    
    sp.add_item_usage_constraints(
        min_usage=0,
        max_usage=2)
    
    sp.add_form_pair_constraints(
        min_overlap_prop=0.2,
        max_overlap_prop=0.2
    )
    
    #### add objective
    sp.write_problem("sample.lp")

    sp.solve_problem(        
        timeLimit=60,  # 2 minutes time limit
        gapRel=0.001, # relative gap of 1%
        gapAbs=0.001, # absolute gap of 1%
        msg=True,   # print the solver messages
        warmStart=False,    # do not use warm start
        solver="CBC")
    

    print(f"Delta is {sp.value(sp.delta)}")



    information_sum_form ={}
    items_selected = {}
    for r in range(sp.number_of_forms):
        weights_per_form_per_theta_point = [0 for i in range(len(sp.theta_points))]
        item_combined = []
        for i in range(sp.pool_size):
            if sp.value(sp.items[i][r])==1:
                selected_item = item_data.iloc[i]
                item_combined.append(selected_item)
                print( f"Form{r}:Item {selected_item.ItemID} from Set {selected_item.SetID} is selected with Domain {selected_item.Domain} and with Difficulty {selected_item.Difficulty}"  )
                
                for k in range(len(sp.theta_points)):
                    weights_per_form_per_theta_point[k]+=sp.information_all[k][i]
        items_selected[r]=pd.concat(item_combined,axis=1).T
        information_sum_form[r]=weights_per_form_per_theta_point    

        combined = pd.merge(items_selected[r],enemy_pairs,left_on="ItemID",right_on="ItemID",how="left")
        print(combined[["ItemID","EnemyID"]])
    


                

        
    