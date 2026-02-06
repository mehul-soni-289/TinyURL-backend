"""
Custom Hash Map Implementation with Collision Handling
Uses separate chaining (linked list) for collision resolution
Dynamic resizing when load factor exceeds 0.75
"""

class HashNode:
    """Node for separate chaining in hash map"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashMap:
    """
    Custom Hash Map with polynomial rolling hash function
    Time Complexity: O(1) average case for all operations
    Space Complexity: O(n) where n is number of entries
    """
    
    def __init__(self, initial_capacity=16):
        self.capacity = initial_capacity
        self.size = 0
        self.buckets = [None] * self.capacity
        self.collision_count = 0
        self.LOAD_FACTOR_THRESHOLD = 0.75
        
    def _hash(self, key):
        """
        Polynomial rolling hash function
        Uses prime number 31 for better distribution
        """
        hash_value = 0
        prime = 31
        for char in str(key):
            hash_value = (hash_value * prime + ord(char)) % self.capacity
        return hash_value
    
    def _resize(self):
        """
        Double the capacity and rehash all entries
        Called when load factor > 0.75
        """
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        self.size = 0
        
        # Rehash all existing entries
        for bucket in old_buckets:
            current = bucket
            while current:
                self.put(current.key, current.value)
                current = current.next
    
    def put(self, key, value):
        """
        Insert or update key-value pair
        Returns: True if new entry, False if updated existing
        """
        # Check load factor and resize if needed
        if self.size / self.capacity > self.LOAD_FACTOR_THRESHOLD:
            self._resize()
        
        index = self._hash(key)
        
        # If bucket is empty, create new node
        if self.buckets[index] is None:
            self.buckets[index] = HashNode(key, value)
            self.size += 1
            return True
        
        # Traverse the chain to find key or end
        current = self.buckets[index]
        prev = None
        
        while current:
            if current.key == key:
                # Update existing key
                current.value = value
                return False
            prev = current
            current = current.next
        
        # Key not found, add to end of chain (collision)
        prev.next = HashNode(key, value)
        self.size += 1
        self.collision_count += 1
        return True
    
    def get(self, key):
        """
        Retrieve value by key
        Returns: value if found, None otherwise
        """
        index = self._hash(key)
        current = self.buckets[index]
        
        while current:
            if current.key == key:
                return current.value
            current = current.next
        
        return None
    
    def contains(self, key):
        """
        Check if key exists in hash map
        Returns: True if key exists, False otherwise
        """
        return self.get(key) is not None
    
    def delete(self, key):
        """
        Remove key-value pair
        Returns: True if deleted, False if key not found
        """
        index = self._hash(key)
        current = self.buckets[index]
        prev = None
        
        while current:
            if current.key == key:
                if prev is None:
                    # Deleting first node in chain
                    self.buckets[index] = current.next
                else:
                    prev.next = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        
        return False
    
    def get_stats(self):
        """
        Get statistics about the hash map
        """
        # Calculate chain lengths
        chain_lengths = []
        for bucket in self.buckets:
            length = 0
            current = bucket
            while current:
                length += 1
                current = current.next
            if length > 0:
                chain_lengths.append(length)
        
        avg_chain_length = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
        max_chain_length = max(chain_lengths) if chain_lengths else 0
        
        return {
            "size": self.size,
            "capacity": self.capacity,
            "load_factor": self.size / self.capacity,
            "collision_count": self.collision_count,
            "avg_chain_length": round(avg_chain_length, 2),
            "max_chain_length": max_chain_length,
            "non_empty_buckets": len(chain_lengths)
        }
    
    def clear(self):
        """Clear all entries from hash map"""
        self.buckets = [None] * self.capacity
        self.size = 0
        self.collision_count = 0
