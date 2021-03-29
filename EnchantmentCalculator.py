#!/bin/env python3

import math
import sys
from anytree import Node, RenderTree, DoubleStyle
import itertools
from random import randint


name_lut = ["None", "Protection", "Fire Protection", "Feather Falling", "Blast Protection", "Projectile Protection", "Thorns", "Respiration", "Depth Strider", "Aqua Affinity", "Sharpness", "Smite", "Bane of Arthropods", "Knockback", "Fire Aspect", "Looting", "Efficiency", "Silk Touch", "Unbreaking", "Fortune", "Power", "Punch", "Flame", "Infinity", "Luck of the Sea", "Lure", "Frost Walker", "Mending", "Curse of Binding", "Curse of Vanishing", "Impaling", "Riptide", "Loyalty", "Channeling", "Multishot", "Piercing", "Quick Charge", "Soul Speed", "Sweeping Edge"]
item_multiplier_lut = [0, 1, 2, 2, 4, 2, 8, 4, 4, 4, 1, 2, 2, 2, 4, 4, 1, 8, 2, 4, 1, 4, 4, 8, 4, 4, 4, 4, 8, 8, 4, 4, 1, 8, 4, 1, 2, 8, 4]
book_multiplier_lut = [0, 1, 1, 1, 2, 1, 4, 2, 2, 2, 1, 1, 1, 1, 2, 2, 1, 4, 1, 2, 1, 2, 2, 4, 2, 2, 2, 2, 4, 4, 2, 2, 1, 4, 2, 1, 1, 4, 2]
prior_work_penalty = [0, 1, 3, 7, 15, 31, 100]


class Enchantment:
	def __init__(self, identifier, level, keep = False):
		if identifier < -1 or identifier > 37: self.identifier = -1
		else: self.identifier = identifier
		self.level = level
		self.keep = keep
		self.name = name_lut[self.identifier + 1]
		self.item_multiplier = item_multiplier_lut[self.identifier + 1]
		self.book_multiplier = book_multiplier_lut[self.identifier + 1]
	
	
class Item(Node):
	def __init__(self, name, parent = None, children = None, item_type = "book", prior_work = 0, enchantments = []):
		self.item_type = item_type		# can be book or item. todo: differentiate between all different types of items to check enchantment compatibility
		self.prior_work = prior_work
		self.enchantments = enchantments
		self.cost = 0
		#self.value = 0
		self.name = name
		self.parent = parent
		if children:
			self.children = children
	
	def updateCost(self):
		# leaves can't update their children, also their prior work and enchantments are fixed and value is calculated differently
		if self.is_leaf:
			return
			
		self.children[0].updateCost()
		self.children[1].updateCost()
					
		possible, self.enchantments, combination_cost = combineEnchantments()
		self.cost = prior_work_penalty[self.children[0].prior_work] + prior_work_penalty[self.children[1].prior_work] + combination_cost # + repairing + renaming
		self.prior_work = min([max([self.children[0].prior_work, self.children[1].prior_work])], 5) + 1		#  prior work caps at 6, which maps to cost of 100 (i.e. too expensive)
	
		self.value = self.children[0].value + self.children[1].value
			
		# todo: reasons to break (figure out, how to propagate this break in order to )
		#  - cost is too expensive (>= 40)
		#  - target is book, sacrifice is item
		#  - combineEnchantments returns not possible (maybe because an enchantment marked as keep gets lost or no enchantments remain after checking combination and compatibility)
	
	# Returns the combined enchantments from both children as well as the resulting cost
	def combineEnchantments(self):
		ench = self.children[0].enchantments	# all target enchantments are kept
		cost = 0
		possible = False
		lut = self.children[1].item_type == "book" ? book_multiplier_lut : item_multiplier_lut
		for e in self.children[1].enchantments:
			# check combining
			# check compatibility
			ench.append(e)
			cost = cost + e.level * lut[e.identifier]
			possible = True
		return possible, ench, cost
		
	# Returns the value determined by an item's enchantments
	#def valueFromEnchantments(self):
	#	value = 0
	#	lut = self.item_type == "book" ? book_multiplier_lut : item_multiplier_lut
	#	for e in self.enchantments:
	#		value = value + e.level * lut[e.identifier]
		
		
		

def total_items(level):
	res = 1
	while(level > 0):
		res = res + pow(2, level)
		level = level - 1
	return res
	

def get_best_combination(tree):
	best_combination = 0
	
	# go through all possible combinations of start items
	# temp: add random prices to each leave
	for l in tree.leaves:
		l.cost = randint(1,9)
		
	# recalculate all costs of parents
	tree.updateCost()
	
	# formatted output
	print()
	print("===================")
	print()
	print(RenderTree(base_tree, style = DoubleStyle).by_attr(lambda n: n.name + ", Cost: " + str(n.cost)))
	
	return best_combination

	
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

# build base tree
base_tree = Item("")
# add two children to every leave until number of leaves matches possible_positions
while len(base_tree.leaves) < possible_positions:
	for n in base_tree.leaves:
		Item("Target", parent = n)
		Item("Sacrifice", parent = n)

base_tree.name = "Final item"

# remember base tree in order to return here later after each iteration
base_tree_leaves = base_tree.leaves

best_tree_variant = 0

# only operate on base tree if no aditional pairs need to be added
if (additional_leave_pairs == 0): get_best_combination(base_tree)

else:
	# build a list of all leaves indices
	indices = []
	for i in range(0, len(base_tree_leaves)): indices.append(i)
	
	# go through all possible positions for additional leave pairs
	tree_variant = 0
	for p in itertools.combinations(indices, additional_leave_pairs):
		
		# add an additional leave pair at each position
		for index in p:
			Item("Target", parent=base_tree_leaves[index])
			Item("Sacrifice", parent=base_tree_leaves[index])
			
		# tree is now ready		
		get_best_combination(base_tree)
		
		# return to base tree for next iteration
		for n in base_tree_leaves:
			n.children = ()
			
		tree_variant = tree_variant + 1



