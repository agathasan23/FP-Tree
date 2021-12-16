#!/usr/bin/env python
# coding: utf-8

# In[6]:


import numpy as np
from collections import OrderedDict
import csv


"""Defining the structure of the FP-Tree Node and a method to print it in a
nested list format."""
class fpTreeNode:
    def __init__(self, name, freq, parent):
        self.name = name #name of the item
        self.freq = freq #  frequency of the item in the dataset
        self.parent = parent #  parent node
        self.child = OrderedDict() #  children node information
        self.link = None # linking to nodes with same name
       
    def display_tree_list(self):
        print(self.name, self.freq,end='')
        if len(self.child)>0:
            print(",[",end='')
        for c in self.child.values():
            print("[",end='')
            c.display_tree_list()
            if len(c.child)==0:
                print("]",end='')
        print("]",end='')


"""Writes the frequent itemsets to a CSV file"""
def export_to_file(data):
    with open(output_file_name, "w",  newline='') as f:
        writer = csv.writer(f, delimiter=',')
        for row in data:
            writer.writerows([[row]])


"""The most recent node is linked to the previous node with same name."""
def similar_item_table_update(similar_item, present_node):
    # Traversing 
    while (similar_item.link != None):
        similar_item = similar_item.link
    similar_item.link = present_node


"""This function takes the input dataset and scans it once to create the
frequent item dictionary. Once that is created, it deletes any value in the
dictionary which is below the threshold."""
def fp_tree_preprocess(doc_name, threshold):
    data = np.genfromtxt(doc_name, delimiter=file_delimiter, dtype=str)
    item_freq = {}
    # 1st database scan
    for (x,y), value in np.ndenumerate(data):
        if value != '':
            if value not in item_freq:
                item_freq[value] = 1
            else:
                item_freq[value] += 1
    item_freq = {k:v for k,v in item_freq.items() if v >= threshold}
    return data, item_freq


"""This function scans the database for the second time.
After deleting items with low threshold value, it orders the items in a given 
transaction.
The ordered transaction is then sent to the FP-Tree creating function."""
def fp_tree_reorder(data, item_freq):
    root = fpTreeNode('Root',1,None)
    sorted_item_freq = sorted(item_freq.items(), key=lambda x: (-x[1],x[0]))
    sorted_keys = []
    similar_item_dict = {}
    for key in sorted_item_freq:
        similar_item_dict[key[0]] = None 
        sorted_keys.append(key[0]) 
    for row in data:
        trans = []
        for col in row:
            if col in item_freq:
                trans.append(col)
        ordered_trans = []
        for item in sorted_keys:
            if item in trans:
                ordered_trans.append(item)
        if len(ordered_trans)!= 0:
            fp_tree_create_and_update(root, ordered_trans, similar_item_dict)
    return root, similar_item_dict


"""This function recursively creates the FP-Tree for each transaction."""
def fp_tree_create_and_update(init_node, trans, similar_item_dict):
    if trans[0] in init_node.child:
        init_node.child[trans[0]].freq += 1
    else:
        init_node.child[trans[0]] = fpTreeNode(trans[0], 1, init_node)
        if similar_item_dict[trans[0]] == None:
            similar_item_dict[trans[0]] = init_node.child[trans[0]]
        else:
            similar_item_table_update(similar_item_dict[trans[0]],                                      init_node.child[trans[0]])
    if len(trans) > 1:
        fp_tree_create_and_update(init_node.child[trans[0]], trans[1::],                                  similar_item_dict)


"""Function to create the conditional FP-Tree for every frequent occuring item
in the main FP-Tree.
The function works exactly similar to the fp_tree_create_and_update() function,
except here the similar-item table is not updated"""
def conditional_fptree(name,init_node,data):
    if data[0][0] == name:
        if len(data)>1:
            conditional_fptree(name,init_node,data[1::])
    if data[0][0] != name:
        if data[0][0] in init_node.child:
            init_node.child[data[0][0]].freq += data[0][1]
        else:
            init_node.child[data[0][0]] = fpTreeNode(data[0][0],data[0][1],                           init_node)
        if len(data) >1:
            conditional_fptree(name,init_node.child[data[0][0]],data[1::])

"""Function to create the conditional FP-Tree for every time present in the
Similar-Item Table.
Each freqently occuring itemset above the threshold is also considered frequent
"""
def create_leaf_cond_base(similar_item_dict, threshold):
    final_cond_base = []
    for key,value in similar_item_dict.items():
        final_cond_base_key = []
        condition_base = []
        leaf_item_freq = OrderedDict()
        while value != None:
            path = []
            leaf_node = value
            leaf_freq = value.freq
            while leaf_node.parent != None:
                leaf_details = [leaf_node.name, leaf_freq]
                path.append(leaf_details) 
                leaf_node = leaf_node.parent 
    
            condition_base.insert(0,path)
            value = value.link
        for row in condition_base:
            for col in row:
                if col[0] not in leaf_item_freq:
                    leaf_item_freq[col[0]] = col[1]
                else:
                    leaf_item_freq[col[0]] += col[1]
        leaf_item_freq = {k:v for k,v in leaf_item_freq.items()                           if v >= threshold}
        for row in condition_base:
            temp = []
            temp_tree = []
            for col in row:
                if col[0] in leaf_item_freq:
                    temp.append(col[0]) 
                    temp_tree.append(col) 
            final_cond_base.append(temp) 
            final_cond_base_key.append(temp_tree) 
        cond_leaf = key
        cond_root = fpTreeNode('Null Set',1,None)
        for row in final_cond_base_key:
            conditional_fptree(cond_leaf,cond_root,row)
        if len(cond_root.child) > 1:
            print('\n--------',"Conditional FP-Tree for",cond_leaf,'--------')
            print("[",end='')
            cond_root.display_tree_list()
            print('\n')
    unique_cond_base_set = set(map(tuple,final_cond_base))
    unique_cond_base_list =list(unique_cond_base_set)
    unique_cond_base_list.sort(key=lambda                                unique_cond_base_list:unique_cond_base_list[0])
    unique_cond_base = map(list,unique_cond_base_list)
    export_to_file(unique_cond_base) 


"""Main part of the code"""
# Required User Inputs
support = 300
file_name = 'groceries.csv'
file_delimiter = ','
output_file_name = "output.csv"

dataset, freq_items = fp_tree_preprocess(file_name, support)
fptree_root, header_table = fp_tree_reorder(dataset, freq_items)
create_leaf_cond_base(header_table,support)


# In[ ]:





# In[ ]:




