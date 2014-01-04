# -*- coding: utf-8 -*-

# This version is beta version
from collections import defaultdict, deque
from operator import itemgetter
try:
    import cPickle as pickle
except:
    import pickle



class pyda(object):
    @classmethod
    def load(cls, file_obj):
        da = pickle.load(file_obj)
        return da
        
    def __init__(self, extend_size):
        self.da_size = 3
        self.unused_head = 2
        self.unused_tail = 2
        self.base = [0, 1, -self.da_size]
        self.check = [0, 0, 0]
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
            current_node, left, right, wd_pt, is_leaf = stack.popleft()
            if is_leaf:
                self.write_base(current_node, address_nums[left])
                continue
            children, labels = self.make_child(words, left, right, wd_pt)
            new_base = self.search_empty(labels)
            self.write_base(current_node, new_base)
            for child in children:
                child[0] += new_base
                self.write_check(child[0], current_node)
            stack.extendleft(children)
        self.size += len(words)

    def make_child(self, words, left, right, wd_pt):
        children  = deque()
        labels = deque()
        label1 = self.char_trans(words[left][wd_pt]) if wd_pt < len(words[left]) else 1
        label2 = None
        _left = left
        for _right in xrange(left, right):
            label2 = self.char_trans(words[_right][wd_pt]) if wd_pt < len(words[_right]) else 1
            if label2 != label1:
                children.appendleft([label1, _left, _right, wd_pt + 1, label1 == 1])
                labels.appendleft(label1)
                label1 = label2
                _left = _right
        children.appendleft([label1, _left, _right + 1, wd_pt + 1, label1 == 1])
        labels.appendleft(label1)

        return children, labels


    def insert(self, word, address_num):
        current_node, wd_pt = self.failed_place(word)

        # wd_pt == -1 means word is already contained.
        if wd_pt == -1:
            return 0
        
        self._insert(current_node, word, wd_pt, address_num)
        return 1

    def upsert(self, word, address_num):
        current_node, wd_pt = self.failed_place(word)

        if wd_pt == -1:
            self.write_base(current_node, address_num)
            return 0

        self._insert(current_node, word, wd_pt, address_num)
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
        self.size += 1

    def insert_rest(self, current_node, word, wd_pt, address_num):
        while wd_pt < len(word) + 1:
            label = self.char_trans(word[wd_pt]) if wd_pt < len(word) else 1
            new_base = self.search_empty([label])
            self.write_base(current_node, new_base)
            next_node = new_base + label
            self.write_check(next_node, current_node)

            current_node = next_node
            wd_pt += 1
        
        self.write_base(current_node, address_num)


    def delete(self, word):
        word_len = len(word)
        current_node = 1
        wd_pt = 0
        
        while wd_pt < word_len:
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
        
        return 1


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
        return self.check_index[current_node][:]


    def search_empty(self, labels):
        node_cand = self.unused_head
        max_label = max(labels)
        while node_cand < self.da_size:
            cand_base = node_cand - labels[0]
            if cand_base >= 0 and all(not self.is_used(cand_base + label) for label in labels):
                max_node = cand_base + max_label
                if max_node >= self.da_size:
                    self.extend_array(max_node - self.da_size + self.extend_size)
                return cand_base
            node_cand = -self.base[node_cand]

        while True:
            if cand_base >= 0 and all(not self.is_used(cand_base + label) for label in labels):
                max_node = node_cand + max_label
                self.extend_array(max_node - self.da_size + self.extend_size)
                return cand_base
            cand_base += 1

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
    def write_base(self, node, base_val):
        if not self.is_used(node):
            next_node = -self.base[node]
            pre_node  = -self.check[node]
            if pre_node != 0:
                self.base[pre_node] = -next_node
            else:
                self.unused_head = next_node
            if next_node != self.da_size:
                self.check[next_node] = -pre_node
            else:
                self.unused_tail = pre_node

        self.base[node] = base_val
                            
    def write_check(self, node, check_val):
        if not self.is_used(node):
            next_node = -self.base[node]
            pre_node  = -self.check[node]
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
        else:
            return self.base[node]>=0 or self.check[node]>0

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
                stack.appendleft((prefix + self.recover_char(child_node - current_base,
                                                             is_unicode),
                                  child_node,
                                  child_node - current_base == 1))

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


# This object is a kind of Int List which ansure its ements is always sorted.
# And this List does't admit any two elements to be same.
class sorted_list(object):
    def __init__(self, ls = []):
        self.list = sorted(list(set(ls)))
    
    def __getitem__(self, i):
        return self.list[i]
    
    def __len__(self):
        return len(self.list)

    def iter(self, num):
        mid = len(self) / 2
        for i in xrange(mid, len(self)):
            yield self[i]
        while True:
            yield num
            num += 1

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

    # This method can be used only if elem is asured to be the biggest in list.
    def append(self, elem):
        self.list.append(elem)

    def pop(self, elem):
        index = self.index(elem)
        if index == -1:
            return
        
        del self.list[index]
