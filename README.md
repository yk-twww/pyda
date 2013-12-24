# Double Array with Python
Implementation of Double Array with Python.
(Not so fast.)

## How to Use

```python
from pyda import pyda

da = pyda(1000) # 1000 is size used in extending array.

words = ["apple", "pine", "cherry", "pineapple"]
address = [3, 0, 5, 9]
da.build(words, address)

da.search("apple")     #=> (3, -1)
da.search("pine")      #=> (0,  1) :Second element is 1 since "pine" is prefix of "pineapple"
da.search("cherry")    #=> (5, -1)
da.search("pineapple") #=> (9, -1)
da.search("rose")      #=> (0, -1)

da.insert("rose", 12)
da.search("rose")      #=> (12, -1)
```
Returned value of *.search* is a tuple, whose first element is registerd index and second one is indicator whether a same prefix word is registerd in this *double array*. Indicator is 1(-1) means same prefix word is(is not) registored.


## Document
#### *class* **pyda**(extend_size)

## To Do
* implement an instance method *.delete*
* implement common prefix search
* make *.build* and *.insert* faster.
* refactoring!