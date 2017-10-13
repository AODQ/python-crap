from drange import *
import os
# third line
# One Point
# Write a function that returns True if the file given file exists, and false otherwise
#
Check_File = os.path.exists;

print("Does /home/aodq/programming/dtoadq/dub.json exist?")
print(Check_File("/home/aodq/programming/dtoadq/dub.json"))
print("Does /home/aodq/programming/dtoadq/dubnot.json exist?")
print(Check_File("/home/aodq/programming/dtoadq/dubnot.json"))

#
# One Point
# Write a function that returns the 'n'th line of a file.
# It should only return one line!
#
# Second point:  If there is no argument, it returns the last line
#

Get_Line = lambda _fname, scount=-1: Move_at(File(_fname), scount);

print("This should be the third line")
thirdLine = Get_Line("quiz.py", 3)
print(thirdLine)

print("This should be the last line")
lastLine = Get_Line("quiz.py")
print(lastLine)


#
# One point
# Counts the number of files in the given directory.
# Just this diretcory, not searching the whole tree or subtree.
# SUBDIRS DO NOT COUNT!
# On error return 0

Count_Shallow_Walk = lambda d: (Range(*os.listdir(d))
                                .Filter(lambda t: not os.path.isdir(t))
                                .Array()
                                .Length());

print(Count_Shallow_Walk("."))

#last line
