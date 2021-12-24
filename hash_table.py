class HashTable:
    def __init__(self, capacity):
        
        if not isinstance(capacity, int):
            capacity = int(capacity)
        
        self.capacity = capacity
        self.table = [None] * capacity
    
    @staticmethod
    def hash_code(string: str):
        string = str(string) # ensure input is cast to str for hash coding
        hc = 0 # what we'll return
        for character in string: # create hash code incrementally for each char in the str
            hc = 31 * hc + ord(character) # 31 is used because it is a prime number
        return hc

    def add(self, key, value):
        hc = HashTable.hash_code(key)
        bucket = hc % self.capacity
        if self.table[bucket] == None:
            self.table[bucket] = [(key, value)]
        else:
            self.table[bucket].append((key, value))

    def get(self, key):
        hc = HashTable.hash_code(key)
        bucket = hc % self.capacity
        if self.table[bucket] != None:
            for (K, V) in self.table[bucket]:
                if K == key:
                    return V
