#iterator_length.jl
#
# Description: Function to extract data from a csv File and use a dictionary to calculate sum (see RAS_Dict.jl). 
#              See iterator_length.jl to run the code for multiple csv files
#
# amousam@dewberry.com

#---Load Files Needed

using("RAS_Dict.jl")
using("RAS_functions.jl")

#---Declare Variables

prefix = "length_"


#====================================================
#---Run Iterators   
	
#-----------------------------------------------------#
#---Calculate Length	
#-----------------------------------------------------#

for i in filter!(r"\.csv$", readdir()) #list the files in the folder with a csv extension			  
	f = calclen(i);g = dict[i]	       # run function for each csv file 		           
	newname = prefix*i	               #create new name based on each csv file
	println(newname) 			       #print newname
	X = f[f[:ELEVATION].<g,:]          #select the rows with elevation less than the threshold as defined in the dictionary
    K = sum(X[:LENGTH]) 		       #sum the length for rows with elevation less than the threshold
	println(K)					       #print results 

end


#-----------------------------------------------------#
#---Export to CSV
#-----------------------------------------------------#

for i in filter!(r"\.csv$", readdir()) #list the files in the folder with a csv extension
	f = exportcsvfile(i)			# run function for each csv file 
	newname = "new_"*i				#create new name based on each csv file 
	println(newname)				#print newname
	println(mean_and_std(f[:Elevation])) #print the mean and std deviation for elevation column 
    writetable(newname, f)         #alternatively the information from the function can be written as a new csv file 
end


#-----------------------------------------------------#
#---Plot Results
#-----------------------------------------------------#

for i in filter!(r"\.csv$", readdir()) #list the files in the folder with a csv extension
	plotfile(i)							# run function for each csv file 
end

#-----------------------------------------------------#
#---Calculate max  
#-----------------------------------------------------#

for i in filter!(r"\.csv$", readdir()) #list the files in the folder with a csv extension
	f = calclen(i)			# run function for each csv file 
	newname = "new_"*i				#create new name based on each csv file 
	println(newname)				#print newname
	println(maximum(f[:Elevation])) #print the maximum for elevation column 

end


