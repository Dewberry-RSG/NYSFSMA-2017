# plotfile.jl
#
# Description: Function to Plot for data from a csv File. See iterator_plot.jl to run the code for multiple csv files
#
# amousam@dewberry.com

#---Load Packages
using PyPlot 

#---Function to Plot a csv File

function plotfile(file)
    df=readdlm(file,',', header=false, skipstart=1)
    data=df[:,6:7]                                    #---Read in columns [(rows),column_1:column_n]
    datasort=sortrows(data, by=x->(x[2],x[1]))        #---Sort
    v=datasort[:,1]				#pick the column of interest
    f=sum(v)					#sum column	
    p=cumsum(v)					#calculate the cumulative sum of each row
    g=p/f						#calculate normalized value of the column
    j=datasort[:,2]				#pick column of interest
    plot(j,g)					#plot
  	plt = PyPlot                #rename Pyploy to a shorter name 
  	plt.ylabel("Normalized Length");   #xlabel
  	plt.xlabel("Elevation (ft)");	#ylabel
  	plt.grid("on")					#turn on grid
  	plt.title("Characteristic Levee Crest Elevation") #title 
  	savefig(replace(file,"csv","png"))				#save plot as png
  	close()                                       #closeplot
end
