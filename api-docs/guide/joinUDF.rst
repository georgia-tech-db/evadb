Utility of the  Join UDF
========================

The basic functionality of the join UDF is to join a given list of words into a single string using a delimiter given as input.

Input: 
------
The join UDF takes a list(list(words)) as well as a delimiter as the input.

Output: 
-------
The ouput contains the same number of rows/lists provided in the input, such that words within each row/list are
joined to form a single sentence using the given delimiter. 
In other words, the ouput format is list(list(sentences)).

Example:
--------

Sample input: 
                [["I","am","a", "girl"],
                ["Bag", "of", "words"],
                ["House", "of", "cards"]]

Sample output: 
                [["I am a girl"],
                ["Bag of words"],
                ["House of cards"]]

This UDF overrides methods from the AbstractNdarrayUDF class:

        1. The name() function, simply returns the name of the UDF.

        2. The exec() function, performs the join operation over the given input of words and returns a list of resulting concatenated sentences as the output.


Testing of joinUDF:
------------------

The test_join.py file is available to test the functionality of the join_UDF.
