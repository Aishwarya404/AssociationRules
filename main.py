# Name : Aishwarya Sivakumar, UNI : as6418
# Name : Sairam Haribabu, UNI : sh4188

import csv
import sys
from collections import defaultdict
from itertools import combinations
import math
import copy


# Method to read the data file and load content into list
# Input : csv file name
# Output : headers and data lists
def read_load_csv(data_file):
    file = open(data_file)
    csvreader = csv.reader(file)
    headers = []
    headers = next(csvreader)
    data = []
    for row in csvreader:
        if not('' in row or 'UNKNOWN' in row):
            data.append(row)
    file.close
    return headers, data


# Method to return all subset combinations from a set
# Input : a set item
# Output : list of all 2^n possible subsets of item
def get_all_combinations(item):
    result = []
    count = len(item)
    for i in range(1, count+1):
        result.extend(combinations(item, i))
    return result


# Method to prune itemsets and remove entries if any subset of length "size" of items in itemsets 
# does not exist in the previous itemsets.
# Input : current iteration itemsets, previous iteration itemsets, size
# Output : dictionary after pruning unncessary itemset
def prune_itemsets(min_supp_itemsets, prev_itemsets, size):
    result = copy.deepcopy(min_supp_itemsets)
    for itemset in min_supp_itemsets.keys():
        subsets = list(combinations(itemset, size))
        for subset in subsets:
            if subset not in prev_itemsets:
                del result[itemset]
    return result


# Method to get candidate itemsets with support above threshold
# Input : list data, itemsets extracted in previous iteration, min support threshold and current size of candidates
# Output : dictionary containing candidates with their support
def get_frequent_itemsets(data, previous, supp_size, size):
    data_size = len(data)
    result = defaultdict()

    # If size of candidate pair is 1, traverse through all rows and update support
    if size == 1:
        for row in data:
            for item in row:
                if (item,) not in result:
                    result[(item,)] = 0
                result[(item,)] += 1
        min_supp_itemsets = {k: (v/data_size)*100 for k, v in result.items() if v > supp_size}
        return min_supp_itemsets

    # If size of candidate is 2, then find all ordered combinations of single candidates, 
    # traverse through all rows and update support
    if size == 2:
        previous = list(previous)
        len_previous = len(previous)
        for i in range(len_previous):
            for j in range(i+1, len_previous):
                tup = previous[i] + previous[j]
                for row in data:
                    if all(x in row for x in tup):
                        if tup not in result:
                            result[tup] = 0
                        result[tup] += 1
        min_supp_itemsets = {k: (v/data_size)*100 for k, v in result.items() if v > supp_size}
        return min_supp_itemsets

    # For all other sizes, apriori requires following conditions to be satisfied:
    # 1. candidate pair of size k can be formed from two (k-1) pairs with same values upto k-2.
    # 2. The k-1 th item should be in ascending order.
    # 3. Current iteration itemsets should be pruned based on subset existence in previous iteration itemsets. 
    else:
        prev_itemsets = copy.deepcopy(previous)
        previous = list(previous)
        len_previous = len(previous)
        for i in range(len_previous):
            for j in range(i+1, len_previous):
                if previous[i][:size-2] != previous[j][:size-2] or previous[i][size-2:size-1] >= previous[j][size-2:size-1]:
                    break
                tup = previous[i][:size-2] + previous[i][size-2:size-1] + previous[j][size-2:size-1]
                for row in data:
                    if all(x in row for x in tup):
                        if tup not in result:
                            result[tup] = 0
                        result[tup] += 1
        min_supp_itemsets = {k: (v/data_size)*100 for k, v in result.items() if v > supp_size}
        min_supp_itemsets = prune_itemsets(min_supp_itemsets, prev_itemsets, size-1)
        return min_supp_itemsets


# Method to return all possible rules with one entry on RHS and one or more on LHS from a candidate itemset
# Input : tuple of an itemset
# Output : list of all possible rules
def get_rule_pairs(itemset):
    result = []
    for item in itemset:
        right = item
        left = get_all_combinations(set(itemset) - {item})
        for l in left:
            result.append((tuple(sorted(l)), right))
    return result


# Method to process all high frequency candidate pairs and return rules with high confidence
# Input : Sorted dictionary of itemsets and min confidence threshold
# Output : dictionary containing candidate rule with confidence and support 
def get_association_rules(sorted_itemsets, min_conf):
    result = {}
    for itemset in sorted_itemsets.keys():
        if len(itemset) != 1:
            rule_pairs = get_rule_pairs(itemset)
            for rule in rule_pairs:
                l_union_r = tuple(sorted(list(rule[0]) + [rule[1]]))
                conf = sorted_itemsets[l_union_r] / sorted_itemsets[rule[0]]
                if conf > min_conf:
                    if rule not in result:
                        result[rule] = [conf*100, sorted_itemsets[itemset]]
                    elif sorted_itemsets[itemset] > result[rule][1]:
                        result[rule] = [conf*100, sorted_itemsets[itemset]]
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return result


# Handler method to aid in execution of apriori algorithm. Calls get_frequent_itemsets with previous itemsets
# Input : list of data and min support value
# Output : dictionary of high support candidate itemsets sorted in decreasing order of support
def apriori_algorithm(data, supp_size):
    frequent_itemsets = defaultdict()
    size = 0
    key_frequent_itemsets = None
    while True:
        size += 1
        val_frequent_itemsets = get_frequent_itemsets(data, key_frequent_itemsets, supp_size, size)
        if len(val_frequent_itemsets) == 0:
            break
        if size == 1:
            frequent_itemsets = val_frequent_itemsets
        else:
            frequent_itemsets.update(val_frequent_itemsets)
        key_frequent_itemsets = dict(sorted(val_frequent_itemsets.items(), key=lambda x: x[0]))
    frequent_itemsets = dict(sorted(frequent_itemsets.items(), key=lambda x: x[1], reverse=True))
    return frequent_itemsets


# Helper method to write itemsets to output file
# Input : dictionary of itemsets and output file name
#  Output : Nothing
def write_itemsets(itemsets, output_f, min_supp):
    output_file = open(output_f, 'a')
    output_file.write("{} Candidate Sets With High Support (min_supp = {}%)\n\n".format(len(itemsets), min_supp*100))
    for item in itemsets:
        output_file.write("{}, {:.4f} % \n ".format(list(item), itemsets[item]))
    output_file.write("\n")
    output_file.close()


# Helper method to write high confidence rules to output file
# Input : dictionary of rules and output file name
#  Output : Nothing
def write_rules(rules, output_f, min_conf):
    output_file = open(output_f, 'a')
    output_file.write("{} Association Rules With High Confidence (min_conf = {}%)\n\n".format(len(rules), min_conf*100))
    for rule in rules:
        output_file.write("{} => {}  (Conf: {:.4f} %,  Supp: {:.4f} %) \n".format(list(rule[0][0]), [rule[0][1]], rule[1][0], rule[1][1]))
    output_file.close()


# Main method which processes command line inputs, loads data from csv, calls method to get frequent itemsets, 
# method to get high conf rules and write to output file
def main():
    data_file = sys.argv[1]
    min_supp = float(sys.argv[2])
    min_conf = float(sys.argv[3])
    output_f = 'output.txt'

    headers, data = read_load_csv(data_file)
    supp_size = math.floor(min_supp * len(data))
    
    frequent_itemsets = apriori_algorithm(data, supp_size)
    write_itemsets(frequent_itemsets, output_f, min_supp)
    rules = get_association_rules(frequent_itemsets, min_conf)
    write_rules(rules, output_f, min_conf)


if __name__ == '__main__':
    main()