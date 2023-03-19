import os
import sys
from io import StringIO

for i in os.listdir():
    buffer = StringIO()
    with open(i, 'r') as f:
        for line in f:
            buffer.write(line.replace('', ''))
    with open(i, 'w') as f:
        f.write(buffer.getvalue())
