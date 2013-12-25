# -*- coding: utf-8 -*-

import unittest
import os
SRC_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../src"
import sys
sys.path.append(SRC_PATH)

from pyda import pyda
import time


class PydaTestCase(unittest.TestCase):
    def setUp(self):
        self.da = pyda(1000)

    def test_build(self):
        words   = ["", "pine", "cherry", "pineapple"]
        address = [3, 1, 2, 1]

        self.da.build(words, address)

        assert self.da.search("")          == (3, 1)
        assert self.da.search("pine")      == (1, 1)
        assert self.da.search("cherry")    == (2, -1)
        assert self.da.search("pineapple") == (1, -1)

        assert self.da.search("apple") == (-1, -1)
        assert self.da.search("pin")   == (-1, 1)


    def test_insert(self):
        words   = ["cherry blossom", "red", "red onion"]
        address = [10, 5, 8]

        for i in range(3):
            assert self.da.insert(words[i], address[i]) == 1

        assert self.da.search("cherry blossom") == (10, -1)
        assert self.da.search("red")            == (5, 1)
        assert self.da.search("red onion")      == (8, -1)

        assert self.da.search("blue onion") == (-1, -1)
        assert self.da.search("cherry")     == (-1, 1)


    def test_build_and_insert(self):
        words1   = ["", "pine", "cherry", "pineapple"]
        address1 = [3, 1, 2, 1]

        words2   = ["cherry blossom", "red", "red onion"]
        address2 = [10, 5, 8]


        self.da.build(words1, address1)

        assert self.da.search("cherry") == (2, -1)
        assert self.da.search("red")    == (-1, -1)


        for i in range(3):
            assert self.da.insert(words2[i], address2[i]) == 1

        assert self.da.search("red")    == (5, 1)
        assert self.da.search("cherry") == (2, 1)


    def test_insert_and_upsert(self):
        words   = ["", "pine", "cherry", "pineapple"]
        address = [3, 1, 2, 1]

        self.da.build(words, address)

        assert self.da.search("pine")     == (1, 1)
        assert self.da.insert("pine", 23) == 0
        assert self.da.search("pine")     == (1, 1)

        assert self.da.upsert("pine", 23) == 0
        assert self.da.search("pine")     == (23, 1)


    def test_large_build(self):
        words = self.read_words()
        address = range(len(words))

        self.da.build(words, address)

        for i in address:
            res = self.da.search(words[i])
            if res[0] != i:
                self.fail("")


    def test_large_insert(self):
        words = self.read_words()
        address = range(len(words))

        for i in address:
            self.da.insert(words[i], i)

        for i in address:
            res = self.da.search(words[i])
            if res[0] != i:
                self.fail("")


    def read_words(self):
        with open("dict.txt", "r") as f:
            words = []
            for line in f:
                words.append(line.rstrip())
            return words


    def test_delete(self):
        words   = ["apple", "rose", "pine", "pineapple"]
        address = [1, 4, 9, 12]

        self.da.build(words, address)

        assert self.da.search("apple") == (1, -1)
        assert self.da.delete("apple") == 1
        assert self.da.search("apple") == (-1, -1)

        assert self.da.search("banana") == (-1, -1)
        assert self.da.delete("banana") == 0
        assert self.da.search("banana") == (-1, -1)

        assert self.da.search("pine")      == (9, 1)
        assert self.da.search("pineapple") == (12, -1)
        assert self.da.delete("pineapple") == 1
        assert self.da.search("pine")      == (9, -1)
        assert self.da.search("pineapple") == (-1, -1)



if __name__ == "__main__":
    unittest.main()
