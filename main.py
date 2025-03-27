from pulp import *
import pandas as pd
from utility import *

## provide sample data
## add enemy constraints there
##TODO add CPLEX solver
##TODO pairwise maximization
##TODO make it a plot for information and SE
##TODO provide sample code
##TODO make it publicly available in Github

class form_assembly_problem:

    # init method or constructor
    def __init__(self, minimize=True):
        if minimize:
            self.__prob = LpProblem("Form Assembly Minimize",LpMinimize)
        else:
            self.__prob = LpProblem("Form Assembly Maximize",LpMaximize)
        
        self.__number_of_items_per_form = 0
        self.__number_of_forms = 0
        self.__pool_size = 0
        self.__items = None
        self.__delta = None

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
            raise f"The irt_a_column {irt_a_column} doesn't exist in the item pool"
        self.__irt_a_column=irt_a_column
    
    ### get irt_b_column
    @property
    def irt_b_column(self):
        return self.__irt_b_column
    
    ##### set irt_b_column
    @irt_b_column.setter
    def irt_b_column(self,irt_b_column):
        if irt_b_column not in self.__pool.columns:
            raise f"The irt_b_column {irt_b_column} doesn't exist in the item pool"
        self.__irt_b_column=irt_b_column
        
    
    ### get irt_c_column
    @property
    def irt_c_column(self):

        return self.__irt_c_column
    
    ##### set irt_c_column
    @irt_c_column.setter 
    def irt_c_column(self,irt_c_column):
        if irt_c_column not in self.__pool.columns:
            raise f"The irt_c_column {irt_c_column} doesn't exist in the item pool"
        # fill na values with 0 for irt_c
        self.__pool[irt_c_column]=self.__pool[irt_c_column].fillna(0)
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
    def create_item_by_form_variables(self):
        self.__items = LpVariable.dicts("Item", (range(self.__pool_size),range(self.__number_of_forms)), cat="Binary")
    
    ### creating set by form variables
    def create_set_by_form_variables(self,number_of_sets):
        return LpVariable.dicts("Set", (range(number_of_sets),range(self.__number_of_forms)), cat="Binary")
    
    ### creating delta variables for min and max method
    def create_delta_variables(self):
        self.__delta = LpVariable("Delta", 0, None, LpContinuous)
    
    ### add information constraints based on theta points
    def add_information_based_on_theta_points(self,theta_points,info_targets):
        self.__theta_points=theta_points
        self.__info_targets=info_targets
        if len(theta_points)!=len(info_targets):
            raise "The length of theta_points and info_targets are different"

        for i,theta in enumerate(theta_points):
            information = [fisher_info(x[0],x[1],x[2],theta,D=1.702) for x in self.__pool[[self.__irt_a_column,self.__irt_b_column,self.__irt_c_column]].values]
            self.__information_all.append(information)
            self.add_information_constraints(
                information=information,
                target=info_targets[i],
                name=f"theta{theta}")
        
    def add_information_constraints(self,information,target,name):
        if len(information)!=self.__pool_size:
            raise "The information length is different from the pool size"
        
        for r in range(self.__number_of_forms):
            self.__prob += (lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]+self.__delta) >= target,f"form{r}_{name}_plus_delta")
            self.__prob += (lpSum([self.__items[i][r]*information[i] for i in range(self.__pool_size)]-self.__delta) <= target,f"form{r}_{name}_minus_delta")

  

    
    ##### add content constraints
    def add_content_constraints(self,constraints,target,direction,name):
        if len(constraints)!=self.__pool_size:
            raise "The content constraints length is different from the pool size"
        direction_selection={
            "==":LpConstraintEQ,
            ">=":LpConstraintGE,
            "<=":LpConstraintLE
        }
        for r in range(self.__number_of_forms):
            self.__prob += LpConstraint(
                e=lpSum([self.__items[i][r]*constraints[i] for i in range(self.__pool_size)]),
                sense=direction_selection[direction],
                rhs=target,
                name=f"form{r}_{name}_direction{direction_selection[direction]}")
    
    ### add enemy constraints
    def add_enemy_constraints(self,enemy_pairs,itemid_column,enemyid_column):
        ## Check if the itemID and enemyID columns exist in the enemy_pairs
        if itemid_column not in enemy_pairs.columns:
            raise f"The itemid_column {itemid_column} doesn't exist in the enemy_pairs"
        
        if enemyid_column not in enemy_pairs.columns:
            raise f"The enemyid_column {enemyid_column} doesn't exist in the enemy_pairs"

        ## For enemy_pairs dataset, order ItemID and EnemyID based on the alphabetical order and combine them to create pairs
        all_enemy_pairs = enemy_pairs.apply(lambda x: sorted([x[itemid_column],x[enemyid_column]]) , axis=1).tolist()

        ### Get unique pairs
        all_enemy_pairs_unique = {}
        for enemy_pair in all_enemy_pairs:
            pair="&".join(enemy_pair)
            all_enemy_pairs_unique[pair]=enemy_pair
    

        for pair_name,enemy_pair in all_enemy_pairs_unique.items():
            enemy_pair_constraint = [1 if x in enemy_pair else 0 for x in self.__pool[self.__item_id_column]]
            if sum(enemy_pair_constraint)>1:
                for r in range(self.__number_of_forms):
                    self.__prob += (lpSum([self.__items[i][r]*enemy_pair_constraint[i] for i in range(self.__pool_size)]) <= 1,f"Form{r}: Enemy pairs {pair_name}_constraints")
        

    #### constrain number of items within a set
    def add_set_constraints(self,set_id_column,number_of_items_per_set):
        if set_id_column not in self.__pool.columns:
            raise f"The set_id_column {set_id_column} doesn't exist in the item pool"
        
        set_ids = self.__pool[set_id_column].unique()
        set_ids = [x for x in set_ids if pd.isna(x)==False]

        setvariables = self.create_set_by_form_variables(
            number_of_sets=len(set_ids))

        for k,set_id in enumerate(set_ids):
            set_constraint = [1 if x==set_id else 0 for x in self.__pool[set_id_column]]
            for r in range(self.__number_of_forms):
                self.__prob += (lpSum([self.__items[i][r]*set_constraint[i] for i in range(self.__pool_size)]-setvariables[k][r]*number_of_items_per_set) == 0,f"Form{r}: Set id {set_id}_constraints")
    



    ##### add content constraints by using column name and values
    def add_content_constraints_by_column(self,column_name,values_range):
        # self.__pool = self.__pool[[self.__item_id_column,column_name]]
        if column_name not in self.__pool.columns:
            raise f"The set_id_column {column_name} doesn't exist in the item pool"
        
        for key,value in values_range.items():
            constraint = [1 if x==key else 0 for x in self.__pool[column_name]]
            self.add_content_constraints(constraint,value[0],">=",key)
            self.add_content_constraints(constraint,value[1],"<=",key)
     


    def add_item_usage_constraints(self,min_usage,max_usage):
        for i in range(self.__pool_size):
            self.__prob += (lpSum([self.__items[i][r] for r in range(self.__number_of_forms)]) >= min_usage,f"item{i}_usage_minimum")
            self.__prob += (lpSum([self.__items[i][r] for r in range(self.__number_of_forms)]) <= max_usage,f"item{i}_usage_maximum")
    


    ##### add 
    def add_objective(self):
        self.__prob += lpSum(self.__delta)

    ##### solve
    def solve_problem(self,
                      timeLimit=60,
                      gapRel=0.01,
                      gapAbs=0.01,
                      msg=True):
        self.__prob.solve(pulp.PULP_CBC_CMD(
            timeLimit=timeLimit,
            gapRel=gapRel,
            gapAbs=gapAbs,
            msg=msg))
        # self.__prob.solve(pulp.PULP_CBC_CMD(timeLimit=60,gapRel=0.01,gapAbs=0.01,msg=True))
        print("Status:", LpStatus[self.__prob.status])
    
    #### write out the LP function
    def write_problem(self,full_file_path):
        self.__prob.writeLP(full_file_path)
    
    



if __name__ == "__main__":
    item_file_location = r"C:\Users\yfu\Box\Yfu\Conference\NCME 2025\ATA\ATA_Python\sample\sample_items_for_ATA.xlsx"
    item_data = pd.read_excel(item_file_location)
    # item_data2 = item_data.sample(n=300).copy()

    enemy_file_location = r"C:\Users\yfu\Box\Yfu\Conference\NCME 2025\ATA\ATA_Python\sample\sample_enemy_pairs_for_ATA.xlsx"
    enemy_pairs = pd.read_excel(enemy_file_location)

   
    domain_column = "Domain"
    domain_values_range = {"Domain_A":[7,7],
                          "Domain_B":[3,3]}
    


    difficulty_column = "Difficulty"
    difficulty_values_range = {"Easy":[3,3],
                         "Medium":[4,4],
                         "Hard":[3,3]
    }

    #### Create a problem
    sp = form_assembly_problem(minimize=True)
    sp.pool = item_data
    sp.number_of_forms = 3
    sp.number_of_items_per_form=10
    sp.create_item_by_form_variables()
    sp.create_delta_variables()
    sp.item_id_column="ItemID"
    sp.irt_a_column = "IRT_a"
    sp.irt_b_column = "IRT_b"
    sp.irt_c_column = "IRT_c"

    sp.add_information_based_on_theta_points(
        theta_points= [
            -0.6,
            -0.4,
            0.2,
            0.4],
        info_targets=[
            2.7,
            4,
            4,
            2.7])

    sp.add_content_constraints_by_column(
        column_name=domain_column,
        values_range=domain_values_range)
    
    sp.add_content_constraints_by_column(
        column_name=difficulty_column,
        values_range=difficulty_values_range)

    sp.add_set_constraints(
        set_id_column="SetID",
        number_of_items_per_set=3)
    sp.add_enemy_constraints(
        enemy_pairs=enemy_pairs,
        itemid_column="ItemID",
        enemyid_column="EnemyID"
    )
    

    sp.add_item_usage_constraints(
        min_usage=0,
        max_usage=1)
    
    #### add objective
    sp.add_objective()
    # sp.write_problem("sample.lp")

    sp.solve_problem(        
        timeLimit=360,
        gapRel=0.01,
        gapAbs=0.01,
        msg=True)


    print(f"Delta is {value(sp.delta)}")

    #### add constraitns
    # sp.add_content_constraints(constraints=difficulty_level_easy,target=3,name="easy")
    # sp.add_content_constraints(constraints=difficulty_level_medium,target=4,name="medium")
    # sp.add_content_constraints(constraints=difficulty_level_hard,target=3,name="hard")

    # sp.add_information_constraints(item_weights,3,"information")

    information_sum_form ={}
    items_selected = {}
    for r in range(sp.number_of_forms):
        weights_per_form_per_theta_point = [0 for i in range(len(sp.theta_points))]
        item_combined = []
        for i in range(sp.pool_size):
            if value(sp.items[i][r])==1:
                selected_item = item_data.iloc[i]
                item_combined.append(selected_item)
                print( f"Form{r}:Item {selected_item.ItemID} from Set {selected_item.SetID} is selected with Domain {selected_item.Domain} and with Difficulty {selected_item.Difficulty}"  )
                
                for k in range(len(sp.theta_points)):
                    weights_per_form_per_theta_point[k]+=sp.information_all[k][i]
        items_selected[r]=pd.concat(item_combined,axis=1).T
        information_sum_form[r]=weights_per_form_per_theta_point    

        combined = pd.merge(items_selected[r],enemy_pairs,left_on="ItemID",right_on="ItemID",how="left")
        print(combined[["ItemID","EnemyID"]])
                

        
    