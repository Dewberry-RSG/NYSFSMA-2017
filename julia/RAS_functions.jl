# plotfile.jl

#============================================#
# Description: Functions for 
#
# amousam@dewberry.com
#============================================#


#-----------------------------------------------------#
# exportcsvfile ==> Read in File, do something
#-----------------------------------------------------#

function exportcsvfile(file)
    df=readdlm(file,',', header=false, skipstart=1) #Read csv file as an array
    data=df[:,6:7]                                  #Read in columns [(rows),column_1:column_n]
    datasort=sortrows(data, by=x->(x[2],x[1]))      #Sort 
    v=datasort[:,1]									#pick the column of interest
    f=sum(v)										#sum column	
    p=cumsum(v)										#calculate the cumulative sum of each row
    g=p/f                                           #calculate normalized value of the column
    j=datasort[:,2]								    #pick column of interest
    K=DataFrame(NormalizedLength=g, Elevation=j)	#Create Dataframe with the two columns of interest 
	return K										#return the K value	
  	close()											#close iteration
end


#-----------------------------------------------------#
# calclen ==> Read in File, do something
#-----------------------------------------------------#
using DataFrames   #load data frames 

function calclen(file)   
	df=readtable(file)				#Read csv file as a Data frame 
	data=df[:,6:7]					#columns of interest
	return data						#return data
	close()
end 