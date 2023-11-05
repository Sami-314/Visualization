#!/usr/bin/env python3


###### import packages
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import matplotlib.ticker as ticker
import sys
import pandas as pd
import argparse
import matplotlib.style as mplstyle
import itertools
from functions import df_filter, is_number, Ransac, boxplot


###### main

###### show manual
if len(sys.argv) == 1:
	print("\nusage : python Prog.py -i [input.csv] -x [Xaxis_Column_Name1] [Xaxis_Column_Name2] -y [Yaxis_Column_Name] -legend [Legend_Column_Name]")
	print("Ex.) python graph.py -i input.csv -x Voltage(V) DC_Leakage_A -y Current(A) -legend Die")
	print("help : -h\n")
	exit()



###### argument setting
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='I show Plot. \n<Key Event> \n 1 : Show All\n 2 : Hide All\n 3 : Show Next\n 4 : Show last\n 5 : Toggle All\n Down_Arrow : Choose Next\n Up_Arrow : Choose Last\n Spacebar : Toggle\n 6 : Choice cancel\n')

parser.add_argument('-i', metavar='input.csv', dest='input', help='Input File')
parser.add_argument('-x', metavar='Xaxis_Column_Name', type=str, nargs='+', dest='xaxis', help='Xaxis_Column_Names in Input File (multiple arguments possible -> Create multiple plots.')
parser.add_argument('-y', metavar='Yaxis_Column_Name', type=str, nargs='+', dest='yaxis', help='Yaxis_Column_Names in Input File (multiple arguments possible -> Create multiple plots.')
parser.add_argument('-legend', metavar='Legend_Column_Names', type=str, nargs='+', dest='legend_multiple', help='Legend_Column_Names in Input File (multiple arguments possible -> Concatenate strings and create new column.')
parser.add_argument('-line', metavar='Line_Split_Condition', type=str, nargs='+', dest='line_multiple', help='[OPTIONAL, Default : Legend] Line_Split_Condition(Column_Names) in Input File (multiple arguments possible -> Concatenate strings and create new column.')
parser.add_argument('-filter', metavar='filter.txt', dest='filter', help='Filter File')
parser.add_argument('-fit', metavar='model(linear, log, expo, poly)', dest='model', help='Fiting Model')
parser.add_argument('-fit_percentile', metavar='Fitting_Percentile_List', type=str, nargs='+', dest='percentile_list', help='Percentile List for Fitting.')
parser.add_argument('-fit_percentile_outlier_count', metavar='Outlier_Count_to_Remove when_Percentile_Fitting', type=int, dest='percentile_outlier_count', help=' Outlier Count to Remove for  Percentile Fitting.')
parser.add_argument('-option', metavar='Plot Options', type=str, nargs='+', dest='plot_option', help='xlog(or _\'N\') / ylog(or _\'N\') / xinvert / yinvert / xshare / yshare / font_big / font_small / scatter / boxplot(or _Xaxis_Column_Name) / no_marker / legend_sort_ascending / legend_sort_descending / plots_vertical_arrange')

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

_legend_sort_ascending = False    # legend column sort
_legend_sort_descending = False

_plot_vertical = False        # plots arrangement (Default : horizontal)

_boxplot = False
_boxplot_additional_xaxis = ""

_line_width = 2     # line_plot = True / scatter_plot = False
_axes_label_title_font_size = 25
_marker_size = 10
_legend_fontsize = 15

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

        elif _option == "legend_sort_ascending":
            _legend_sort_ascending = True

        elif _option == "legend_sort_descending":
            _legend_sort_descending = True

        elif _option == "plots_vertical_arrange":
            _plot_vertical = True

        elif _option == "scatter":
            _line_width = 0     # line_plot = False / scatter_plot = True

        elif _option.find("boxplot") >= 0:
            if _dimension_0:
                if _option == "boxplot":
                    _boxplot = True
                else:
                    _xaxis_column_name = _option.split("boxplot_")
                    if len(_xaxis_column_name) > 1:
                        _boxplot = True
                        _boxplot_additional_xaxis = _xaxis_column_name[1]
                    else:
                        print(str(_option) + " input is invalid!")
                        exit()
            else:
                print("Boxplot is only available in a single plot!")
                exit()

        elif _option == "no_marker":
            _marker_size = 0

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
                _log_index = _option.split("_")     # xlog_0, xlog_1...
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
                _log_index = _option.split("_")     # ylog_0, ylog_1...
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
df['_legend_merged'] = 'ALL'
df['line_split_condition_merged'] = 'ALL'


###### set input Legends into string
if _legend_input:
    for _each_column in args.legend_multiple:
        df[_each_column] = df[_each_column].apply(str)

###### merge input Legends and pick-up legend list
    df['_legend_merged'] = df[args.legend_multiple].agg('_'.join,axis=1)

###### Line split condition on plot = Legend(Default)
    df['line_split_condition_merged'] = df['_legend_merged']



###### Same as legend setting above(legend -> line_split_condition)
if _line_input:
    for _each_column in args.line_multiple:
        df[_each_column] = df[_each_column].apply(str)
    df['line_split_condition_merged'] = df[args.line_multiple].agg('_'.join,axis=1)

    
###### plot setting
parameters = {'axes.labelsize' : _axes_label_title_font_size, 'axes.titlesize' : _axes_label_title_font_size, 'font.size' : _axes_label_title_font_size}
plt.rcParams.update(parameters)


###### base plot setting
if _plot_vertical:
    fig, ax = plt.subplots(_dimension_length,1, sharex = _x_share, sharey = _y_share, figsize=(10,6))
else:
    fig, ax = plt.subplots(1,_dimension_length, sharex = _x_share, sharey = _y_share, figsize=(10,6))


# axis scale inversion : high to low
# conflict when axis share is false 
if _x_invert:
    if _x_share:
        plt.gca().invert_xaxis()

if _y_invert:
    if _y_share:
        plt.gca().invert_yaxis()


###### plot setting
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


###### plot marker list
_legend_marker_list = itertools.cycle(('o', 'X', '^', 'P', 's', '*', 'D')) 
_line_marker_list = itertools.cycle(('o', 'X', '^', 'P', 's', '*', 'D')) 
_legend_color_list = itertools.cycle(('r','b','tab:orange','tab:green','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','black')) 
_line_color_list = itertools.cycle(('r','b','tab:orange','tab:green','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','black')) 

###### plots > lines > line
plots = []
for _index in range(_dimension_length):
        lines = []
        plots.append(lines)


###### plot every legend
_legend_list = list(df['_legend_merged'].drop_duplicates())

if _legend_sort_ascending == True:      # Legend Sort
    _legend_list.sort()
elif _legend_sort_descending == True:
    _legend_list.sort(reverse=True)


# Ransac Fitting
if _ransac_fit_linear:
    df = Ransac(df, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _legend_list)
elif _ransac_fit_log:
    df = Ransac(df, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _legend_list, _scale = "log")
elif _ransac_fit_expo:
    df = Ransac(df, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _legend_list, _scale = "expo")
elif _ransac_fit_ndegree:
    df = Ransac(df, args.xaxis[0], args.yaxis[0], _percentile_list, _percentile_outlier_count, _legend_list, _scale = "poly")


if _boxplot:
    boxplot(df, args.xaxis[0], args.yaxis[0], _boxplot_additional_xaxis, _x_scale_log)
    
    plt.tight_layout()
    plt.show()
    
    exit()


for _legend in _legend_list:
    _filtered_legend = df.loc[df['_legend_merged']==_legend,:]

    _line_split_condition_list = list(_filtered_legend['line_split_condition_merged'].drop_duplicates())
    
    for _line_split in _line_split_condition_list:
        _filtered_line = _filtered_legend.loc[_filtered_legend['line_split_condition_merged']==_line_split,:]

        for _index in range(_dimension_length):

            if _dimension_0:
                line, = ax.plot(_filtered_line[args.xaxis[_index]], _filtered_line[args.yaxis[_index]], lw=_line_width, label=_legend, marker='o', markersize=_marker_size, color = 'black')

                plots[0].append(line)

            elif _dimension_1:
                line, = ax[_index].plot(_filtered_line[args.xaxis[_index]], _filtered_line[args.yaxis[_index]], lw=_line_width, label=_legend, marker='o', markersize=_marker_size, color = 'black')

                plots[_index].append(line)



###### ploted(list) > lined(hash) > line / will map legend lines to original lines.
ploted = []
for _index in range(_dimension_length):
    lined = {}
    ploted.append(lined)


# ###### remove legend duplicates
leg = _ax.legend()

handles, labels = _ax.get_legend_handles_labels()

newLabels, newHandles = [], []
for handle, label in zip(handles, labels):
    if label not in newLabels:
        newLabels.append(label)
        newHandles.append(handle)

for handle in newHandles:
    handle.set_marker(next(_legend_marker_list))
    handle.set_color(next(_legend_color_list))

leg_duplicates_removed = _ax.legend(newHandles, newLabels, markerscale=1,loc='upper left',bbox_to_anchor=(1,1),fontsize=_legend_fontsize,shadow=True,fancybox=True)


###### set legend text pickable
from collections import defaultdict

origline = []
for _index in range(_dimension_length):
    ploted[_index] = defaultdict(list)      # Enable list access thruogh hash
    origline.append('')         # Initialize empty index

    # match line and legend
    for legline, origline[_index] in zip(leg.get_texts(), plots[_index]):
        for legline_duplicates_removed in leg_duplicates_removed.get_texts():
            legline_duplicates_removed.set_picker(True)
            if str(legline) == str(legline_duplicates_removed):
                ploted[_index][legline_duplicates_removed].append(origline[_index])
                break
    

###### plot color and marker setting
for _index in range(_dimension_length):

    # move to the first of the cycle
    for _line_marker in _line_marker_list:
        if _line_marker == 'D':
            break

    for _line_color in _line_color_list:
        if _line_color == 'black':
            break


    # color and marker setting
    for _legline in ploted[_index]:
        _line_marker = next(_line_marker_list)
        _line_color = next(_line_color_list)
        
        for _origline_index in ploted[_index][_legline]:
            _origline_index.set_marker(_line_marker)
            _origline_index.set_color(_line_color)


##### pick legend
def on_pick(event):

    for legline in ploted[0]:           # ploted[1] the same.
        legline.set_color('black')
    # On the pick event, find the original line corresponding to the legend
    # proxy line, and toggle its visibility.
    legline = event.artist
    for _index in range(_dimension_length):
        origline = ploted[_index][legline]
        for _origline_index in origline:
            visible = not _origline_index.get_visible()
            _origline_index.set_visible(visible)
    # Change the alpha on the line in the legend so we can see what lines
    # have been toggled.
    legline.set_alpha(1.0 if visible else 0.2)
    legline.set_color('red')

    fig.canvas.draw_idle()      # .draw() on Windows.


fig.canvas.mpl_connect("pick_event", on_pick)



###### show all legend
def show_all(event):

    if event.key == "1":
        for legline in ploted[0]:
            for _index in range(_dimension_length):
                origline = ploted[_index][legline]
                for _origline_index in origline:
                    _origline_index.set_visible(1)

            legline.set_alpha(1.0)

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', show_all)



###### hide all legend
def hide_all(event):

    if event.key == "2":
        for legline in ploted[0]:
            for _index in range(_dimension_length):
                origline = ploted[_index][legline]
                for _origline_index in origline:
                    _origline_index.set_visible(0)

            legline.set_alpha(0.2)

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', hide_all)



###### show next legend
def show_next(event):

    if event.key == "3":
        former_legline = list(ploted[0])[-1]
        show_done = 0

        for legline in ploted[0]:
            if former_legline.get_color() == 'red':
                for _legline in ploted[0]:
                    for _index in range(_dimension_length):
                        origline = ploted[_index][_legline]
                        for _origline_index in origline:
                            _origline_index.set_visible(0)

                    _legline.set_alpha(0.2)
                    _legline.set_color('black')

                for _index in range(_dimension_length):
                    origline = ploted[_index][legline]
                    for _origline_index in origline:
                        _origline_index.set_visible(1)

                legline.set_alpha(1.0)
                legline.set_color('red')
                show_done = 1
                break

            former_legline = legline

        if show_done == 0:
            first_legline = list(ploted[0])[0]
            for _index in range(_dimension_length):
                origline = ploted[_index][first_legline]
                for _origline_index in origline:
                    _origline_index.set_visible(1)

            first_legline.set_alpha(1.0)
            first_legline.set_color('red')

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', show_next)



###### show last legend
def show_last(event):
	
    if event.key == "4":
        former_legline = list(ploted[0])[-1]
        show_done = 0

        for legline in ploted[0]:

            if legline.get_color() == 'red':

                for _legline in ploted[0]:
                    for _index in range(_dimension_length):
                        origline = ploted[_index][_legline]
                        for _origline_index in origline:
                            _origline_index.set_visible(0)

                    _legline.set_alpha(0.2)
                    _legline.set_color('black')

                for _index in range(_dimension_length):
                    origline = ploted[_index][former_legline]
                    for _origline_index in origline:
                        _origline_index.set_visible(1)

                former_legline.set_alpha(1.0)
                former_legline.set_color('red')
                show_done = 1
                break

            former_legline = legline

        if show_done == 0:
            last_legline = list(ploted[0])[-1]
            for _index in range(_dimension_length):
                origline = ploted[_index][last_legline]
                for _origline_index in origline:
                    _origline_index.set_visible(1)

            last_legline.set_alpha(1.0)
            last_legline.set_color('red')

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', show_last)



###### toggle all legends
def toggle_all(event):

    if event.key == "5":
        for legline in ploted[0]:
            for _index in range(_dimension_length):
                origline = ploted[_index][legline]
                for _origline_index in origline:
                    visible = not _origline_index.get_visible()
                    _origline_index.set_visible(visible)

            legline.set_alpha(1.0 if visible else 0.2)

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', toggle_all)



###### choose legend
def move_down(event):

    if event.key == "down":
        former_legline = list(ploted[0])[-1]
        show_done = 0

        for legline in ploted[0]:
            if former_legline.get_color() == 'red':

                former_legline.set_color('black')
            
                legline.set_color('red')
                show_done = 1
                break

            former_legline = legline

        if show_done == 0:
            first_legline = list(ploted[0])[0]
            first_legline.set_color('red')

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', move_down)



###### choose legend
def move_up(event):
	
    if event.key == 'up':
        former_legline = list(ploted[0])[-1]
        show_done = 0

        for legline in ploted[0]:

            if legline.get_color() == 'red':

                legline.set_color('black')

                former_legline.set_color('red')
                show_done = 1
                break

            former_legline = legline

        if show_done == 0:
            last_legline = list(ploted[0])[-1]
            last_legline.set_color('red')

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', move_up)



###### toggle selected legend
def selected_toggle(event):

    if event.key == ' ':

        for legline in ploted[0]:

            if legline.get_color() == 'red':

                for _index in range(_dimension_length):
                    origline = ploted[_index][legline]
                    for _origline_index in origline:
                        visible = not _origline_index.get_visible()
                        _origline_index.set_visible(visible)

                legline.set_alpha(1.0 if visible else 0.2)
                
                break

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', selected_toggle)



###### remove selection
def remove_selected(event):
	
    if event.key == '6':

        for legline in ploted[0]:

            if legline.get_color() == 'red':

                legline.set_color('black')
                
                break

    fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', remove_selected)


###### tight layout
def tight_layout(event):
	
	if event.key == '0':

		fig.tight_layout()

	fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', tight_layout)


#pixels to scroll per mousewheel event
d = {"down" : 63, "up" : -63}


def func(evt):

    if leg_duplicates_removed.contains(evt):
        bbox = leg_duplicates_removed.get_bbox_to_anchor()
        bbox = Bbox.from_bounds(bbox.x0, bbox.y0+d[evt.button], bbox.width, bbox.height)
        tr = leg_duplicates_removed.axes.transAxes.inverted()
        leg_duplicates_removed.set_bbox_to_anchor(bbox.transformed(tr))
        fig.canvas.draw_idle()

fig.canvas.mpl_connect("scroll_event", func)

###### tighten plot layout
fig.tight_layout()

###### fasten performance
mplstyle.use(['fast'])

###### show plot
plt.show()