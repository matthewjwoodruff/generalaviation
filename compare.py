import re
import math

rline = None
pline = None
header = None

biggestdifference = []

with open('ruby_responses.txt', 'rb') as ruby:
    with open('python.txt', 'rb') as pyth:
        header = re.split("[\t ,]", ruby.readline().strip())
        biggestdifference = [(0,0) for _ in header]
        
        rline = ruby.readline()
        pline = pyth.readline()
        counter=1
        while rline and pline:
            if counter % 10000 == 0:
                print counter, ["{0:.1f}".format(math.log10(xx) )
                                for _, xx in biggestdifference]
            rrow = [float(xx) for xx 
                    in re.split("[\t, ]", rline.strip())]
            prow = [float(xx) for xx
                    in re.split("[\t, ]", pline.strip())]
            difference = [abs(xx - yy) for xx, yy 
                          in zip(rrow, prow)]
            for ii in range(len(difference)):
                if difference[ii] > biggestdifference[ii][1]:
                    biggestdifference[ii] = (counter, difference[ii])
            rline = ruby.readline()
            pline = pyth.readline()
            counter += 1
        if rline: print "ruby had leftover lines"
        if pline: print "python had leftover lines"

print "final: ", ["{0:.1f}".format(math.log10(xx)) 
                  for _, xx in biggestdifference]
