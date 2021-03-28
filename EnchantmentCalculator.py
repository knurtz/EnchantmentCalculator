#!/bin/env python3

import math
import sys
from anytree import Node, NodeMixin, RenderTree, DoubleStyle
import itertools
from random import randint


class Enchantment:
	identifier = -1			# Default = -1, Sweeping Edge = 37
	name = "Default"
	level = 0
	item_multiplier = 0
	book_multiplier = 0
	
	
class Item(Node):
	def __init__(self, name, parent = None, children = None, item_type = "book", cost = 0, enchantments = []):
		self.item_type = item_type			# can be book or item. todo: differentiate between all different types of items to check enchantment compatibility
		self.cost = cost
		self.enchantments = enchantments
		self.name = name
		self.parent = parent
		if children:
			self.children = children
	
	def updateCost(self):
		# leaves can't update their cost, it is fixed
		if self.is_leaf: return
		
		# recursively update costs of all child nodes and add to own cost
		self.cost = 0
		for n in self.children:
			n.updateCost()
			self.cost = self.cost + n.cost


def total_items(level):
	res = 1
	while(level > 0):
		res = res + pow(2, level)
		level = level - 1
	return res

	
total_inputs = 1
try:
	if (len(sys.argv) > 1): total_inputs = int(sys.argv[1])
except:
	pass

full_rows = int(math.log(total_inputs, 2))
additional_leave_pairs = int(total_inputs - pow(2,full_rows))
possible_positions = int(pow(2, full_rows))
tree_layouts = math.comb(possible_positions, additional_leave_pairs)
combinations_per_tree = math.factorial(total_inputs)
total_combinations = tree_layouts * combinations_per_tree

#print("Total items: %i \nFull rows: %i \nAdditional leave pairs: %i \nPossible Positions for additional pairs: %i \nDifferent tree layouts: %i \nCombinations per tree: %i \nTotal combinations: %i" % (total_inputs, full_rows, additional_leave_pairs, possible_positions, tree_layouts, combinations_per_tree, total_combinations))

all_items = []
base_tree = Item("", cost = 0)
# add two children to every leave until number of leaves matches possible_positions
while len(base_tree.leaves) < possible_positions:
	for n in base_tree.leaves:
		Item("Target", parent = n, cost = 0)
		Item("Sacrifice", parent = n, cost = 0)

base_tree.name = "Final item"

# remember base tree in order to return here later after each iteration
base_tree_leaves = base_tree.leaves

# only operate on base tree if no aditional pairs need to be added
if (additional_leave_pairs == 0): print(RenderTree(base_tree).by_attr())

else:
	# build a list of all leaves indices
	indices = []
	for i in range(0, len(base_tree_leaves)): indices.append(i)
	
	# go through all possible positions for additional leave pairs
	for p in itertools.combinations(indices, additional_leave_pairs):
		
		# add an additional leave pair at each position
		for index in p:
			Item("Target", parent=base_tree_leaves[index], cost = 0)
			Item("Sacrifice", parent=base_tree_leaves[index], cost = 0)
			
		# tree is now ready
		
		# temp: add random prices to each leave
		for l in base_tree.leaves:
			l.cost = randint(1,9)
			
		# recalculate all costs of parents
		base_tree.updateCost()
			
		print(RenderTree(base_tree, style = DoubleStyle).by_attr(lambda n: n.name + ", Cost: " + str(n.cost)))
		print("===================")
		print()
		
		# return to base tree for next iteration
		for n in base_tree_leaves:
			n.children = ()
















