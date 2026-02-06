"""
Custom Data Structures & Algorithms Module
All implementations built from scratch without external DSA libraries
"""

from .hash_map import HashMap
from .base62_codec import Base62Codec
from .lru_cache import LRUCache
from .trie import Trie
from .min_heap import MinHeap, TopKURLs
from .collision_detector import CollisionDetector

__all__ = [
    'HashMap',
    'Base62Codec',
    'LRUCache',
    'Trie',
    'MinHeap',
    'TopKURLs',
    'CollisionDetector'
]
