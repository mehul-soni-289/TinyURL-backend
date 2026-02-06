"""
Trie (Prefix Tree) Implementation
Used for URL search and autocomplete functionality
Efficient prefix-based searching
"""

class TrieNode:
    """Node in the Trie structure"""
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.is_end_of_word = False
        self.url = None  # Store the full URL at end nodes
        self.frequency = 0  # Track how often this URL is accessed


class Trie:
    """
    Trie data structure for efficient prefix-based URL search
    
    Time Complexity:
        - Insert: O(m) where m is length of URL
        - Search: O(m + k) where k is number of results
    Space Complexity: O(n * m) where n is number of URLs
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.total_urls = 0
    
    def insert(self, url, frequency=1):
        """
        Insert a URL into the Trie
        
        Args:
            url (str): URL to insert
            frequency (int): Initial frequency count
        """
        if not url:
            return
        
        node = self.root
        url_lower = url.lower()  # Case-insensitive search
        
        for char in url_lower:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        # Mark end of URL
        if not node.is_end_of_word:
            self.total_urls += 1
        
        node.is_end_of_word = True
        node.url = url  # Store original URL (with original case)
        node.frequency = frequency
    
    def search(self, url):
        """
        Search for exact URL match
        
        Args:
            url (str): URL to search
            
        Returns:
            bool: True if URL exists, False otherwise
        """
        node = self._find_node(url.lower())
        return node is not None and node.is_end_of_word
    
    def _find_node(self, prefix):
        """
        Find the node corresponding to a prefix
        
        Args:
            prefix (str): Prefix to search
            
        Returns:
            TrieNode: Node if found, None otherwise
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def search_prefix(self, prefix, max_results=5):
        """
        Search for all URLs matching a prefix (autocomplete)
        
        Args:
            prefix (str): Prefix to search
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of tuples (url, frequency) sorted by frequency
        """
        if not prefix:
            return []
        
        prefix_lower = prefix.lower()
        node = self._find_node(prefix_lower)
        
        if node is None:
            return []
        
        # Collect all URLs with this prefix
        results = []
        self._collect_urls(node, results)
        
        # Sort by frequency (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]
    
    def _collect_urls(self, node, results):
        """
        Recursively collect all URLs from a node
        
        Args:
            node (TrieNode): Starting node
            results (list): List to append results to
        """
        if node.is_end_of_word:
            results.append((node.url, node.frequency))
        
        for child in node.children.values():
            self._collect_urls(child, results)
    
    def update_frequency(self, url):
        """
        Increment frequency count for a URL
        
        Args:
            url (str): URL to update
            
        Returns:
            bool: True if updated, False if URL not found
        """
        url_lower = url.lower()
        node = self._find_node(url_lower)
        
        if node and node.is_end_of_word:
            node.frequency += 1
            return True
        return False
    
    def delete(self, url):
        """
        Delete a URL from the Trie
        
        Args:
            url (str): URL to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        def _delete_helper(node, url_lower, index):
            if index == len(url_lower):
                if not node.is_end_of_word:
                    return False
                
                node.is_end_of_word = False
                node.url = None
                node.frequency = 0
                self.total_urls -= 1
                
                # Return True if node has no children (can be deleted)
                return len(node.children) == 0
            
            char = url_lower[index]
            if char not in node.children:
                return False
            
            child_node = node.children[char]
            should_delete_child = _delete_helper(child_node, url_lower, index + 1)
            
            if should_delete_child:
                del node.children[char]
                # Return True if current node can also be deleted
                return not node.is_end_of_word and len(node.children) == 0
            
            return False
        
        if not url:
            return False
        
        return _delete_helper(self.root, url.lower(), 0)
    
    def get_all_urls(self):
        """
        Get all URLs in the Trie
        
        Returns:
            list: List of all URLs
        """
        results = []
        self._collect_urls(self.root, results)
        return [url for url, _ in results]
    
    def get_stats(self):
        """
        Get statistics about the Trie
        
        Returns:
            dict: Statistics including total URLs, node count, etc.
        """
        def count_nodes(node):
            count = 1
            for child in node.children.values():
                count += count_nodes(child)
            return count
        
        total_nodes = count_nodes(self.root)
        
        return {
            "total_urls": self.total_urls,
            "total_nodes": total_nodes,
            "avg_nodes_per_url": round(total_nodes / self.total_urls, 2) if self.total_urls > 0 else 0
        }
    
    def clear(self):
        """Clear all URLs from the Trie"""
        self.root = TrieNode()
        self.total_urls = 0
