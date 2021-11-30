

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
        tuple = (key, value)
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
        return default

    def dump(self):
        for bucket in range(0, self.capacity):
            if self.table[bucket] != None:
                
                if len(self.table[bucket]) == 1:
                    print(f"bucket {bucket} has 1 entry")
                else:
                    print(f"bucket {bucket} has {len(self.table[bucket])} entries")
                
                for (K, V) in self.table[bucket]:
                    print(f"bucket {bucket} : K = {K}, V = {V}")
            else:
                print(f"bucket {bucket} is empty")
