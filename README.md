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

```python
da = pyda.load(open("pyda.dump", "r"))
```

### instance attribute
#### .*da_size*
Size of base array(= check array).

####.*size*
Number of registerd words.

### instance method
#### .*build*(*words*, *address_nums*)

```python
da = pyda()
da.build(["hoge", "foo", "fuga"], [0, 1, 2])
```

#### .*insert*(*word*, *address_num*)

```pyhton
da = pyda()
da.insert("hoge", 12)
da.search("hoge") # => (12, -1)
```

#### .*upsert*(*word*, *address_num*)

```python
da = pyda()
da.insert("hoge", 10)
da.search("hoge") # => (10, -1)
da.insert("hoge", 20)
da.search("hoge") # => (10, -1)
da.upsert("hoge", 20)
da.search("hoge") # => (20, -1)
```

#### .*search*(*word*)

 ```python
 da = pyda()
 da.insert("hoge", 32)
 da.search("hoge") # => (32, -1)
 da.insert("hogehoge", 10)
 da.search("hoge") # => (32, 1)
 ```
 
#### .*common_prefix_search*(*word*[, *is_unicode*=False])

```python
da = pyda()
da.build(["foo", "fuga", "foot"], [23, 2, 10])
da.common_prefix_search("foo") #=> [("foo", 23), ("foot", 10)]
da.common_prefix_search("") # => [("foo", 23), ("foot", 10), ("fuga", 2)]
```

```python
da = pyda()
da.build([u"ほげ", u"ふが", u"ほむ"], [1, 2, 3])
da.common_prefix_search(u"ほ", is_unicode=True) # => [(u"ほげ", 1), (u"ほむ", 3)]
```

#### .*delete*(*word*)

```python
da = pyda()
da.insert("hoge", 10)
da.search("hoge") # => (10, -1)
da.delete("hoge")
da.search("hoge") # => (-1, -1)
```

#### .*dump*(*file_obj*)

```python
da = pyda()
da.build(["hoge", "foo", "fuga"], [0, 3, 5])
da.dump(open("pyda.dump", "w"))
```

## To Do
* make *.build* and *.insert* faster.
* refactoring!