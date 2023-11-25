# %%
import numpy as np
import pandas as pd
import pulp as p

# %%
#Load the data
# digi_data = pd.read_excel("budget_alloc_testdata.xlsx", sheet_name='PT')
# digi_data.head(20)

# %%
#LP Budget Allocation Problem

lp_model = p.LpProblem("Budget_Allocation", p.LpMaximize)




# %%
#Define decision variables for each marketing channel
#brand_x1, nonbrand_x2, value_x3 cannot = 0
brand_x1 = p.LpVariable("Brand", lowBound=0)
nonbrand_x2 = p.LpVariable("Nonbrand", lowBound=0)
value_x3 = p.LpVariable("Value", lowBound=0)


# %%
#Objective Function Value
#Note in this example we know the return of each activity.
#Replace weights with conversions or conversion rate metric
lp_model += 1*brand_x1 + 2*nonbrand_x2 + 3*value_x3

# %%
#Constraints e.g
#Note #brand_x1, nonbrand_x2, value_x3 cannot = 0
#In this example total budget is 20,000/month and brand budget must be greater than 8K, 
#nonbrand and value must be greater than 3K
lp_model += brand_x1 + nonbrand_x2 + value_x3 <= 20000
lp_model += brand_x1 >= 5000
lp_model += nonbrand_x2 >= 3000
lp_model += value_x3 >= 1000

# %%
#Display the LP Allocation Problem
print(lp_model)

# %%
#Solve the problem
lp_Solution = lp_model.solve()
print("Solution:", p.LpStatus[lp_Solution])

# %%
#Print the result of the model
print("Solution:", p.LpStatus[lp_Solution])
print("Optimal budget allocation:")
for v in lp_model.variables():
    print(v.name, "=", v.varValue)
print("Optimal objective value: $", -p.value(lp_model.objective))

# %%



