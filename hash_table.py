class HashTable:
    def __init__(self, capacity):
        
        if not isinstance(capacity, int):
            capacity = int(capacity)
        
        self.capacity = capacity
        self.table = [None] * capacity
    
    @staticmethod
    def hash_code(string):
        h = 0
        for c in string:
            h = 31 * h + ord(c) # 31 is used because it is a prime number
        return h

    def add(self, key, value):
        hash_code = HashTable.hash_code(key)
        bucket = hash_code % self.capacity
        if self.table[bucket] == None:
            self.table[bucket] = [(key, value)]
        else:
            self.table[bucket].append((key, value))

    def get(self, key):
        hash_code = HashTable.hash_code(str(key))
        bucket = hash_code % self.capacity
        if self.table[bucket] != None:
            for (K, V) in self.table[bucket]:
                if K == key:
                    return V
