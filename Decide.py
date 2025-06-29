# -*- coding: utf-8 -*-
"""
Copyright 2025 Tim Langhorst

First version created on Tue Sep  5 2023

@authors: tlanghorst, mtuchschmid

Please read the ReadMe.txt

Short guide for usage:
1. Fill out the Input.xlsx table
2. Use requirements.txt to load the right packages
3. Click on "Run"/[Shift]+[F10] to run this code
4. Carefully assess the estimated results and replace them with more appropriate data as soon as it becomes available
"""

import pickle
import os
import pandas as pd
from openpyxl import load_workbook
from pylab import *
import pyodbc
import re
import numpy as np
import sys


def find_ChemID(CASN):
    """
    Returns the ChemID
    Input: CAS number
    Output: ChemID
    """
    ChemID=None
    
    conn = pyodbc.connect(database)
    cursor = conn.cursor()
    cursor.execute('select * from Chem_Info')
    for row in cursor.fetchall():
        rows=list(row)
        if rows[3]==CASN:
            ChemID=rows[0]
    return ChemID

def find_AcceptedValue(Values):
    """
    Returns the accepted value of properties (values are classified as R=rejected, A=Accepted, N=Not Used, U=Unevaluated, see Manual (p.14))
    Input: List of different Values of one propery (from the DIPPR database)
    Output: Accepted Value
    """
    AccepValue=None
    
    i=0
    while i<len(Values):
        SourceID=Values[i][1]
        test=list()
        conn = pyodbc.connect(database)
        cursor = conn.cursor()
        cursor.execute('select * from Sources')   
        for row in cursor.fetchall():
            rows=list(row)
            if rows[0]==SourceID and rows[6]=="A":
                AccepValue=Values[i][0]
            if rows[0]==SourceID:    
                test.append([Values[i][0],SourceID,rows[6]])
        i+=1  
    return AccepValue

def find_Formula(CASN):
    """
    Returns the Formula
    Input: CAS number
    Output: Formula
    """
    Formula=None
    
    conn = pyodbc.connect(database)
    cursor = conn.cursor()
    cursor.execute('select * from Chem_Info')
    for row in cursor.fetchall():
        rows=list(row)
        if rows[3]==CASN:
            Formula=rows[2]
    return Formula

def find_NBP(CASN):
    """
    Returns the accepted temperature-independent parameters and all temperature-independent parameters found in the database
    Input: CAS number
    Output:[accepted critical temperature, accepted critical pressure, accepted acentric factor, accepted standard state heat of formation, accepted standard state absolute entropy,
            critical temperature, critical pressure, acentric factor, standard state heat of formation, standard state absolute entropy] 
                            (K, Pa,-,J/mol, J/molK, K, Pa,-,J/mol, J/molK)
    """
    ChemID=find_ChemID(CASN)
    conn = pyodbc.connect(database)
    cursor = conn.cursor()
    cursor.execute('select * from Const_Values')
    
    NBPs=list() #Normal boiling point in K
    
    for row in cursor.fetchall():
        rows=list(row)
        if rows[1]==ChemID and rows[2]=="NBP":
            NBPs.append([rows[5],rows[6]])

    NBP=find_AcceptedValue(NBPs)

    return NBP

def find_MW(CASN):
    """
    Returns the accepted temperature-independent parameters and all temperature-independent parameters found in the database
    Input: CAS number
    Output:[accepted critical temperature, accepted critical pressure, accepted acentric factor, accepted standard state heat of formation, accepted standard state absolute entropy,
            critical temperature, critical pressure, acentric factor, standard state heat of formation, standard state absolute entropy] 
                            (K, Pa,-,J/mol, J/molK, K, Pa,-,J/mol, J/molK)
    """
    ChemID=find_ChemID(CASN)
    conn = pyodbc.connect(database)
    cursor = conn.cursor()
    cursor.execute('select * from Const_Values')
    
    MWs=list() #Normal boiling point in K
    
    for row in cursor.fetchall():
        rows=list(row)
        if rows[1]==ChemID and rows[2]=="MW":
            MWs.append([rows[5],rows[6]])

    MW=find_AcceptedValue(MWs)

    return MW

def extract_value_from_dict(cell, key):
    if cell is None:
        return None
    
    return cell.get(key)

def split_formula(formula):
    pattern = r'([A-Z][a-z]*)(\d*)'
    
    if formula is None:
        return None

    matches = re.findall(pattern, formula)

    elements_counts = {}

    for match in matches:
        element, count = match
        if count == '':
            count = 1
        else:
            count = int(count)
        elements_counts[element] = count

    return elements_counts

def search_CASN_in_rows(df1, df2, lookup):

    storage_list = []
    
    for index, row in df1.iterrows():
        if lookup in row.values:
            position = row[row == lookup].index[0]
            
            storage_list.append(pd.Series(df2.loc[index, position]))
        
        else: storage_list.append(pd.Series(0))
    
    storage = pd.concat(storage_list, ignore_index=True)
    
    return storage

def create_input_DT(products_CAS, products_stoich, reactants_CAS, reactants_stoich, c_arom, AddSidePro):
    
    countPro = products_CAS.count(axis=1)
    countReac = reactants_CAS.count(axis=1)
    x_MP = products_stoich.iloc[:,0] / products_stoich.sum(axis=1)
    MW_mainP = products_CAS.iloc[:,0].apply(find_MW)
    
    BP_prod = products_CAS.applymap(find_NBP)
    BP_reac = reactants_CAS.applymap(find_NBP)
    BPmaxP = BP_prod.max(axis=1)
    BPminP = BP_prod.min(axis=1)
    BPmaxE = BP_reac.max(axis=1)
    BPminE = BP_reac.min(axis=1)
    
    df_formulas = reactants_CAS.applymap(find_Formula)
    df_split = df_formulas.applymap(split_formula)
    C = ((df_split.applymap(lambda cell: extract_value_from_dict(cell, 'C')) * reactants_stoich).sum(axis=1) - (c_arom * reactants_stoich).sum(axis=1)) / products_stoich.iloc[:,0]
    c = (c_arom * reactants_stoich).sum(axis=1) / products_stoich.iloc[:,0]
    F = (df_split.applymap(lambda cell: extract_value_from_dict(cell, 'F')) * reactants_stoich).sum(axis=1) / products_stoich.iloc[:,0]
    N = (df_split.applymap(lambda cell: extract_value_from_dict(cell, 'N')) * reactants_stoich).sum(axis=1) / products_stoich.iloc[:,0]
    Cl = (df_split.applymap(lambda cell: extract_value_from_dict(cell, 'Cl')) * reactants_stoich).sum(axis=1) / products_stoich.iloc[:,0]
    
    stoichioH2 = (search_CASN_in_rows(reactants_CAS, reactants_stoich, '1333-74-0') - search_CASN_in_rows(products_CAS, products_stoich, '1333-74-0')) / products_stoich.iloc[:,0]
    water =  (search_CASN_in_rows(products_CAS, products_stoich, '7732-18-5') - search_CASN_in_rows(reactants_CAS, reactants_stoich, '7732-18-5')) / products_stoich.iloc[:,0]
    
    result = pd.concat([F, N, countPro, BPmaxE, BPmaxP, BPminE, BPminP, MW_mainP, Cl, C, c, countReac, AddSidePro, stoichioH2, water, x_MP], axis=1)
    return result

# find directory of .py file
directory = os.getcwd()

# import decision trees in list decision_trees

directory_pickles = os.path.join(directory, "pickles D7")
pickles = sorted(os.listdir(directory_pickles))

decision_trees = []

for file in pickles:
    path = os.path.join(directory_pickles, file)
    with open (path, 'rb') as p:
        dp = pickle.load(p)
        
        decision_trees.append(dp)

# import input data from excel
directory_inputexcel = os.path.join(directory, "Input.xlsx")

# check if Input_manual sheet contains empty cells

input_manual = pd.read_excel(directory_inputexcel, sheet_name = 'Input_manual', header = None, usecols = 'D:S', skiprows = [0,1,2])
if input_manual.isna().any().any():
    
    input_autom = pd.read_excel(directory_inputexcel, sheet_name = 'Input_autom', header = None, usecols = 'B:V', skiprows = [0,1])
    
    identifiers = input_autom.iloc[:,[0,1]].copy()
    products_CAS = input_autom.iloc[:,[2,3,4]].copy()
    products_stoich = input_autom.iloc[:,[5,6,7]].copy()
    reactants_CAS = input_autom.iloc[:,[8,9,10,11]].copy()
    reactants_stoich = input_autom.iloc[:,[12,13,14,15]].copy()
    c_arom = input_autom.iloc[:,[16,17,18,19]].copy()
    AddSidePro = input_autom.iloc[:,[20]].copy()
    
    products_CAS.columns = range(products_CAS.shape[1])
    products_stoich.columns = range(products_stoich.shape[1])
    reactants_CAS.columns = range(reactants_CAS.shape[1])
    reactants_stoich.columns = range(reactants_stoich.shape[1])
    c_arom.columns = range(c_arom.shape[1])
    
    directory_database = os.path.join(directory, "DIPPR\\DIPPR801_Full_May2021.accdb")
    database=r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=" + directory_database
    
    data = create_input_DT(products_CAS, products_stoich, reactants_CAS, reactants_stoich, c_arom, AddSidePro)

    with pd.ExcelWriter(directory_inputexcel, mode='a', if_sheet_exists='overlay') as writer:
        identifiers.to_excel(writer, sheet_name="Input_manual", startrow=3, startcol=1, header=False, index=False)
        data.to_excel(writer, sheet_name="Input_manual", startrow=3, startcol=3, header=False, index=False)

else:
    data = input_manual

da = data.values

# run decision trees 

storage = []

for item in decision_trees:
    storage.append(item.predict(da).tolist())


# get leaf_indices of test data and the corresponding MAE

leaf_indices = []
mae = []
mae_results = []

for item in decision_trees:
    leaf_indices.append(item.apply(da))
    mae.append(item.tree_.impurity)

# assign mae's to the test data leafs

for i in range(7):
    leafs = leaf_indices[i]
    maes = mae[i]
    mae_list = []
    
    for item in leafs:
        mae_list.append(maes[item])
    
    mae_results.append(mae_list) 

# combine results and mae's

combined = []

for i in range (7):
    combined.append(storage[i])
    combined.append(mae_results[i])
    

combined_df = pd.DataFrame(combined).T

#print results to output file

identifiers = pd.read_excel(directory_inputexcel, sheet_name = 'Input_manual', header = None, usecols = 'B:C', skiprows = [0,1,2])

directory_outputexcel = os.path.join(directory, "Output.xlsx")
# book = load_workbook(directory_outputexcel)
# writer_output = pd.ExcelWriter(directory_outputexcel, engine='openpyxl')
# writer_output.book = book
with pd.ExcelWriter(directory_outputexcel, mode='a', if_sheet_exists='overlay') as writer:
    identifiers.to_excel(writer, sheet_name="Output", startrow=2, startcol=0, header=False, index=False)
    combined_df.to_excel(writer, sheet_name="Output", startrow=2, startcol=2, header=False, index=False)

#writer_output.save()





















