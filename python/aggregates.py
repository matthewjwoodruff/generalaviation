"""
Copyright (C) 2013 Matthew Woodruff

This script is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This script is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this script. If not, see <http://www.gnu.org/licenses/>.

===================================================================

aggregates.py
Implement aggregation for the GAA problem, from 27 performance 
criteria down to 9 min-max objectives or 1 non-preemptive goal
programming objective.
"""

import sys
import re

class Aggregates(object):
    def __init__(self):
        self.constraints = [
             75, 2200, 80, 2, 450,  None, -2000, None, None ,
             75, 2200, 80, 2, 475,  None, -2000, None, None ,
             75, 2200, 80, 2, 500,  None, -2000, None, None ]
        self.goals = [
             None, 1900, 60, None, 450, 41000, -2500, -17, -200,
             None, 1950, 60, None, 400, 42000, -2500, -17, -200,
             None, 2000, 60, None, 350, 43000, -2500, -17, -200 ]
        self.minimize = [1, 1, 1, 1, 1, 1, -1, -1, -1]

    def minmax(self, row):
        """
        Args: row is 27 responses in 3 groups of 9 (one for
            each of the 2, 4, and 6 seat aircraft)
        Returns: 9 minmax objectives
        """
        return [max(row[ii], row[ii+9], row[ii+18]) for ii in range(9)]

    def constr_violation(self, row):
        cv = 0
        for perf, constr, mini in zip(
                        row, self.constraints, self.minimize*3):
            if not constr: continue
            if mini > 0:
                violation = max((perf - constr) / constr, 0)
            else:
                violation = max((constr - perf) / constr, 0)
            cv += violation
        return cv

    def goal_attainment(self, row):
        # deviation function: (attained - goal) / attained for min
        #                     (goal - attained) / goal for max
        zed = 0
        for performance, goal, mini in zip(
                                row, self.goals, self.minimize*3):
            if not goal: continue
            if mini > 0:
                zed += max((performance - goal) / performance, 0)
            else:
                zed += max((goal - performance) / goal, 0)
        return zed

    def convert_row(self, row):
        return [xx * yy for (xx, yy) in zip(self.minimize*3, row)]

def run_aggregation():

    line = sys.stdin.readline()
    agg = Aggregates()

    while line:
        # read 27 responses from STDIN:
        # NOISE2 WEMP2 DOC2 ROUGH2 WFUEL2 PURCH2 RANGE2 LDMAX2 VCMAX2 
        # NOISE4 WEMP4 DOC4 ROUGH4 WFUEL4 PURCH4 RANGE4 LDMAX4 VCMAX4 
        # NOISE6 WEMP6 DOC6 ROUGH6 WFUEL6 PURCH6 RANGE6 LDMAX6 VCMAX6

        # convert line to row
        row = [float(xx) for xx in re.split("[\t ,]", line.strip())]
        # change all responses to minimization
        row = agg.convert_row(row)
        # get minmax objectives
        minmaxobjs = agg.minmax(row)
        # compute constraint violation
        cv = agg.constr_violation(row)
        # compute aggregate performance objective "zed"
        zed = agg.goal_attainment(row)
        outputline = [unicode(xx) for xx in minmaxobjs+[zed, cv]]
        print " ".join(outputline)

        line = sys.stdin.readline()

if __name__ == '__main__': run_aggregation()


# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
