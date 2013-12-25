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

        res1 = self.da.search("")
        assert res1 == (3, 1)

        res2 = self.da.search("pine")
        assert res2 == (1, 1)

        res3 = self.da.search("cherry")
        assert res3 == (2, -1)

        res4 = self.da.search("pineapple")
        assert res4 == (1, -1)

        res5 = self.da.search("apple")
        assert res5 == (-1, -1)

        res6 = self.da.search("pin")
        assert res6 == (-1, 1)


    def test_insert(self):
        words   = ["cherry blossom", "red", "red onion"]
        address = [10, 5, 8]

        for i in range(3):
            self.da.insert(words[i], address[i])

        res1 = self.da.search("cherry blossom")
        assert res1 == (10, -1)

        res2 = self.da.search("red")
        assert res2 == (5, 1)

        res3 = self.da.search("red onion")
        assert res3 == (8, -1)

        res4 = self.da.search("blue onion")
        assert res4 == (-1, -1)

        res5 = self.da.search("cherry")
        assert res5 == (-1, 1)


    def test_build_and_insert(self):
        words1   = ["", "pine", "cherry", "pineapple"]
        address1 = [3, 1, 2, 1]

        words2   = ["cherry blossom", "red", "red onion"]
        address2 = [10, 5, 8]


        self.da.build(words1, address1)

        res1 = self.da.search("cherry")
        assert res1 == (2, -1)

        res2 = self.da.search("red")
        assert res2 == (-1, -1)


        for i in range(3):
            self.da.insert(words2[i], address2[i])

        res3 = self.da.search("red")
        assert res3 == (5, 1)

        res4 = self.da.search("cherry")
        assert res4 == (2, 1)


    def test_insert_and_upsert(self):
        words   = ["", "pine", "cherry", "pineapple"]
        address = [3, 1, 2, 1]

        self.da.build(words, address)

        res1 = self.da.search("pine")
        assert res1 == (1, 1)

        self.da.insert("pine", 23)
        res2 = self.da.search("pine")
        assert res2 == (1, 1)

        self.da.upsert("pine", 23)
        res3 = self.da.search("pine")
        assert res3 == (23, 1)


    def test_large_build(self):
        words = self.read_words()
        address = range(len(words))

        #s_t = time.clock()
        self.da.build(words, address)
        #e_t = time.clock()
        #print "building: ", e_t - s_t, "sec"
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

        res1 = self.da.search("apple")
        assert res1 == (1, -1)

        self.da.delete("apple")
        res2 = self.da.search("apple")
        assert res2 == (-1, -1)

        res3 = self.da.search("banana")
        assert res3 == (-1, -1)

        self.da.delete("banana")
        res4 = self.da.search("banana")
        assert res4 == (-1, -1)

        assert self.da.search("pine") == (9, 1)
        assert self.da.search("pineapple") == (12, -1)
        self.da.delete("pineapple")
        assert self.da.search("pine") == (9, -1)



if __name__ == "__main__":
    unittest.main()
