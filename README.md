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

da.search("apple")    #=> (3, -1)
da.search("pine")     #=> (0,  1) second element is 1 since "pine" is prefix of "pineapple"
da.search("cherry")   #=> (5, -1)
da.search("pineapple")#=> (9, -1)
da.search("rose")     #=> (-1, -1)

da.insert("rose", 12)
da.search("rose")      #=> (12, -1)
```
Returned value of *.search* is a tuple, whose first element is registerd index or -1 if the word is not found and second one is indicator whether a same prefix word is registerd in this *double array*. Indicator 1(-1) means same prefix word is(is not) registored.


## Documentation
### class
#### *pyda*(*extend_size*)
*extend_size* must be positive integer, which is used in extending arrays.

### class method
#### *load*(*file_obj*)

### instance attribute
#### .*da_size*
Size of base array(= check array).

####.*size*
Number of registerd words.

### instance method
#### .*build*(*words*, *address_nums*)

#### .*insert*(*word*, *address_num*)
#### .*upsert*(*word*, *address_num*)
#### .*search*(*word*)
#### .*common_prefix_search*(*word*[, *is_unicode*=False])
#### .*delete*(*word*)
#### .*dump*(*file_obj*)


## To Do
* make *.build* and *.insert* faster.
* refactoring!