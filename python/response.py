import sys
import re

class Response(object):
    def __init__(self):
        self.matrix = self.read_matrix("coefficient_matrix.txt")
        self.matrixoffsets = {"2":0,"4":9,"6":18}
        self.translate = [0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73]
        self.scale = [0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27]

    def read_matrix(self, filename):
        """
        It's worth remembering what the matrix is, exactly.
        Each row is the coefficients for a response.
        Each column is the DVs to which they apply.
        We're assuming that we're generating the design
        vector from the DVs in a consistent way:
        constant, linear terms, interactions, squares
        """
        with open(filename, 'rb') as fp:
            matrix_text = fp.read()
        lines = matrix_text.split("\n")
        lines.pop(0) # header

        matrix = []
        for line in lines:
            row = line.strip().split("\t")
            row.pop(0) # response name
            matrix.append([float(xx) for xx in row])

        return matrix

    def get_interactions(self, dvs):
        """
        Standard order for interactions:
        All interactions with the first dv, then all
        remaining interactions for the second dv, etc.
        """
        if len(dvs) == 0: return []
        interactions = self.get_interactions(dvs[1:])
        return [dvs[0]*dv for dv in dvs[1:]] + interactions

    def scale_dvs(self, dvs):
        translate_and_scale = lambda xx, yy, zz: (xx-yy)/zz
        return map(translate_and_scale, 
                    dvs, self.translate, self.scale)
        

    def design_vector(self, dvs):
        return [1] + dvs + self.get_interactions(dvs) + \
               [dv**2 for dv in dvs]

    def evaluate(self, dvs, pax):
        design = self.design_vector(self.scale_dvs(dvs))

        outputs = []
        # compute each response
        for jj in range(9):
            offset = jj + self.matrixoffsets[pax]
            response = sum(map(lambda xx, yy: xx * yy, 
                            design, self.matrix[offset]))
            outputs.append(response)
        return outputs

    def evaluate_wide(self, dvs):
        return self.evaluate(dvs[0:9], "2") \
               + self.evaluate(dvs[9:18], "4") \
               + self.evaluate(dvs[18:27], "6") 
               

def run_response():
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

    driver = Response()

    ndvs = 9 # 9 decision variables per aircraft
    totalndvs = ndvs * len(seats)

    nresp = 9 # 9 responses per aircraft
    respoffset = {"2":nresp*0,"4":nresp*1,"6":nresp*2}

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
        for seat in seats:
            # compute design vector from decision variables
            dvs = variables[0:ndvs]
            variables[0:ndvs] = []
            outputs += driver.evaluate(dvs, seat)

        # write response to stdout
        print "\t".join([unicode(xx) for xx in outputs])

        # get next line
        line = sys.stdin.readline()

if __name__ == '__main__': run_response()

# vim:ts=4:sw=4:expandtab:fdm=indent:ai
