from io import StringIO

class Blockchain:
    """
    """
    ## again default arg for endpoint initializaiton
    def __init__(self, chain = []):
        self.chain = chain

    def __len__(self):
        """
        Returns the amount of validated blocks in the chain.
        """
        return len(self.chain)

    def __str__(self):
        res = 'LIST OF BLOCKS IN BLOCKCHAIN:\n'
        for i, b in enumerate(self.chain):
            res += str(i) + '\n' + str(b)
        return res

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
