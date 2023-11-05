#!/usr/bin/env python3



from audioop import reverse
import fnmatch
#ransac regresssion on a dataset with outliers
import numpy as np
from matplotlib import pyplot as plt
# from sklearn.linear_model import RANSACRegressor
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn import linear_model
import scipy.stats as st
import itertools

def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def df_filter(df, filter_file):

    df['_is_target'] = True
    df['or'] = False
    line_readable = True
    values = []

    f_read = open(filter_file,'r')

    for line in f_read:

        if line.find("/*") >= 0:
            line_readable = False
        elif line.find("*/") >= 0:
            line_readable = True

        word = line.split(":")
        
        if line_readable and word[0].strip() == ".select":
            _chosen_column_name = word[1].strip()

        elif line_readable and word[0].strip() == ".target":
            _condition = word[1].strip()

            if _condition == "get_values()":
                df.loc[~(df[_chosen_column_name].isin(values)),'_is_target'] = False

            elif _condition.find('==') >= 0:
            # X == a,b,c...
            
                _targets = _condition.split('==')
                _targets = _targets[1].strip()
                _targets = _targets.split(",")

                for _index, _target in enumerate(_targets):
                    _targets[_index] = _target.strip()

                df[_chosen_column_name] = df[_chosen_column_name].astype(str)
                _chosen_column_list = list(df[_chosen_column_name].drop_duplicates())

                _targets_in_chosen_column=[]
                for _target in _targets:
                    _targets_in_chosen_column += fnmatch.filter(_chosen_column_list, _target)

                df.loc[~(df[_chosen_column_name].isin(_targets_in_chosen_column)),'_is_target'] = False


            elif _condition.find('>=') >= 0:
            # X >= N / N >= X / N >= X >= -N / N >= X > -N / N > X >= -N

                _targets = _condition.split('>=')

                if _targets[0].strip() == 'X':
                # X >= N
                
                    _operand = _targets[1].strip()

                    if is_number(_operand):

                        for index, row in df.iterrows():

                            if is_number(row[_chosen_column_name]):

                                if row[_chosen_column_name] < float(_operand):
                                    df.at[index, '_is_target'] = False 

                            else:
                                print(str(row[_chosen_column_name]) + " is not a number!")
                                exit()

                    else:
                        print(".target invalid!")
                        exit()
                
                elif _targets[1].strip() == 'X':
                # N >= X / N >= X >= -N

                    if len(_targets) == 3:
                    # N >= X >= -N

                        _operand_1 = _targets[0].strip()
                        _operand_2 = _targets[2].strip()

                        if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) < row[_chosen_column_name] or row[_chosen_column_name] < float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()

                    else:
                    # N >= X

                        _operand = _targets[0].strip()

                        if is_number(_operand):
                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand) < row[_chosen_column_name]:
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()
                
                elif _targets[1].find('>') >= 0:
                # N >= X > -N
                
                    _operand_1 = _targets[0].strip()
                    _targets = _targets[1].split('>')
                    _operand_2 = _targets[1].strip()

                    if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) < row[_chosen_column_name] or row[_chosen_column_name] <= float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                    else:
                        print(".target invalid!")
                        exit()

                elif _targets[0].find('>') >= 0:
                # N > X >= -N

                    _operand_2 = _targets[1].strip()
                    _targets = _targets[0].split('>')
                    _operand_1 = _targets[0].strip()

                    if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) <= row[_chosen_column_name] or row[_chosen_column_name] < float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                    else:
                        print(".target invalid!")
                        exit()

                else:
                    print(".target invalid!")
                    exit()


            elif _condition.find('<=') >= 0:
            # X <= N / N <= X / -N <= X <= N / -N <= X < N / -N < X <= N

                _targets = _condition.split('<=')

                if _targets[0].strip() == 'X':
                # X <= N

                    _operand = _targets[1].strip()

                    if is_number(_operand):

                        for index, row in df.iterrows():

                            if is_number(row[_chosen_column_name]):

                                if row[_chosen_column_name] > float(_operand):
                                    df.at[index, '_is_target'] = False

                            else:
                                print(str(row[_chosen_column_name]) + " is not a number!")
                                exit()

                    else:
                        print(".target invalid!")
                        exit()
                
                elif _targets[1].strip() == 'X':
                # N <= X / -N <= X <= N

                    if len(_targets) == 3:
                    # -N <= X <= N

                        _operand_1 = _targets[0].strip()
                        _operand_2 = _targets[2].strip()

                        if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) > row[_chosen_column_name] or row[_chosen_column_name] > float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()

                    else:
                    # N <= X
                        _operand = _targets[0].strip()

                        if is_number(_operand):
                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand) > row[_chosen_column_name]:
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()
                
                elif _targets[1].find('<') >= 0:
                # -N <= X < N

                    _operand_1 = _targets[0].strip()
                    _targets = _targets[1].split('<')
                    _operand_2 = _targets[1].strip()

                    if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) > row[_chosen_column_name] or row[_chosen_column_name] >= float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                    else:
                        print(".target invalid!")
                        exit()

                elif _targets[0].find('<') >= 0:
                # -N < X <= N

                    _operand_2 = _targets[1].strip()
                    _targets = _targets[0].split('<')
                    _operand_1 = _targets[0].strip()

                    if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) >= row[_chosen_column_name] or row[_chosen_column_name] > float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                    else:
                        print(".target invalid!")
                        exit()

                else:
                    print(".target invalid!")
                    exit()


            elif _condition.find('>') >= 0:
            # X > N / N > X / -N > X > N

                _targets = _condition.split('>')

                if _targets[0].strip() == 'X':
                # X > N

                    _operand = _targets[1].strip()

                    if is_number(_operand):

                        for index, row in df.iterrows():

                            if is_number(row[_chosen_column_name]):

                                if row[_chosen_column_name] <= float(_operand):
                                    df.at[index, '_is_target'] = False

                            else:
                                print(str(row[_chosen_column_name]) + " is not a number!")
                                exit()

                    else:
                        print(".target invalid!")
                        exit()
                
                elif _targets[1].strip() == 'X':
                # N > X / -N > X > N

                    if len(_targets) == 3:
                    # -N > X > N

                        _operand_1 = _targets[0].strip()
                        _operand_2 = _targets[2].strip()

                        if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) <= row[_chosen_column_name] or row[_chosen_column_name] <= float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()

                    else:
                    # N > X

                        _operand = _targets[0].strip()

                        if is_number(_operand):
                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand) <= row[_chosen_column_name]:
                                        df.at[index, '_is_target'] = False
                                
                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()
                
                
            elif _condition.find('<') > 0:
            # X < N / N < X / -N < X < N

                _targets = _condition.split('<')

                if _targets[0].strip() == 'X':
                # X < N

                    _operand = _targets[1].strip()

                    if is_number(_operand):

                        for index, row in df.iterrows():

                            if is_number(row[_chosen_column_name]):

                                if row[_chosen_column_name] >= float(_operand):
                                    df.at[index, '_is_target'] = False

                            else:
                                print(str(row[_chosen_column_name]) + " is not a number!")
                                exit()

                    else:
                        print(".target invalid!")
                        exit()
                
                elif _targets[1].strip() == 'X':
                # N < X / -N < X < N

                    if len(_targets) == 3:
                    # -N < X < N

                        _operand_1 = _targets[0].strip()
                        _operand_2 = _targets[2].strip()

                        if is_number(_operand_1) and is_number(_operand_2):

                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand_1) >= row[_chosen_column_name] or row[_chosen_column_name] >= float(_operand_2):
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()

                    else:
                    # N < X

                        _operand = _targets[0].strip()

                        if is_number(_operand):
                            for index, row in df.iterrows():

                                if is_number(row[_chosen_column_name]):

                                    if float(_operand) >= row[_chosen_column_name]:
                                        df.at[index, '_is_target'] = False

                                else:
                                    print(str(row[_chosen_column_name]) + " is not a number!")
                                    exit()

                        else:
                            print(".target invalid!")
                            exit()

            else:
            
                print(".target invalid!")
                exit()


        elif line_readable and word[0].strip() == ".do":

            _do = word[1].strip()

            if _do == "get":

                df.drop(df.loc[(df['_is_target'] == False) & (df['or'] == False),:].index, inplace = True)
                df['_is_target'] = True
                df['or'] = False



            elif _do == "cut":

                df.drop(df.loc[(df['_is_target'] == True) | (df['or'] == True),:].index, inplace = True)
                df['_is_target'] = True
                df['or'] = False



            elif _do.find('abs*[') >= 0:

                _abs_target = _do.split("abs*[")
                _abs_target = _abs_target[1].split("]*")

                df.loc[((df['_is_target'] == True) | (df['or'] == True)) & (df[_abs_target[0]] < 0),_abs_target[0]] *= -1
                df['_is_target'] = True
                df['or'] = False


            elif _do.find('set_values*[') >= 0:

                _set_value_target = _do.split("set_values*[")
                _set_value_target = _set_value_target[1].split("]*")

                _filtered_df = df.loc[((df['_is_target'] == True) | (df['or'] == True)),:]
                values = list(_filtered_df[_set_value_target[0]].drop_duplicates())
                df['_is_target'] = True
                df['or'] = False


            elif _do == "or":
                
                df.loc[df['_is_target'] == True,'or'] = True
                df['_is_target'] = True
            

            elif _do != "and":
                print(str(_do) + " in .do is invalid!")
                exit()

                

    del df['_is_target']
    del df['or']
    return df



# evaluate a model
def evaluate_model(X, y, model):
	#define model evaluation method
	cv = RepeatedKFold(n_splits = 5, n_repeats = 10, random_state = 1)
	#evaluate model
	scores = cross_val_score(model, X, y, scoring = 'neg_mean_absolute_error', cv = cv, n_jobs = -1)

	print('Mean MAE : %.3f, Std MAE : %.3f' % (np.mean(np.absolute(scores)), np.std(np.absolute(scores))))



def Ransac(df, Xaxis_Column_Name, Yaxis_Column_Name, _percentile_list, _percentile_outlier_count, _legend_list, _scale = "linear"):

    if len(_legend_list) == 1:
        _line_color_list = itertools.cycle(('black', 'black'))
    else:
        _line_color_list = itertools.cycle(('r','b','tab:orange','tab:green','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan','black')) 

    for _legend in _legend_list:
        _filtered_legend = df.loc[df['_legend_merged']==_legend,:]
        
        X=_filtered_legend[[Xaxis_Column_Name]].to_numpy()
        y=_filtered_legend[[Yaxis_Column_Name]].to_numpy()

        #Check Inlier vs Outlier (maybe)
        ransac = linear_model.RANSACRegressor(max_trials=10000)

        if _scale == "log":
            X = np.log10(X)

        elif _scale == "expo":
            y = np.log10(y)

        elif _scale == "poly":
            X = np.log10(X)
            y = np.log10(y)

        #fit the model on all data
        ransac.fit(X, y)

        #evaluate model
        # evaluate_model(X,y,model)

        #plot the line of best fit
        xaxis = np.arange(X.min(),X.max(), (X.max() - X.min())/100)
        yaxis = ransac.predict(xaxis.reshape((len(xaxis),1)))

        # inlier_mask = ransac.inlier_mask_
        # outlier_mask = np.logical_not(inlier_mask)

        predicted_y = ransac.predict(X.reshape((len(X),1)))
        _error_list = y - predicted_y

        _filtered_legend.reset_index(inplace = True)
        for _count in range(_percentile_outlier_count):
            if abs(_error_list.max()) > abs(_error_list.min()):
                _filtered_legend.drop(_filtered_legend.loc[[np.argmax(_error_list)],:].index, inplace = True)
                _error_list[np.argmax(_error_list)] = 0
                
            else:
                _filtered_legend.drop(_filtered_legend.loc[[np.argmin(_error_list)],:].index, inplace = True)
                _error_list[np.argmin(_error_list)] = 0


        _sigma = np.std(_error_list)

        _percentile_list.sort(reverse = True)

        for _index, _percentile in enumerate(_percentile_list):
            _z_value = st.norm.ppf(float(_percentile) / 100)

            percentile_yaxis = yaxis + _z_value * _sigma 

            if _scale == "log":
                plt.plot(10**xaxis, percentile_yaxis, color = next(_line_color_list), linestyle = '--', lw = 2.5)
            elif _scale == "expo":
                plt.plot(xaxis, 10**percentile_yaxis, color = next(_line_color_list), linestyle = '--', lw = 2.5)    
            elif _scale == "poly":
                plt.plot(10**xaxis, 10**percentile_yaxis, color = next(_line_color_list), linestyle = '--', lw = 2.5)
            else:
                plt.plot(xaxis, percentile_yaxis, color = next(_line_color_list), linestyle = '--', lw = 2.5)
            

            # if _scale == "log":
            #     plt.figtext(0.1, 0.1 - _index / 40, str(_percentile) + chr(37) + ' : Y = %.4f * (Log X) + (%.4f)' % (float(ransac.estimator_.coef_), float(ransac.estimator_.intercept_) + _z_value * _sigma), ha="left", fontsize=10)
            # elif _scale == "expo":
            #     plt.figtext(0.1, 0.1 - _index / 40, str(_percentile) + chr(37) + ' : (Log Y) = %.4f * (X) + (%.4f)' % (float(ransac.estimator_.coef_), float(ransac.estimator_.intercept_) + _z_value * _sigma), ha="left", fontsize=10)
            # elif _scale == "poly":
            #     plt.figtext(0.1, 0.1 - _index / 40, str(_percentile) + chr(37) + ' : (Log Y) = %.4f * (Log X) + (%.4f)' % (float(ransac.estimator_.coef_), float(ransac.estimator_.intercept_) + _z_value * _sigma), ha="left", fontsize=10)
            # else:
            #     plt.figtext(0.1, 0.1 - _index / 40, str(_percentile) + chr(37) + ' : Y = %.4f * (X) + (%.4f)' % (float(ransac.estimator_.coef_), float(ransac.estimator_.intercept_) + _z_value * _sigma), ha="left", fontsize=10)


        # Return dataframe with percentile fitting outliers removed
    
    df.reset_index(inplace = True)
    return df   


def boxplot(df, Xaxis_Column_Name, Yaxis_Column_Name, _boxplot_additional_xaxis, _x_scale_log):

    boxprops=dict(linestyle='-', linewidth=1.5, color ='black')
    flierprops=dict(marker='o', markersize=5, markeredgecolor ='black')
    medianprops=dict(linestyle='-', linewidth=2.5, color ='black', solid_capstyle = 'butt')
    whiskerprops=dict(linestyle='-', linewidth=1.5, color ='black')
    capprops=dict(linestyle='-', linewidth=1.5, color ='black')


    _Xaxis_list = list(df[Xaxis_Column_Name].drop_duplicates())

    _is_xaxis_number_only = True
    for _Xaxis in _Xaxis_list:
        if not is_number(_Xaxis):
            _is_xaxis_number_only = False
            break
    
    if _is_xaxis_number_only:

        for _Xaxis in _Xaxis_list:
            filtered_df = df.loc[df[Xaxis_Column_Name] == _Xaxis,:]

            if _x_scale_log:
                _width = _Xaxis / 4
            else:
                _width = 1

            plt.boxplot(filtered_df[Yaxis_Column_Name], positions = [_Xaxis]
                        , widths = _width
                        , boxprops = boxprops
                        , flierprops = flierprops
                        , medianprops = medianprops
                        , whiskerprops = whiskerprops
                        , capprops = capprops)

        plt.xticks([])

        if len(_boxplot_additional_xaxis) > 0:

            plt.plot(df[_boxplot_additional_xaxis], df[Yaxis_Column_Name], linewidth = 0, marker ='o', color = 'r', markersize = 5)

        if _x_scale_log:        
            plt.xscale('log')
        else:
            plt.xscale('linear')

    else:
        _Xaxis_list.sort()
        _box_location_list = []

        for _box_location, _Xaxis in enumerate(_Xaxis_list):
            filtered_df = df.loc[df[Xaxis_Column_Name] == _Xaxis,:]

            plt.boxplot(filtered_df[Yaxis_Column_Name], positions = [_box_location]
                        , boxprops = boxprops
                        , flierprops = flierprops
                        , medianprops = medianprops
                        , whiskerprops = whiskerprops
                        , capprops = capprops)

            _box_location_list.append(_box_location)
            
            if len(_boxplot_additional_xaxis) > 0:

                plt.plot([_box_location] * len(filtered_df[Yaxis_Column_Name]), filtered_df[Yaxis_Column_Name], linewidth = 0, marker ='o', color = 'r', markersize = 5)

        plt.xticks(_box_location_list, _Xaxis_list)