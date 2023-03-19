import os
import sys
from io import StringIO

for i in os.listdir():
    for j in os.listdir(i):
        if(j == 'preprocess.py'):
            continue
        buffer = StringIO()
        with open(j, 'r') as f:
            for line in f:
                buffer.write(line.replace('id', ''))
        with open(j, 'w') as f:
            f.write(buffer.getvalue())
