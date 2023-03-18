from io import StringIO
from copy import deepcopy

class Blockchain:
    """
    """
    ## again default arg for endpoint initializaiton
    def __init__(self, chain = []):
        self.chain = deepcopy(chain)

    def __len__(self):
        """
        Returns the amount of validated blocks in the chain.
        """
        return len(self.chain)

    def __str__(self):
        res = StringIO()
        res.write('LIST OF BLOCKS IN BLOCKCHAIN:\n')
        for i, b in enumerate(self.chain):
            res.write('BLOCK #')
            res.write(str(i))
            res.write('\n')
            res.write(str(b))
        return res.getvalue()

    def as_dict(self):
        return {'chain': [b.as_dict() for b in self.chain]}

    def view_transactions(self):
        if(len(self.chain) == 0):
            raise Exception("Empty Blockchain")
        ## for each transaction in the last block
        ans = StringIO()
        for t in self.chain[-1].list_of_transactions:
            ans.write(str(t))
        return ans.getvalue()

    def get_latest_block_hash(self):
        if(len(self.chain) > 0):
            return self.chain[-1].hash
        else:
            return 1

    def add_block(self, b):
        self.chain.append(b)
