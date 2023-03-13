class Blockchain:
    """
    """
    def __init__(self):
        self.chain = []

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
        for t in self.chain[-1].list_of_transactions:
            print(t)

    def get_latest_block_hash(self):
        return self.chain[-1].hash

    def add_block(self, b):
        self.chain.append(b)
