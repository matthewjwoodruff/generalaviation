import re
import math
import sys

lline = None
rline = None
header = None

biggestdifference = []

if len(sys.argv) < 3: print "boo!"; exit(1)

with open(sys.argv[1], 'rb') as left:
    with open(sys.argv[2], 'rb') as right:
        # header = re.split("[\t ,]", left.readline().strip())
        
        lline = left.readline()
        rline = right.readline()
        biggestdifference = [(0,0) for _ in re.split("[\t ,]", lline)]
        counter=1
        while lline and rline:
            if counter % 10000 == 0:
                print counter, ["{0:.1f}".format(math.log10(xx) )
                                for _, xx in biggestdifference]
            rrow = [float(xx) for xx 
                    in re.split("[\t, ]", lline.strip())]
            prow = [float(xx) for xx
                    in re.split("[\t, ]", rline.strip())]
            difference = [abs(xx - yy) for xx, yy 
                          in zip(rrow, prow)]
            for ii in range(len(difference)):
                if difference[ii] > biggestdifference[ii][1]:
                    biggestdifference[ii] = (counter, difference[ii])
            lline = left.readline()
            rline = right.readline()
            counter += 1
        if lline: print "left had leftover lines"
        if rline: print "right had leftover lines"

print "final: ", ["{0:.1f}".format(math.log10(xx)) 
                  for _, xx in biggestdifference]
