rex = /^[-+]?(([0-9]*\.?[0-9]+)|([0-9]+\.?[0-9]*))([eE][-+]?[0-9]+)?$/
line = "73.2718282539098	1878.07329363553	61.9778594068574	2.000408334	0.0	0.0	0.0	0.0	0.0	0.0																													732	93	30	80	0	0	0	0	0	0"
row = line.chomp.split("\t")
puts "row size #{row.size}"
row.each do |element|
  puts "element is: |#{element}|. Match with regex is |#{(rex =~element).class}|." 
end
