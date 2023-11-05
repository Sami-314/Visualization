#!/usr/bin/env python3


import pandas as pd
import argparse
from functions import df_filter


###### main


###### argument setting
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='')

parser.add_argument('-i', metavar='input.csv', dest='input', help='Input Data')
parser.add_argument('-filter', metavar='filter.txt', dest='filter', help='Data Filtering Condition')
parser.add_argument('-o', metavar='output.csv', dest='output', help='Output Data(Filtered)')

args = parser.parse_args()

if args.input == None:
	print("missing Input!")
	exit()

if args.filter == None:
	print("missing Filtering Condition!")
	exit()

if args.output == None:
	print("missing Output!")
	exit()


df = pd.read_csv(args.input)

df=df_filter(df,args.filter)

df.to_csv(args.output, index=False)
