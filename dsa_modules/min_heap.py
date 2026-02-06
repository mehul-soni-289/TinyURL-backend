"""
Min Heap Implementation
Array-based binary heap for tracking top K URLs by click count
Used for analytics and finding most popular URLs
"""

class MinHeap:
    """
    Min Heap implementation using array-based binary tree
    
    Time Complexity:
        - Insert: O(log n)
        - Extract Min: O(log n)
        - Get Min: O(1)
    Space Complexity: O(n)
    """
    
    def __init__(self):
        self.heap = []
        self.size = 0
    
    def _parent(self, index):
        """Get parent index"""
        return (index - 1) // 2
    
    def _left_child(self, index):
        """Get left child index"""
        return 2 * index + 1
    
    def _right_child(self, index):
        """Get right child index"""
        return 2 * index + 2
    
    def _swap(self, i, j):
        """Swap two elements in heap"""
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def _heapify_up(self, index):
        """
        Move element up to maintain heap property
        Called after insertion
        """
        while index > 0:
            parent_idx = self._parent(index)
            
            # Compare based on clicks (first element of tuple)
            if self.heap[index][0] < self.heap[parent_idx][0]:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break
    
    def _heapify_down(self, index):
        """
        Move element down to maintain heap property
        Called after extraction
        """
        while True:
            smallest = index
            left = self._left_child(index)
            right = self._right_child(index)
            
            # Find smallest among node and its children
            if left < self.size and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            
            if right < self.size and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest != index:
                self._swap(index, smallest)
                index = smallest
            else:
                break
    
    def insert(self, clicks, url_data):
        """
        Insert a new element into heap
        
        Args:
            clicks (int): Number of clicks (priority)
            url_data (dict): URL data including short_code, original_url, etc.
        """
        self.heap.append((clicks, url_data))
        self.size += 1
        self._heapify_up(self.size - 1)
    
    def extract_min(self):
        """
        Remove and return the minimum element
        
        Returns:
            tuple: (clicks, url_data) or None if heap is empty
        """
        if self.size == 0:
            return None
        
        if self.size == 1:
            self.size = 0
            return self.heap.pop()
        
        # Store min element
        min_element = self.heap[0]
        
        # Move last element to root and heapify down
        self.heap[0] = self.heap.pop()
        self.size -= 1
        self._heapify_down(0)
        
        return min_element
    
    def get_min(self):
        """
        Get minimum element without removing it
        
        Returns:
            tuple: (clicks, url_data) or None if heap is empty
        """
        return self.heap[0] if self.size > 0 else None
    
    def is_empty(self):
        """Check if heap is empty"""
        return self.size == 0
    
    def get_all_sorted(self):
        """
        Get all elements in sorted order (non-destructive)
        
        Returns:
            list: List of (clicks, url_data) tuples sorted by clicks
        """
        # Create a copy and extract all elements
        temp_heap = MinHeap()
        temp_heap.heap = self.heap.copy()
        temp_heap.size = self.size
        
        sorted_elements = []
        while not temp_heap.is_empty():
            sorted_elements.append(temp_heap.extract_min())
        
        return sorted_elements
    
    def clear(self):
        """Clear all elements from heap"""
        self.heap = []
        self.size = 0


class TopKURLs:
    """
    Track top K URLs by click count using Min Heap
    Maintains a fixed-size heap of K most clicked URLs
    """
    
    def __init__(self, k=10):
        """
        Initialize TopKURLs tracker
        
        Args:
            k (int): Number of top URLs to track
        """
        self.k = k
        self.heap = MinHeap()
        self.url_map = {}  # short_code -> (clicks, url_data) for quick lookup
    
    def add_or_update(self, short_code, clicks, url_data):
        """
        Add or update a URL in the top K tracker
        
        Args:
            short_code (str): Short code of URL
            clicks (int): Current click count
            url_data (dict): URL data
        """
        # If URL already in tracker, we need to rebuild heap
        if short_code in self.url_map:
            # Remove old entry and rebuild
            del self.url_map[short_code]
            self._rebuild_heap()
        
        # If heap not full, just insert
        if self.heap.size < self.k:
            self.heap.insert(clicks, url_data)
            self.url_map[short_code] = (clicks, url_data)
        else:
            # If new URL has more clicks than minimum, replace minimum
            min_clicks, _ = self.heap.get_min()
            if clicks > min_clicks:
                # Remove minimum
                removed = self.heap.extract_min()
                if removed:
                    removed_code = removed[1].get('short_code')
                    if removed_code in self.url_map:
                        del self.url_map[removed_code]
                
                # Insert new URL
                self.heap.insert(clicks, url_data)
                self.url_map[short_code] = (clicks, url_data)
    
    def _rebuild_heap(self):
        """Rebuild heap from url_map"""
        self.heap.clear()
        for short_code, (clicks, url_data) in self.url_map.items():
            self.heap.insert(clicks, url_data)
    
    def get_top_k(self):
        """
        Get top K URLs sorted by clicks (descending)
        
        Returns:
            list: List of url_data dicts with click counts
        """
        sorted_urls = self.heap.get_all_sorted()
        # Reverse to get descending order (most clicks first)
        return [(clicks, data) for clicks, data in reversed(sorted_urls)]
    
    def clear(self):
        """Clear all tracked URLs"""
        self.heap.clear()
        self.url_map.clear()
