import sys
import re

def minmax(row):
    """
    Args: row is 27 responses in 3 groups of 9 (one for
        each of the 2, 4, and 6 seat aircraft)
    Returns: 9 minmax objectives
    """
    return [max(row[ii], row[ii+9], row[ii+18]) for ii in range(9)]

global constraints
constraints = [75, 2200, 80, 2, 450,  None, -2000, None, None ,
               75, 2200, 80, 2, 475,  None, -2000, None, None ,
               75, 2200, 80, 2, 500,  None, -2000, None, None ]
def constr_violation(row):
    global constraints
    cv = 0
    for perf, constr in zip(row, constraints):
        if constr: 
            violation = max((perf - constr) / constr, 0)
            cv += violation
    return cv

global goals
goals = [None, 1900, 60, None, 450, 41000, -2500, -17, -200,
         None, 1950, 60, None, 400, 42000, -2500, -17, -200,
         None, 2000, 60, None, 350, 43000, -2500, -17, -200 ]
def goal_attainment(row):
    global goals
    global minimize
    # deviation function: (attained - goal) / attained for min
    #                     (goal - attained) / goal for max
    zed = 0
    for performance, goal, mini in zip(row, goals, minimize*3):
        if not goal: continue
        if mini > 0:
            zed += max((performance - goal) / performance, 0)
        else:
            zed += max((goal - performance) / goal, 0)
    return zed

line = sys.stdin.readline()
global minimize
minimize = [1, 1, 1, 1, 1, 1, -1, -1, -1]

while line:
    # read 27 responses from STDIN:
    # NOISE2 WEMP2 DOC2 ROUGH2 WFUEL2 PURCH2 RANGE2 LDMAX2 VCMAX2 
    # NOISE4 WEMP4 DOC4 ROUGH4 WFUEL4 PURCH4 RANGE4 LDMAX4 VCMAX4 
    # NOISE6 WEMP6 DOC6 ROUGH6 WFUEL6 PURCH6 RANGE6 LDMAX6 VCMAX6

    # convert line to row
    row = [float(xx) for xx in re.split("[\t ,]", line.strip())]
    # change all responses to minimization
    row = [xx * yy for (xx, yy) in zip(minimize*3, row)]
    # get minmax objectives
    minmaxobjs = minmax(row)
    # compute constraint violation
    cv = constr_violation(row)
    # compute aggregate performance objective "zed"
    zed = goal_attainment(row)
    outputline = [unicode(xx) for xx in minmaxobjs+[zed, cv]]
    print " ".join(outputline)

    line = sys.stdin.readline()

# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
