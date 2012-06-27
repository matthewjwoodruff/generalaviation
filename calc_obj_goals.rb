require 'yaml'

class ObjectiveCalculator
  def initialize(paramfilename)
    read_config(paramfilename)
    read_datafile
    @objective_function = ObjectiveFunction.new
  end

  def read_config(paramfilename)
    # read configuration file
    parameters = YAML.load_file paramfilename
    @header = parameters[:header]
    @infilename = parameters[:inputfile]
    @outfilename = parameters[:outputfile]
    @dv_indices = []
    @header.each_index do |cc|
      @dv_indices << cc if(@header[cc][:decision]) 
    end
  end

  def read_datafile
    # create table to hold data
    @table = Array.new
    @nilrows = 0

    # read the data file into a table in memory
    if(!File.exist?(@infilename))
      raise "Could not find input file #{@infilename}"
    end
    File.open(@infilename, 'rb') do |fp|
      # no need to skip past header; we're checking every row for nulls, and dropping any row where they're found
      rex = /^[-+]?(([0-9]*\.?[0-9]+)|([0-9]+\.?[0-9]*))([eE][-+]?[0-9]+)?$/
      counter = 0
      while(line = fp.gets)
        nils = 0
        row = line.chomp.split("\t").collect do |element|
          if(rex =~ element) 
            element = element.to_f
          else 
            element = nil 
            nils += 1 
          end
        end

        # check for an invalid short row
        if(row.size < @header.size) then nils = @header.size end

        row = row[0... @header.size] #just the columns we care about
        if(nils == 0) then @table.push row
        else 
          #puts "nils found on line #{counter}"
          @nilrows += 1 
        end
        counter += 1
      end
    end
  end

  def report
    case @nilrows
    when 0 
      puts "0 rows with non-float elements.  You didn't have a header?"
    when 1 
      puts "1 row with non-float elements.  Was that your header?"
    else 
      puts "#{@nilrows} nil rows.  You may want to check your data."
    end
  end

  # extract the decision variables from a row
  def dvs(row)
    @dv_indices.collect{|cc| row[cc]}
  end

  def calc_objectives(row)
    objectives = @objective_function.evaluate(dvs(row))
  end

  def run
#    puts "table row"
#    puts @table[0].join("\t")
#    calc_objectives(@table[0])
    counter = 0
    result = @table.collect do |row|
      counter += 1
      smallrow = Array.new
      @header.each_index do |ii|
        smallrow << row[ii] if(!@header[ii][:goal])
      end
       
#      begin
        val = smallrow + calc_objectives(row)
#      rescue
#        raise "failed at row #{counter}"
#      end
      val
    end

    File.open(@outfilename, 'wb') do |fp|
      @header.each do |col| 
        # exclude the original objectives, now that we've verified them
        fp << col[:name] << "\t" if(!col[:goal])
      end
      objectives = "NOISE WEMP DOC ROUGH WFUEL PURCH RANGE LDMAX VCMAX".split(" ")
      objective_names = Array.new
      [2,4,6].each do |seat|
        objective_names += objectives.collect{|word| word+seat.to_s}
      end
      fp << objective_names.join("\t")
      fp << "\t"
      fp << (objectives + ["pfpf", "zed", "cv"]).join("\t") 
      fp << "\t"
      goal_names = objective_names.reject{|word| /(NOISE)|(ROUGH)/ =~ word}.collect{|word| word+"_attained"}
      fp << goal_names.join("\t")
      fp << "\n"
      result.each do |row|
        fp.puts row.join("\t")
      end
    end
  end
end

class ObjectiveFunction
  def initialize
    @mat = matrix
    @header = "NOISE WEMP DOC ROUGH WFUEL PURCH RANGE LDMAX VCMAX pfpf zed".split
    @objectives = @header[0..8]
    @seats = [2,4,6]
    @goals = 
      [[1900,60,450,41000,2500,17,200],
       [1950,60,400,42000,2500,17,200],
       [2000,60,350,43000,2500,17,200] ]
    @constraints = [[75, 2200, 80, 2, 450,  nil, 2000, nil, nil ],
                    [75, 2200, 80, 2, 475,  nil, 2000, nil, nil ],
                    [75, 2200, 80, 2, 500,  nil, 2000, nil, nil ]]
    @constrained = [true, true, true, true, true, false, true, false, false]
    @max = [false, false, false, false, false, false, true, true, true]
  end

  def matrix
    mat = File.read("coefficient_matrix.txt")
    # convert to a table
    mat = mat.split("\n").collect do |line|
      row = line.split("\t")
      row.collect!{|entry| entry.strip}
    end
    # convert numbers from strings to floats
    mat.each_index do |rr|
      # skip the first row
      next if rr==0
      row = mat[rr]
      row.each_index do |cc|
        # skip the first column
        next if cc == 0
        # do the conversion
        row[cc] = row[cc].to_f
      end
    end
    mat[1...(mat.size )] #return the matrix, minus the blank rows
  end

  # get the coefficients for the objective / seat
  def coeffs(objective, seat)
    tofind = "#{objective}#{seat}"
    #ii = @mat.find_index {|row| row[0] == tofind}
    temp = []
    @mat.each {|row| temp << row[0]}
    ii = temp.index(tofind)
    raise "couldn't find #{objective}#{seat}" if !ii
    @mat[ii][1...(@mat[ii].size)]
  end

  def deviation_function(attained, goal, max)
    #puts "attained #{attained}, goal #{goal}, max #{max}"
    if(max) then val = -(attained - goal)/goal 
    # change denominator form minimization to attained for strict version
    else  val = (attained - goal) / attained end
    val = 0 if(val < 0) 
    val
  end

  def difference_metric(performance)
    # calculate the difference metric
    zed = 0
    goal_having_performance_metrics = performance.collect do |row| 
      [1,2,4,5,6,7,8].collect { |index| row[index]}
    end
    max = [1,2,4,5,6,7,8].collect { |index| @max[index]}
    #puts "max: #{max.join "\t"}"
    goal_having_performance_metrics.each_index do |ss|
      #puts "row size #{goal_having_performance_metrics[ss].size}"
      goal_having_performance_metrics[ss].each_index do |oo|
        zed += deviation_function(goal_having_performance_metrics[ss][oo], @goals[ss][oo], max[oo])
      end
    end
    zed
  end

  def goals_attained(performance)
    goal_having_performance_metrics = performance.collect do |row| 
      [1,2,4,5,6,7,8].collect { |index| row[index]}
    end
    max = [1,2,4,5,6,7,8].collect { |index| @max[index]}
    attained = Array.new
#puts "ss\too\tmax\tmetric\tgoal\tattained"
    goal_having_performance_metrics.each_index do |ss|
      attained << Array.new
      goal_having_performance_metrics[ss].each_index do |oo|
        if(max[oo] && goal_having_performance_metrics[ss][oo] - @goals[ss][oo] > 0)
          attained[ss][oo] = 1
        elsif(!max[oo] && @goals[ss][oo] - goal_having_performance_metrics[ss][oo] > 0)
          attained[ss][oo] = 1
        else attained[ss][oo] = 0
        end
#puts "#{ss}\t#{oo}\t#{max[oo]}\t#{goal_having_performance_metrics[ss][oo]}\t#{@goals[ss][oo]}\t#{attained[ss][oo]}"
      end
    end
#		attained.inject(0) do |total, row|
#      total += row.inject(0) do |subtotal, val|
#        subtotal += val
#      end
#    end
    attained
  end
        
    

  # this PFPF is specifically for 9 design variables across three
  # desings, in 3x9 array
  def pfpf(xreal)
    averages = (0...9).collect do |jj|
      (xreal[0][jj] + xreal[1][jj] + xreal[2][jj]) / 3
    end
    #puts "averages: #{averages.join "\t"}"
    mse = (0...9).collect do |jj|
      ((xreal[0][jj]-averages[jj])**2 +
      (xreal[1][jj]-averages[jj])**2 +
      (xreal[2][jj]-averages[jj])**2 ) /2 
    end
    #puts "mse: #{mse.join "\t"}"
    errors = Array.new
    mse.each_index do |jj|
      errors[jj] = mse[jj] ** 0.5 / averages[jj]
    end
    #puts "errors: #{errors.join "\t"}"
    # variance / sum of euclidean distances
    pf = errors.inject(0) do |total, ee|
      total += ee; total
    end
    #puts "pf: #{pf}"
    pf
  end

  def pfpf_new(xreal)
    total = 0
    9.times do |obj|
      mean = (xreal[0][obj] + xreal[1][obj] + xreal[2][obj])/3
      total += (xreal[0][obj] - mean) ** 2 +
               (xreal[1][obj] - mean) ** 2 +
               (xreal[2][obj] - mean) ** 2
    end
    total ** 0.5
  end

  # the objective function works on scaled DVs
  def scale_dvs(xreal)
    translate = [0.36, 9, 3, 5.734, 22, 97.5, 17, 3.375, 0.73]
    scale = [0.12, 2, 3, 0.234, 3, 12.5, 3, 0.375, 0.27]
    temp = [[],[],[]]

    (0...3).each do |ii|
      (0...9).each do |jj|
        raise "no decision variable! #{ii},#{jj}" if !xreal[ii][jj]
        temp[ii][jj] = (xreal[ii][jj] - translate[jj]) / scale[jj]
      end
    end
    temp
  end

  # transform the decision variables into the objectives
  def response(xreal)
    # first augment the array of DVs with interactions, squared terms, and a constant term
    xreal.each_index do |ii|
      dvs = xreal[ii]
      interactions = Array.new
      (0...(dvs.size-1)).each do |jj|
        (jj+1...dvs.size).each do |kk|
          interactions.push dvs[jj]*dvs[kk]
        end
      end
      squares = dvs.collect{|xx| xx ** 2 }
      dvs += interactions
      dvs += squares
      dvs.unshift 1 # prepend constant term
      xreal[ii] = dvs
    end

    # initialize the response
    resp = @seats.collect { Array.new }

    # do matrix multiplication to get the objectives
    @seats.each_index do |ss|
      @objectives.each_index do |oo|
        # get the coeffs for that objective and that number of seats
        coe = coeffs(@objectives[oo],@seats[ss])
        accumulator = 0
        # do the actual multiplication
        coe.each_index do |cc|
          raise "xreal[#{ss}][#{cc}] is nil!" if !xreal[ss][cc]
          raise "coe[#{cc}] is nil!" if !coe[cc]
          accumulator += xreal[ss][cc] * coe[cc]
        end
        # write the result to the accumulator array
        resp[ss][oo] = accumulator
      end
    end

    resp
  end

  def print_xreal(xreal)
    puts "xreal..."
    xreal.each do |row|
      puts row.join("\t")
    end
  end

  def constraint_violation(performance)
    cvs = Array.new
    @constraints.each_index do |ii|
      cvs[ii] = Array.new
      @constraints[ii].each_index do |jj|
        if(!@constrained[jj])
          cvs[ii][jj] = 0.0
          next
        end
				if(@max[jj])
					cvs[ii][jj] = (@constraints[ii][jj] - performance[ii][jj])/@constraints[ii][jj]
				else
					cvs[ii][jj] = (performance[ii][jj] - @constraints[ii][jj])/@constraints[ii][jj]
				end
				cvs[ii][jj] = [cvs[ii][jj], 0.0].max
      end
    end
    cv = 0
    cvs.each do |row|
      row.each do |val|
        cv += val
      end
    end
    #cv = 0 if cv < 0.03 
    cv
  end

  def evaluate(decision_variables)
    xreal = Array.new
    xreal = [decision_variables[0..9], decision_variables[9..18], decision_variables[18..27]]
    # pfpf is on the UNSCALED version
    # the computation breaks if we have negative numbers
    #pvars = pfpf(xreal) 
    xreal = scale_dvs(xreal)

    pvars = pfpf_new(xreal)

    # get the 27 performance measures
    performance = response(xreal)

    #performance.each do |seat|
    #  puts seat.join("\t")
    #end

    zed = difference_metric(performance)
    #puts "zed #{zed}"

    # calculate the minmax / maxmin objectives
    # and flip the sign of the max objectives
    maxmin = (0..8).collect do | index |
      choosefrom = [performance[0][index], performance[1][index], performance[2][index]]
      if(@max[index])
        choosefrom.collect!{|val| -val}
      end

     #puts "choosing from #{choosefrom.join ", "}"
      #puts "max is #{choosefrom.max}"
      #puts "min is #{choosefrom.min}"
      choosefrom.max
    end

    # calculate the constraint violation
    cv = constraint_violation(performance)

    # compute the number of goals attained
    attained = goals_attained(performance)

    #puts "maxmin: #{maxmin.join("\t")}"
    ret = performance[0]+performance[1]+performance[2]+maxmin+[pvars,zed, cv] +  attained

  end
end


if(ARGV.size < 1) 
  raise "\nUSAGE: ruby #{$0} <configuration_file.yml>\n"
end
raise "Could not find parameter file #{ARGV[0]}" if !File.exist?(ARGV[0])

oc = ObjectiveCalculator.new(ARGV[0])
oc.report
oc.run

# based on the decision variables, calculate the objectives

# write to output file

# profit!!!!
