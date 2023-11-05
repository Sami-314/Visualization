#!/usr/bin/env python3


#Library Import
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import argparse
import itertools
from functions import df_filter, is_number, Ransac

###### main

###### show manual
if len(sys.argv) == 1:
	print("\nusage : python Prog.py -i [input.csv] -x [Xaxis_Column_Name1] [Xaxis_Column_Name2] -y [Yaxis_Column_Name] -legend [Legend_Column_Name]")
	print("Ex.) python graph.py -i input.csv -x Voltage(V) DC_Leakage_A -y Current(A) -legend Die")
	print("help : -h\n")
	exit()



###### argument setting
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='I show Plots in PDF.\n')

parser.add_argument('-i', metavar='input.csv', dest='input', help='Input File')
parser.add_argument('-x', metavar='Xaxis_Column_Name', type=str, nargs='+', dest='xaxis', help='Xaxis_Column_Names in Input File (multiple arguments possible -> Create multiple plots.')
parser.add_argument('-y', metavar='Yaxis_Column_Name', type=str, nargs='+', dest='yaxis', help='Yaxis_Column_Names in Input File (multiple arguments possible -> Create multiple plots.')
parser.add_argument('-page', metavar='Page_Column_Names', type=str, nargs='+', dest='page_multiple', help='Page_Column_Names in Input File (multiple arguments possible -> Concatenate strings and create new column.')
parser.add_argument('-legend', metavar='Legend_Column_Names', type=str, nargs='+', dest='legend_multiple', help='Legend_Column_Names in Input File (multiple arguments possible -> Concatenate strings and create new column.')
parser.add_argument('-line', metavar='Line_Split_Condition', type=str, nargs='+', dest='line_multiple', help='[OPTIONAL, Default : Legend] Line_Split_Condition(Column_Names) in Input File (multiple arguments possible -> Concatenate strings and create new column.')
parser.add_argument('-filter', metavar='filter.txt', dest='filter', help='Filter File')
parser.add_argument('-fit', metavar='model(linear, log, expo, poly)', dest='model', help='Fiting Model')
parser.add_argument('-fit_percentile', metavar='Fitting_Percentile_List', type=str, nargs='+', dest='percentile_list', help='Percentile List for Fitting.')
parser.add_argument('-fit_percentile_outlier_count', metavar='Outlier_Count_to_Remove when_Percentile_Fitting', type=int, dest='percentile_outlier_count', help=' Outlier Count to Remove for  Percentile Fitting.')
parser.add_argument('-option', metavar='Plot Options', type=str, nargs='+', dest='plot_option', help='xlog(or _\'N\') / ylog(or _\'N\') / xinvert / yinvert / xshare / yshare / font_big / font_small / scatter / no_marker / title / raster / page_sort_ascending / page_sort_ascending / legend_sort_ascending / legend_sort_descending / plots_vertical_arrange')

args = parser.parse_args()

if args.input == None:
	print("missing Input!")
	exit()

if args.xaxis == None:
	print("missing Xaxis!")
	exit()

if args.yaxis == None:
	print("missing Yaxis!")
	exit()

###### parameter setting
_page_input = True
if args.page_multiple == None:
	_page_input = False

_legend_input = True
if args.legend_multiple == None:
	_legend_input = False

_line_input = True
if args.line_multiple == None:
	_line_input = False

_filter_input = True
if args.filter == None:
	_filter_input = False


###### Check the plots dimension
_dimension_0 = False
_dimension_1 = False

_x_length = len(args.xaxis)
_y_length = len(args.yaxis)
if _x_length != _y_length:
    print("X-axis and Y-axis input unmatched!")
    exit()

if _x_length == 1:              #x_length == _y_length
    _dimension_0 = True
else:
    _dimension_1 = True

_dimension_length = _x_length   #_dimension_length == _x_length == _y_length

_x_input_all_the_same = False       #Check if all input the same for label drop
_y_input_all_the_same = False
if len(list(set(args.xaxis))) == 1:
    _x_input_all_the_same = True
if len(list(set(args.yaxis))) == 1:
    _y_input_all_the_same = True


_ransac_fit_linear = False      # Ransac Fitting OFF
_ransac_fit_log = False
_ransac_fit_expo = False
_ransac_fit_ndegree = False
if args.model != None:
    if _dimension_0:
        if args.model == "linear":
            _ransac_fit_linear = True
        elif args.model == "log":
            _ransac_fit_log = True
        elif args.model == "expo":
            _ransac_fit_expo = True
        elif args.model == "poly":
            _ransac_fit_ndegree = True
        else:
            print(str(args.model) + " input is invalid!")
            exit()
    else:
        print("Fitting is only available in a single plot!")
        exit()

if args.percentile_list == None:
    _percentile_list = [50]     # Default Fitting Line
else:
    for _percentile in args.percentile_list:
        if is_number(_percentile):
            if float(_percentile) >= 100 or float(_percentile) <= 0:
                print("-fit_percentile input is invalid!")
                exit()
        else:
            print("-fit_percentile input is invalid!")
            exit()
    
    _percentile_list = args.percentile_list

if args.percentile_outlier_count == None:
    _percentile_outlier_count = 0
else:
    if is_number(args.percentile_outlier_count):
        if int(args.percentile_outlier_count) < 0:
            print("-fit_percentile_outlier_count input is invalid!")
            exit()
        else:
            _percentile_outlier_count = int(args.percentile_outlier_count)
    else:
        print("-fit_percentile_outlier_count input is invalid!")
        exit()


###### Check -option
_x_scale_log = False      # X axis scale = Decimal
_x_scale_log_index =[]
_y_scale_log = False      # Y axis scale = Decimal
_y_scale_log_index =[]

_x_share = False        # X axis share
_y_share = False       # Y axis share

_x_invert = False		# axis scale inversion : high to low
_y_invert = False		

_page_sort_ascending = False    # page column sort
_page_sort_descending = False

_legend_sort_ascending = False    # legend column sort
_legend_sort_descending = False

_plot_vertical = False        # plots arrangement (Default : horizontal)

_line_width = 2     # line_plot = True / scatter_plot = False
_axes_label_title_font_size = 25
_marker_size = 10
_legend_fontsize = 15

_title = False		# Plot Title

_raster = False		# Plot into image

if args.plot_option != None:
	for _option in args.plot_option:

		if _option == "xshare":
			_x_share = True

		elif _option == "yshare":
			_y_share = True   

		elif _option == "xinvert":
			_x_invert = True     

		elif _option == "yinvert":
			_y_invert = True

		elif _option == "page_sort_ascending":
			_page_sort_ascending = True

		elif _option == "page_sort_descending":
			_page_sort_descending = True

		elif _option == "legend_sort_ascending":
			_legend_sort_ascending = True

		elif _option == "legend_sort_descending":
			_legend_sort_descending = True

		elif _option == "plots_vertical_arrange":
			_plot_vertical = True   

		elif _option == "scatter":
			_line_width = 0     # line_plot = False / scatter_plot = True

		elif _option == "no_marker":
			_marker_size = 0

		elif _option == "title":
			_title = True  

		elif _option == "raster":
			_raster = True  

		elif _option == "font_big":
			_axes_label_title_font_size = 30
			if _marker_size > 0:
				_marker_size = 15
			if _line_width > 0:
				_line_width = 2.5
			_legend_fontsize = 20

		elif _option == "font_small":
			_axes_label_title_font_size = 20
			if _marker_size > 0:
				_marker_size = 5
			if _line_width > 0:
				_line_width = 1.5
			_legend_fontsize = 10

		elif _option.find("xlog") >= 0:
			_x_scale_log = True       # X axis scale = Log
			
			if _option == "xlog":
				for _index in range(_dimension_length):
					_x_scale_log_index.append(_index)


			else:
				_log_index = _option.split("_")		# xlog_0, xlog_1...
				if len(_log_index) > 1:
					if is_number(_log_index[1]):
						if int(_log_index[1]) >= _dimension_length:
							print(str(_option) + " input is invalid!(Out of Range)")
							exit()
						else:
							_x_scale_log_index.append(int(_log_index[1]))
					else:
						print(str(_option) + " input is invalid!(Not a number)")
						exit()
				else:
					print(str(_option) + " input is invalid!")
					exit()


		elif _option.find("ylog") >= 0:
			_y_scale_log = True       # Y axis scale = Log

			if _option == "ylog":
				for _index in range(_dimension_length):
					_y_scale_log_index.append(_index)

			else:
				_log_index = _option.split("_")		# ylog_0, ylog_1...
				if len(_log_index) > 1:
					if is_number(_log_index[1]):
						if int(_log_index[1]) >= _dimension_length:
							print(str(_option) + " input is invalid!(Out of Range)")
							exit()
						else:
							_y_scale_log_index.append(int(_log_index[1]))
					else:
						print(str(_option) + " input is invalid!(Not a number)")
						exit()
				else:
					print(str(_option) + " input is invalid!")
					exit()


###### read input
df = pd.read_csv(args.input)


###### dataframe filtering
if _filter_input:
    df = df_filter(df,args.filter)


###### default -page, -legend, -line
df['_page_merged'] = 'ALL'
df['_legend_merged'] = 'ALL'
df['line_split_condition_merged'] = 'ALL'


###### set input pages into string
if _page_input:
	for _each_column in args.page_multiple:
		df[_each_column] = df[_each_column].apply(str)

###### merge input pages and pick-up page list
	df['_page_merged'] = df[args.page_multiple].agg('_'.join,axis=1)
	df['_legend_merged'] = df['_page_merged']
	df['line_split_condition_merged'] = df['_page_merged']


###### set input Legends into string
if _legend_input:
	for _each_column in args.legend_multiple:
		df[_each_column] = df[_each_column].apply(str)

	df['_legend_merged'] = df[args.legend_multiple].agg('_'.join,axis=1)
	df['line_split_condition_merged'] = df['_legend_merged']

###### Same as legend setting above(legend -> line_split_condition)
if _line_input:
	for _each_column in args.line_multiple:
		df[_each_column] = df[_each_column].apply(str)
	df['line_split_condition_merged'] = df[args.line_multiple].agg('_'.join,axis=1)


###### plot setting
parameters = {'axes.labelsize' : _axes_label_title_font_size, 'axes.titlesize' : _axes_label_title_font_size, 'font.size' : _axes_label_title_font_size}
plt.rcParams.update(parameters)


###### plot marker list
_line_marker_list = itertools.cycle(('o', 'X', '^', 'P', 's', '*', 'D')) 
_line_color_list = itertools.cycle(('tab:red','tab:blue','tab:green','tab:orange','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','black')) 


# Create PDF
from datetime import datetime
now = datetime.now()

current_time = "_(" + str(now.year) + "_" + str(now.month) + "_" + str(now.day) + ")_(" + str(now.hour) + "_" + str(now.minute) + "_" + str(now.second) + ").pdf"

from matplotlib.backends.backend_pdf import PdfPages
mypdf = PdfPages("Plot_in_PDF" + current_time)



###### plot every legend
_page_list = list(df['_page_merged'].drop_duplicates())

if _page_sort_ascending == True:		# Page Sort
    _page_list.sort()
elif _page_sort_descending == True:
    _page_list.sort(reverse=True)

for _page in _page_list:
	_filtered_page = df.loc[df['_page_merged']==_page,:]


	###### base plot setting
	if _plot_vertical:
		fig, ax = plt.subplots(_dimension_length,1, sharex = _x_share, sharey = _y_share, figsize=(10,6))
	else:
		fig, ax = plt.subplots(1,_dimension_length, sharex = _x_share, sharey = _y_share, figsize=(10,6))


	# Ransac Fitting
	if _ransac_fit_linear:
		_filtered_page = Ransac(_filtered_page, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count)
	elif _ransac_fit_log:
		_filtered_page = Ransac(_filtered_page, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _scale = "log")
	elif _ransac_fit_expo:
		_filtered_page = Ransac(_filtered_page, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _scale = "expo")
	elif _ransac_fit_ndegree:
		_filtered_page = Ransac(_filtered_page, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _scale = "poly")


	# axis scale inversion : high to low
	# conflict when axis share is false 
	if _x_invert:
		if _x_share:		
			plt.gca().invert_xaxis()

	if _y_invert:
		if _y_share:
			plt.gca().invert_yaxis()

	###### plot setting
	
	if _title:
		plt.suptitle(_page, fontsize = _axes_label_title_font_size + 5)

	if _dimension_0:
		ax.set_xlabel(args.xaxis[0])
		ax.set_ylabel(args.yaxis[0])
		_ax = ax

		if _x_scale_log:
			ax.set_xscale('log')
		else:
			ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
		
		if _y_scale_log:
			ax.set_yscale('log')
		else:
			ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(5))

		# axis scale inversion : high to low
		# conflict when axis share is true 
		if _x_invert:
			if not _x_share:
				ax.invert_xaxis()

		if _y_invert:
			if not _y_share:
				ax.invert_yaxis()

		ax.tick_params(which='major',width=1.0,length=5)
		ax.grid(visible=True,which='major',color='gray',linestyle='--',linewidth=1.0)
		ax.grid(visible=True,which='minor',color='gray',linestyle=':',linewidth=1.0)
		ax.set_rasterized(_raster)

	elif _dimension_1:
		for _index in range(_dimension_length):

			if _plot_vertical:
				if _x_input_all_the_same:
					ax[_dimension_length-1].set_xlabel(args.xaxis[_dimension_length-1])
					ax[_index].set_ylabel(args.yaxis[_index])
				else:
					ax[_index].set_xlabel(args.xaxis[_index])
					ax[_index].set_ylabel(args.yaxis[_index])
				_ax = ax[0]
			else:
				if _y_input_all_the_same:
					ax[_index].set_xlabel(args.xaxis[_index])
					ax[0].set_ylabel(args.yaxis[0])
				else:
					ax[_index].set_xlabel(args.xaxis[_index])
					ax[_index].set_ylabel(args.yaxis[_index])
				_ax = ax[_dimension_length-1]
			
			if _x_scale_log:
				
				if _index in _x_scale_log_index:
					ax[_index].set_xscale('log')
				else:
					ax[_index].xaxis.set_minor_locator(ticker.AutoMinorLocator(5))

			else:
				ax[_index].xaxis.set_minor_locator(ticker.AutoMinorLocator(5))
			
			if _y_scale_log:

				if _index in _y_scale_log_index:
					ax[_index].set_yscale('log')
				else:
					ax[_index].yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
				
			else:
				ax[_index].yaxis.set_minor_locator(ticker.AutoMinorLocator(5))

			# axis scale inversion : high to low
			# conflict when axis share is true 
			if _x_invert:
				if not _x_share:
					ax[_index].invert_xaxis()

			if _y_invert:
				if not _y_share:
					ax[_index].invert_yaxis()

			ax[_index].tick_params(which='major',width=1.0,length=5)
			ax[_index].grid(visible=True,which='major',color='gray',linestyle='--',linewidth=1.0)
			ax[_index].grid(visible=True,which='minor',color='gray',linestyle=':',linewidth=1.0)
			ax[_index].set_rasterized(_raster)



	# move to the first of the cycle
	for _marker in _line_marker_list:
		if _marker == 'D':
			break

	for _color in _line_color_list:
		if _color == 'black':
			break

	_legend_list = list(_filtered_page['_legend_merged'].drop_duplicates())

	if _legend_sort_ascending == True:		# Legend Sort
		_legend_list.sort()
	elif _legend_sort_descending == True:
		_legend_list.sort(reverse=True)

	for _legend in _legend_list:

		_marker = next(_line_marker_list)
		_color = next(_line_color_list)

		_filtered_legend = _filtered_page.loc[_filtered_page['_legend_merged']==_legend,:]

		_line_split_condition_list = list(_filtered_legend['line_split_condition_merged'].drop_duplicates())

		for _line_split in _line_split_condition_list:
			_filtered_line = _filtered_legend.loc[_filtered_legend['line_split_condition_merged']==_line_split,:]

			for _index in range(_dimension_length):

				if _dimension_0:
					line, = ax.plot(_filtered_line[args.xaxis[_index]], _filtered_line[args.yaxis[_index]], lw=_line_width, label=_legend, marker=_marker, markersize=_marker_size, color = _color)

				elif _dimension_1:
					line, = ax[_index].plot(_filtered_line[args.xaxis[_index]], _filtered_line[args.yaxis[_index]], lw=_line_width, label=_legend, marker=_marker, markersize=_marker_size, color = _color)



	# ###### remove legend duplicates
	leg = _ax.legend()

	handles, labels = _ax.get_legend_handles_labels()

	newLabels, newHandles = [], []
	for handle, label in zip(handles, labels):
		if label not in newLabels:
			newLabels.append(label)
			newHandles.append(handle)

	_ax.legend(newHandles, newLabels, markerscale=1,loc='upper left',bbox_to_anchor=(1,1),fontsize=_legend_fontsize,shadow=True,fancybox=True)


	fig.tight_layout()
	mypdf.savefig(fig)


mypdf.close()

