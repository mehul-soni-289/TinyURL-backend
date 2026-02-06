"""
LRU (Least Recently Used) Cache Implementation
Uses Doubly Linked List + Hash Map for O(1) operations
Fixed capacity with automatic eviction of least recently used items
"""

class DLLNode:
    """Doubly Linked List Node"""
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """
    LRU Cache with O(1) get and put operations
    Uses doubly linked list for ordering and hash map for fast lookup
    
    Time Complexity: O(1) for get and put
    Space Complexity: O(capacity)
    """
    
    def __init__(self, capacity=100):
        """
        Initialize LRU Cache
        
        Args:
            capacity (int): Maximum number of items to cache
        """
        self.capacity = capacity
        self.cache = {}  # key -> DLLNode
        self.size = 0
        
        # Dummy head and tail for easier manipulation
        self.head = DLLNode(0, 0)
        self.tail = DLLNode(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _add_to_front(self, node):
        """Add node right after head (most recently used position)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove node from its current position"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_front(self, node):
        """Move existing node to front (mark as recently used)"""
        self._remove_node(node)
        self._add_to_front(node)
    
    def _remove_lru(self):
        """Remove least recently used item (node before tail)"""
        lru_node = self.tail.prev
        self._remove_node(lru_node)
        return lru_node
    
    def get(self, key):
        """
        Get value from cache
        
        Args:
            key: Key to lookup
            
        Returns:
            Value if found, None otherwise
        """
        if key in self.cache:
            node = self.cache[key]
            self._move_to_front(node)
            self.hits += 1
            return node.value
        
        self.misses += 1
        return None
    
    def put(self, key, value):
        """
        Put key-value pair in cache
        Evicts LRU item if capacity is reached
        
        Args:
            key: Key to store
            value: Value to store
        """
        # If key exists, update value and move to front
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._move_to_front(node)
            return
        
        # Create new node
        new_node = DLLNode(key, value)
        self.cache[key] = new_node
        self._add_to_front(new_node)
        self.size += 1
        
        # Check capacity and evict if needed
        if self.size > self.capacity:
            lru_node = self._remove_lru()
            del self.cache[lru_node.key]
            self.size -= 1
            self.evictions += 1
    
    def contains(self, key):
        """
        Check if key exists in cache without updating access time
        
        Args:
            key: Key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        return key in self.cache
    
    def delete(self, key):
        """
        Delete key from cache
        
        Args:
            key: Key to delete
            
        Returns:
            bool: True if deleted, False if key not found
        """
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            del self.cache[key]
            self.size -= 1
            return True
        return False
    
    def clear(self):
        """Clear all items from cache"""
        self.cache.clear()
        self.size = 0
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def get_stats(self):
        """
        Get cache statistics
        
        Returns:
            dict: Statistics including hits, misses, hit rate, etc.
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": self.size,
            "capacity": self.capacity,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "evictions": self.evictions,
            "utilization": round((self.size / self.capacity) * 100, 2)
        }
    
    def get_all_keys(self):
        """
        Get all keys in cache (from most to least recently used)
        
        Returns:
            list: List of keys in order of recency
        """
        keys = []
        current = self.head.next
        while current != self.tail:
            keys.append(current.key)
            current = current.next
        return keys
