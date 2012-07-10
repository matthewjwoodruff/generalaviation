import sys
import re

def read_matrix(filename):
  fp = open("coefficient_matrix.txt", 'rb')
  matrix_text = fp.read()
  fp.close()
  lines = matrix_text.split("\n")
  lines.pop(0) # header

  matrix = []
  for line in lines:
    row = line.strip().split("\t")
    row.pop(0) # response name
    matrix.append([float(xx) for xx in row])

  return matrix

# determine which seats to compute
seats = [ss for ss in sys.argv if
         ss in ['2','4','6']]

if len(seats) == 0:
  message = "  usage: python response.py [2] [4] [6]"
  message += "\n  must specify a number of seats"
  message += "\n  examples:"
  message += "\n  python response.py 6"
  message += "\n  python response.py 2 4 6"
  print message
  exit(1)

# read the matrix
matrix = read_matrix("coefficient_matrix.txt")

ndvs = 9
totalndvs = ndvs * len(seats)

# main loop
line = sys.stdin.readline()
while line:
  # take dvs from stdin
  variables = [float(xx) for xx in 
               re.split("[ ,\t]", line.strip())]
  
  if(totalndvs != len(variables)):
    print "Defective inputs!  Got {}, expected {}.".format(
      len(variables), totalndvs)
    exit(1)

  outputs = []
  # for each number of seats
  for ii in range(len(seats)):

    # compute design from decision variables

    # compute response

  # write response to stdout

  # get next line
