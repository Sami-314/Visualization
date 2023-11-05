> plot.py -i [input.csv] -x [Xaxis_Column_Name] -y [Yaxis_Column_Name]
* This shows plots.
* options
	- legend : legend split condition (args : Legend_Split_Column_Name)
	- line : line split condition (args : Line_Split_Column_Name)
	- filter : filter dataframe based on filter.txt condition (args : filter.txt)
	- option : 
		1) xlog(or xlog_'N') : plots(or plot[N-1]) Xaxis into log scale
		2) ylog(or ylog_'N') : plots(or plot[N-1]) Yaxis into log scale
		3) xinvert / yinvert : invert axis scale
		4) xshare / yshare : share axis when multiple plots
		5) font_big / font_small : set font size
		6) scatter : shows scatter plots (Default : line with markers)
		7) no_marker : shows line only
		8) legend_sort_ascending / legend_sort_descending : legend sorting
		9) plots_vertical_arrange : (Default : horizontal arrange)

> plot_pdf.py -i [input.csv] -x [Xaxis_Column_Name] -y [Yaxis_Column_Name]
* This shows plots in PDF.
* options
	- page : page split condition (args : Page_Split_Column_Name)
	- The rest options are all the same as plot.py

> filter.py -i [input.csv] -filter [filter.txt] -o [output.txt]
* Filter input.csv based on filter.txt condition and save as output.txt

> functions.py
* imported in plot.py, plot_pdf.py and filter.py

> filter.txt
* include data frame filtering condition