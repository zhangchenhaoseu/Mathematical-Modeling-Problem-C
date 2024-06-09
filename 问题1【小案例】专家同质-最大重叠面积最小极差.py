
# 靡不有初，鲜克有终
# 开发时间：2023/7/11 12:14
from gurobipy import *

# 小案例：20个作品，4个专家，每个作品需要2名专家进行评审
# 建立作品集合和专家集合的数据结构
works_num = 20
expert_num = 10
requirement = 2
review_num = works_num*requirement/expert_num

works_index = [i for i in range(0, works_num)]  # 作品集合
expert_index = [j for j in range(0, expert_num)]  # 专家集合
y_index = [i for i in range(len(expert_index))]  # 用来存放每一列（每一个专家）对应的数量（作品数量）

# 建立gurobi里变量x的tuplelist
variables_lst = []
for i in works_index:
    for j in expert_index:
        variables_lst.append((i, j))
print(variables_lst)
variables = tuplelist(variables_lst)
print(variables)

# 建立gurobi里变量j，k的tuplelist
jk_lst = []
for i in expert_index:
    for j in expert_index:
        if i !=j:
            jk_lst.append((i, j))
print(jk_lst)


# 定义模型
m = Model('shumo2')

# 定义变量
c = m.addVar(lb=0.0, vtype=GRB.INTEGER, name='c')
max_r = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='max_r')
min_r = m.addVar(lb=0.0, vtype=GRB.CONTINUOUS, name='min_r')

x = m.addVars(len(works_index), len(expert_index), vtype=GRB.BINARY, name='x')
y = m.addVars(y_index, vtype=GRB.CONTINUOUS, lb=0.0, name='y')  # y变量是每一列的1的数量
m.update()
print(x)
print(y)

# 定义目标函数(双目标,多目标函数默认的优化方向是最小化)
m.setObjectiveN(-c, index=0, weight=0.1, name='Obj1')  # 最大化覆盖面积
m.setObjectiveN(max_r-min_r, index=1, weight=0.1, name='Obj2')  # 最小化极差

# 定义约束条件
m.addConstrs((quicksum(x[i, j] for i, j in variables.select(w, '*')) == requirement for w in works_index), '-')
# m.addConstrs((quicksum(x[i, j] for i, j in variables.select('*', e)) == review_num for e in expert_index), '-')
m.addConstrs((quicksum(x[i, j]*x[i, k] for i in works_index) >= c for j, k in jk_lst), '-')
m.addConstrs((quicksum(x[i, j] for i in works_index) <= y[j] for j in expert_index), '-')
m.addConstrs((quicksum(x[i, j] for i in works_index) >= y[j] for j in expert_index), '-')
m.addConstrs((max_r >= y[j] for j in expert_index), '-')  # 取每一列最大的数量，即含1最多的
m.addConstrs((min_r <= y[j] for j in expert_index), '-')  # 取每一列最小的数量，即含1最少的

# 求解
m.optimize()

# 保存展示结果
m.write('shumo2.lp')
var_lst = m.getVars()
for i in var_lst:
    if i.X != 0:
        print(i.VarName, ':', i.X)
print("目标函数值为：", m.ObjVal)
