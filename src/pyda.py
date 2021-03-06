# -*- coding: utf-8 -*-

# This version is beta version
from collections import defaultdict, deque
from operator import itemgetter
try:
    import cPickle as pickle
except:
    import pickle
import sys


class pyda(object):
    @classmethod
    def load(cls, file_obj):
        da = pickle.load(file_obj)
        return da
        
    def __init__(self, extend_size):
        self.da_size = 3
        self.unused_head = 2
        self.unused_tail = 2
        self.base = [0, 1, -self.da_size]  # Index 0 is not used since a check value
        self.check = [0, 0, 0]             # for used index need to be positive.
        self.check_index = defaultdict(list)
        self.size = 0                        # number of registerd words
        if extend_size < 1:
            raise Exception, "extend_size must be greater than 0"
        self.extend_size = extend_size

    def dump(self, file_obj):
        pickle.dump(self, file_obj)

    def char_trans(self, char): # fix end-mark's number to 1
        return ord(char) + 2

    def recover_char(self, num, is_unicode = False):
        if is_unicode:
            return unichr(num - 2) if num != 1 else u""
        else:
            return chr(num - 2) if num != 1 else ""

    def _sort_by_word(self, words, address_nums):
        if len(words) == 0:
            raise Exception, "first argument of .build must contain at least one element"
        elif len(words) != len(address_nums):
            raise Exception, "words number and address_nums number differ"
        pairs = zip(words, address_nums)
        pairs.sort(key=itemgetter(0))

        word_and_address = zip(*pairs)
        return word_and_address


    def build(self, words, address_nums):
        words, address_nums = self._sort_by_word(words, address_nums)

        stack = deque([[1, 0, len(words), 0, False]])
        while len(stack) > 0:
            current_node, left, right, wd_pt, is_leaf = stack.pop()
            if is_leaf:
                self.write_base(current_node, address_nums[left])
                continue

            children = deque()
            labels   = deque()
            label1 = self.char_trans(words[left][wd_pt]) if wd_pt < len(words[left]) else 1
            next_wd_pt = wd_pt + 1
            _left = left
            for _right in xrange(left, right):
                label2 = self.char_trans(words[_right][wd_pt]) if wd_pt < len(words[_right]) else 1
                if label2 != label1:
                    children.append([label1, _left, _right, next_wd_pt, label1 == 1])
                    labels.append(label1)
                    label1 = label2
                    _left = _right
            children.append([label1, _left, right, next_wd_pt, label1 == 1])
            labels.append(label1)

            new_base = self.search_empty(labels)
            self.write_base(current_node, new_base)
            for child in children:
                child[0] += new_base
                self.write_check(child[0], current_node)
            stack.extend(children)
        self.size += len(words)

    # EXPERIMENTAL: This method doesn't work well.
    def build2(self, words, address_nums):
        words, address_nums = self._sort_by_word(words, address_nums)

        stack = deque([[0, 1, 0, len(words), 0, False]])
        base_stack = deque([0])
        while len(stack) > 0:
            pre_node, label, left, right, wd_pt, is_leaf = stack.pop()
            base = base_stack.pop()
            current_node = base + label
            if current_node != 1:
                self.write_check(current_node, pre_node)
            if is_leaf:
                self.write_base(current_node, address_nums[left])
                continue

            labels = deque()
            label1 = self.char_trans(words[left][wd_pt]) if wd_pt < len(words[left]) else 1
            _left = left
            next_wd_pt = wd_pt + 1
            for _right in xrange(left, right):
                label2 = self.char_trans(words[_right][wd_pt]) if wd_pt < len(words[_right]) else 1
                if label2 != label1:
                    stack.append([current_node, label1, _left, _right, next_wd_pt, label1 == 1])
                    labels.append(label1)
                    label1 = label2
                    _left = _right
            stack.append([current_node, label1, _left, right, next_wd_pt, label1 == 1])
            labels.append(label1)

            new_base = self.search_empty(labels)
            self.write_base(current_node, new_base)
            base_stack.extend(new_base for _ in xrange(len(labels)))
        self.size += len(words)


    def insert(self, word, address_num):
        current_node, wd_pt = self.failed_place(word)

        # wd_pt == -1 means word is already contained.
        if wd_pt == -1:
            return 0
        
        self._insert(current_node, word, wd_pt, address_num)
        self.size += 1
        return 1

    def upsert(self, word, address_num):
        current_node, wd_pt = self.failed_place(word)

        if wd_pt == -1:
            self.write_base(current_node, address_num)
            return 0

        self._insert(current_node, word, wd_pt, address_num)
        self.size += 1
        return 1

    def _insert(self, current_node, word, wd_pt, address_num):
        label = self.char_trans(word[wd_pt]) if wd_pt < len(word) else 1
        next_node = self.base[current_node] + label
        if next_node >= self.da_size:
            self.extend_array(next_node - self.da_size + self.extend_size)
        elif self.is_used(next_node):
            new_base = self.search_empty(self.get_label(current_node) + [label])
            self.modify(current_node, new_base)
            next_node = new_base + label
        self.write_check(next_node, current_node)
        
        self.insert_rest(next_node, word, wd_pt+1, address_num)


    def insert_rest(self, current_node, word, wd_pt, address_num):
        wd_len = len(word)
        upper = wd_len + 1
        while wd_pt < upper:
            label = self.char_trans(word[wd_pt]) if wd_pt < wd_len else 1
            new_base = self.search_empty_for_one(label)
            self.write_base(current_node, new_base)
            next_node = new_base + label
            self.write_check(next_node, current_node)

            current_node = next_node
            wd_pt += 1
        
        self.write_base(current_node, address_num)

    # EXPERIMENTAL: This method works well, but is very slow.
    def insert_rest2(self, current_node, word, wd_pt, address_num):
        while wd_pt < len(word) + 1:
            label = self.char_trans(word[wd_pt]) if wd_pt < len(word) else 1
            next_node = self.search_empty_and_write_base(current_node, label)
            self.write_check(next_node, current_node)
            current_node = next_node
            wd_pt += 1
        
        self.write_base(current_node, address_num)


    def delete(self, word):
        current_node = 1
        wd_pt = 0

        wd_len = len(word)
        while wd_pt < wd_len:
            next_node = self.forward(current_node, word[wd_pt])
            if next_node == -1:
                return 0
            current_node = next_node
            wd_pt += 1
        
        end_node = self.forward(current_node, 1, num_flag = 1)
        if end_node == -1:
            return 0

        child_num = 0
        while child_num == 0:
            parent_node = self.check[end_node]
            self.clear_node(end_node)
            child_num = len(self.check_index[parent_node])
            end_node = parent_node

        self.size -= 1
        return 1


    def failed_place(self, word):
        current_node = 1
        wd_pt = 0

        wd_len = len(word)
        while wd_pt < wd_len:
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
        return self.check_index[current_node][:]


    def search_empty(self, labels):
        node_cand = self.unused_head
        max_label = max(labels)
        while node_cand < self.da_size:
            cand_base = node_cand - labels[0]
            if all(not self.is_used(cand_base + label) for label in labels):
                max_node = cand_base + max_label
                if max_node >= self.da_size:
                    self.extend_array(max_node - self.da_size + self.extend_size)
                return cand_base
            node_cand = -self.base[node_cand]

        cand_base = self.da_size - labels[0]
        while True:
            if all(not self.is_used(cand_base + label) for label in labels):
                max_node = cand_base + max_label
                self.extend_array(max_node - self.da_size + self.extend_size)
                return cand_base
            cand_base += 1

    def search_empty_for_one(self, label):
        return self.unused_head - label

    def modify(self, current_node, new_base):
        old_base = self.base[current_node]
        label_ls = self.get_label(current_node)
        self.write_base(current_node, new_base)
        
        for label in label_ls:
            new_node = new_base + label
            self.write_check(new_node, current_node)
            
            old_node = old_base + label
            self.write_base(new_node, self.base[old_node])
            
            children = self.get_child(old_node)
            for child_node in children:
                self.write_check(child_node, new_node)
            self.clear_node(old_node)

    # Don't use .write_base and .write_check methods for clearing node.
    # Don't use .write_base methods for unused node.
    # We suppose .write_check method is first used for unused node, then .write_base
    # method is used for it.
    def write_base(self, node, base_val):
        self.base[node] = base_val

    # EXPERIMENTAL: This method is used in experimental method .insert_rest2
    def search_empty_and_write_base(self, current_node, label):
        next_node = -self.base[current_node]
        new_base  = next_node - label

        if next_node == self.da_size:
            self.extend_array(5)
        self.base[current_node] = new_base

        return next_node

    def write_check(self, node, check_val):
        if not self.is_used(node):
            next_node = -self.base[node]
            pre_node  = -self.check[node]

            if self.unused_head == self.unused_tail:
                self.extend_array(self.extend_size)
            if pre_node != 0:
                self.base[pre_node] = -next_node
            else:
                self.unused_head = next_node
            if next_node != self.da_size:
                self.check[next_node] = -pre_node
            else:
                self.unused_tail = pre_node

        old_check_val = self.check[node]
        if old_check_val > 0:
            self.check_index[old_check_val].remove(node)
        self.check_index[check_val].append(node)

        self.check[node] = check_val


    def is_used(self, node):
        if node >= self.da_size:
            return False
        elif node <= 1:
            return True
        else:
            return self.check[node] > 0

    # Don't use this method for a node which is not used.
    # You must not use .write_base and .write_check methods in this method.
    def clear_node(self, node):
        self.base[node] = -self.unused_head
        old_check_val = self.check[node]
        self.check[node] = 0
        self.check[self.unused_head] = -node
        self.unused_head = node

        if old_check_val > 0:
            self.check_index[old_check_val].remove(node)

    # Return taple (address, contain_same_prefix_word?).
    # If word does't contained, address = -1 else return registerd address.
    # If there contained a word which has same prefix, is_succeedalbe = 1 else -1.
    def search(self, word):
        current_node = 1
        wd_pt = 0

        wd_len = len(word)
        while wd_pt < wd_len:
            next_node = self.forward(current_node, word[wd_pt])
            if next_node == -1:
                return (-1, -1)
            current_node = next_node
            wd_pt += 1
        
        next_node = self.forward(current_node, 1, num_flag = 1)
        if next_node == -1:
            return (-1, 1)    # This is possibly (-1, self.is_succeed(current_node))
        else:
            return (self.base[next_node], self.is_succeed(current_node, next_node))


    def common_prefix_search(self, word, is_unicode=False):
        current_node, wd_pt = self.failed_place(word)
        if wd_pt == -1:
            current_node = self.check[current_node]
        elif wd_pt < len(word):
            return []

        searched_words = deque()
        stack = deque([(word, current_node, False)])
        while len(stack) > 0:
            prefix, current_node, is_leaf = stack.popleft()
            if is_leaf:
                searched_words.append((prefix, self.base[current_node]))
                continue
            child_nodes = self.get_child(current_node)
            current_base = self.base[current_node]
            for child_node in child_nodes:
                stack.appendleft((
                    prefix + self.recover_char(child_node - current_base, is_unicode),
                    child_node,
                    child_node - current_base == 1
                ))

        return list(searched_words)


    # Check whether current_node has a child except to end_node.
    def is_succeed(self, current_node, end_node):
        contain_num = len(self.check_index[current_node])
        
        if contain_num > 1:
            return 1
        else:
            return -1
    
    # Check whether it is transible.
    # If transible, return next node number, else return -1.
    def forward(self, current_node, char, num_flag = 0):
        next_node = self.base[current_node]
        next_node += self.char_trans(char) if num_flag == 0 else char
        if 0 < next_node < self.da_size and self.check[next_node] == current_node:
            return next_node
        else:
            return -1
    
    def extend_array(self, extend_size):
        self.base.extend( xrange(-self.da_size - 1, -self.da_size - extend_size - 1, -1))
        self.check.extend(xrange(-self.da_size + 1, -self.da_size - extend_size + 1, -1))

        self.check[self.da_size] = -self.unused_tail
        self.da_size += extend_size
        self.unused_tail = self.da_size - 1
