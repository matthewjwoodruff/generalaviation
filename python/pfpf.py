import sys 
import re

translate = [0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73]
scale = [0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27]

counter = 0
line = sys.stdin.readline()

while line:
    counter += 1
    # convert line to row
    row = [float(xx) for xx in re.split("[\t ,]", line.strip())]
    row = [(xx-tr)/sc for xx, tr, sc 
           in zip(row, translate*3, scale*3)]
    # compute averages
    means = [(row[ii] + row[ii+9] + row[ii+18])/3 
             for ii in range(9)]
    sqdiff = [(row[ii] - means[ii]) ** 2 +
              (row[ii+9] - means[ii]) ** 2 +
              (row[ii+18] - means[ii]) ** 2
              for ii in range(9)]
    pfpf = sum(sqdiff) ** 0.5
    print pfpf
    line = sys.stdin.readline()

sys.stderr.write("count: {}".format(counter))
# vim:ts=4:sw=4:expandtab:fdm=indent:ai:colorcolumn=68
