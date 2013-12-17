# Double Array with Python
Implementation of Double Array with Python.

## How to Use

```
from pyda import pyda

da = pyda(10000) # 10000 is size of extending array

words = {"apple" => 1, "pine" => 2, "cherry" => 3, "pineapple" => 5}
for word, index in words.items():
    da.insert(word, index)

da.search("apple")    #=> (1, -1)
da.search("pine")     #=> (2, 1)  
da.search("cherry")   #=> (3, -1)
da.serch("pineapple") #=> (5, -1)
```
Return value of *.search* is a tuple, whose first element is registerd index and second is indicator if a same prefix word is registerd in this *double array*. Indicator is 1(-1) means same prefix word is(is not) registored.


## Document
under construction

## To Do
* add mathod *.delete*
* add method *.upsert*
* enable to common prefix search
* write test
* refactoring, refactoring, refactoring!!