import sys 
import re

class PFPF(object):
    def __init__(self):
        self.translate = [
                    0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73]
        self.scale = [0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27]

    def pfpf(self, row):
        row = [(xx-tr)/sc for xx, tr, sc 
               in zip(row, self.translate*3, self.scale*3)]
        # compute averages
        means = [(row[ii] + row[ii+9] + row[ii+18])/3 
                 for ii in range(9)]
        sqdiff = [(row[ii] - means[ii]) ** 2 +
                  (row[ii+9] - means[ii]) ** 2 +
                  (row[ii+18] - means[ii]) ** 2
                  for ii in range(9)]
        return sum(sqdiff) ** 0.5
        
def run_aggregation():
    pfpf = PFPF()
    line = sys.stdin.readline()

    while line:
        # convert line to row
        row = [float(xx) for xx in re.split("[\t ,]", line.strip())]
        print pfpf.pfpf(row)
        line = sys.stdin.readline()

if __name__ == '__main__': run_aggregation()

# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
