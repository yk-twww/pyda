# -*- coding: utf-8 -*-

# This version is beta version
from collections import defaultdict

# fix end mark's number to 1
class pyda(object):
    def __init__(self, extend_size):
        self.base = [0, 1]
        self.check =[0, 0]
        self.da_size = 2
        self.check_index = defaultdict(list)
        self.unused_list= sorted_list()
        self.size = 0                        # number of contained elements
        self.extend_size = extend_size
    
    def char_trans(self, char):
        return ord(char) + 2

    def insert(self, word, address_num):
        (current_node, wd_pt) = self.failed_place(word)
        
        # wd_pt == -1 means word is already contained.
        # In this case, we replace address
        if wd_pt == -1:
            self.write_base(current_node, -address_num)
            return 0
        
        label = self.char_trans(word[wd_pt]) if wd_pt < len(word) else 1
        next_node = self.base[current_node] + label
        if next_node >= self.da_size or self.is_used(next_node):
            self.modify(current_node, label)
        
        self.insert_rest(current_node, word, wd_pt, address_num)
        self.size += 1
        return 1
    

    def insert_rest(self, current_node, word, wd_pt, address_num):
        while wd_pt < len(word) + 1:
            current_node, wd_pt = self.one_step_for_insert(current_node, word, wd_pt)
        
        self.write_base(current_node, -address_num)

    def one_step_for_insert(self, current_node, word, wd_pt):
        label = self.char_trans(word[wd_pt]) if wd_pt < len(word) else 1
        next_node = self.base[current_node] + label

        if next_node >= self.da_size or self.is_used(next_node):
            new_base = self.search_empty_for_one_label(label)
            self.write_base(current_node, new_base)
            next_node = new_base + label
        self.write_check(next_node, current_node)

        return (next_node, wd_pt + 1)


    def failed_place(self, word):
        word_len = len(word)
        current_node = 1
        wd_pt = 0
        
        while wd_pt < word_len:
            next_node = self.forward(current_node, word[wd_pt])
            if next_node == -1:
                return (current_node, wd_pt)
            current_node = next_node
            wd_pt += 1
        
        next_node = self.forward(current_node, 1, num_flag = 1)
        if next_node == -1:
            return (current_node, wd_pt)
        else:
            return (next_node, -1)
    

    def get_label(self, current_node):
        children = self.get_child(current_node)
        base_val = self.base[current_node]

        return [node - base_val for node in children]
    
    def get_child(self, current_node):
        children = self.check_index[current_node][:]
        
        return children

    def search_empty(self, label_ls):
        node_cands = self.unused_list.list
        cand_base = -1
        i = len(node_cands) / 2
        #i = 0
        while True:
            for j in xrange(i, len(node_cands)):
                cand_base = node_cands[j] - label_ls[0]
                if cand_base > 0:
                    i = j
                    break
            if cand_base > 0:
                break
            else:
                i = len(node_cands)
                self.extend_array(-cand_base + self.extend_size)
                
        
        while True:
            find_flag1 = 0
            for j in xrange(i, len(node_cands)):
                
                find_flag2 = 1
                cand_base = node_cands[j] - label_ls[0]
                for label in label_ls:
                    next_node = cand_base + label
                    if next_node < self.da_size:
                        if self.is_used(next_node):
                            find_flag2 = 0
                            break
                    else:
                        self.extend_array(next_node - self.da_size + self.extend_size)
                        find_flag2 = 0
                        break
                
                if find_flag2 == 1:
                    find_flag1 = 1
                    break
                else:
                    i = j
            if find_flag1 == 1:
                break
        
        return cand_base

    def search_empty_for_one_label(self, label):
        node_cands = self.unused_list.list
        cand_base = -1
        i = len(node_cands) / 2
        #i = 0
        while True:
            for j in xrange(i, len(node_cands)):
                cand_base = node_cands[j] - label
                if cand_base > 0:
                    break
            if cand_base > 0:
                break
            else:
                i = len(node_cands)
                self.extend_array(-cand_base + self.extend_size)
        return cand_base

    def modify(self, current_node, new_label):
        label_ls = self.get_label(current_node)
        new_base = self.search_empty(label_ls + [new_label])
        
        old_base = self.base[current_node]
        self.write_base(current_node, new_base)
        
        for label in label_ls:
            new_node = new_base + label
            self.write_check(new_node, current_node)
            
            old_node = old_base + label
            self.write_base(new_node, self.base[old_node])
            self.clear_node(old_node)
            
            children = self.get_child(old_node)
            for child_node in children:
                self.write_check(child_node, new_node)
    
    def write_base(self, node, base_val):
        before = self.is_used(node)
        self.base[node] = base_val
        after = self.is_used(node)
        
        if after and (not before):
            self.unused_list.pop(node)
        elif (not after) and before:
            self.unused_list.insert(node)
                            
    
    def write_check(self, node, check_val):
        old_check_val = self.check[node]
        before = self.is_used(node)
        self.check[node] = check_val
        after = self.is_used(node)
        
        if old_check_val != 0:
            self.check_index[old_check_val].remove(node)
        if check_val != 0:
            self.check_index[check_val].append(node)
      
        if after and (not before):
            self.unused_list.pop(node)
        elif (not after) and before:
            self.unused_list.insert(node)
    
    def is_used(self, node):
        return self.base[node] or self.check[node]
    
    def clear_node(self, node):
        self.write_base(node, 0)
        self.write_check(node, 0)
    
    # return taple (address, is_succeedable), if word does't exit, address = -1.
    # if next word may exist, is_succeedalbe = 1 else -1
    def search(self, word):
        word_len = len(word)
        current_node = 1
        wd_pt = 0
        
        while wd_pt < word_len:
            next_node = self.forward(current_node, word[wd_pt])
            if next_node == -1:
                return (-1, -1)
            current_node = next_node
            wd_pt += 1
        
        next_node = self.forward(current_node, 1, num_flag = 1)
        if next_node == -1:
            return (-1, 1)    # this is possibly (-1, self.is_succeed(current_node))
        else:
            return (-self.base[next_node], self.is_succeed(current_node, next_node))
    
    # does have current_node a child except to end_node
    def is_succeed(self, current_node, end_node):
        contain_num = len(self.check_index[current_node])
        
        if contain_num > 1:
            return 1
        else:
            return -1
    
    # decide whether it is transible.
    # if transible, return next node number, else return -1.
    def forward(self, current_node, char, num_flag = 0):
        next_node = self.base[current_node]
        next_node += self.char_trans(char) if num_flag == 0 else char
        if 0 < next_node < self.da_size and self.check[next_node] == current_node:
            return next_node
        else:
            return -1
    
    def extend_array(self, extend_size):
        add_arr = [0 for _ in xrange(extend_size)]
        self.base.extend(add_arr)
        self.check.extend(add_arr)
        self.unused_list.extend(range(self.da_size, self.da_size + extend_size))
        
        self.da_size += extend_size


# this object is a kind of Int List which ansure its
# elements is always sorted.
# And this List does't admit any two elements to be same.
class sorted_list(object):
    # list must not contain same elements.
    def __init__(self, ls = [], sorted_flag = 0):
        if sorted_flag:
            self.list = ls[:]
        else:
            self.list = sorted(list(set(ls)))
    
    def __getitem__(self, i):
        return self.list[i]
    
    def __len__(self):
        return len(self.list)

    def extend(self, arr):
        self.list.extend(arr)
    
    def index(self, elem):
        left = 0
        right = len(self) - 1
        
        if right == -1:
            return -1
        
        while left != right:
            mid = (left + right) / 2
            if self[mid] == elem:
                return mid
            elif self[mid] < elem:
                left = mid + 1
            else:
                right = mid
        
        if self[left] == elem:
            return left
        else:
            return -1
    
    def insert(self, elem):
        left = 0
        right = len(self) - 1
        
        if right == -1 or self[right] < elem :
            self.list.append(elem)
            return
        
        while left != right:
            mid = (left + right) / 2
            if self[mid] == elem:
                return
            elif self[mid] < elem:
                left = mid + 1
            else:
                right = mid
        
        if self[left] == elem:
            return
        else:
            self.list.insert(left, elem)

    # this messod can be used only if elem is asured
    # to be the biggest in list
    def append(self, elem):
        self.list.append(elem)

    def pop(self, elem):
        index = self.index(elem)
        if index == -1:
            return
        
        del self.list[index]
