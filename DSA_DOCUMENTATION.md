# Data Structures & Algorithms Documentation

This document explains the 6 custom DSA implementations used in the TinyURL application, their time/space complexities, and real-world applications.

---

## 1. Hash Map (hash_map.py)

### Overview
A custom hash map implementation using **separate chaining** for collision resolution and **polynomial rolling hash** for key distribution.

### Key Concepts

#### Hash Function
```python
hash_value = (hash_value * 31 + ord(char)) % capacity
```
- Uses prime number 31 for better distribution
- Polynomial rolling hash reduces collisions
- Modulo operation keeps index within array bounds

#### Separate Chaining
- Each bucket contains a linked list of nodes
- Collisions are handled by appending to the list
- Allows multiple keys to hash to the same index

#### Dynamic Resizing
- Monitors load factor (size / capacity)
- Resizes when load factor > 0.75
- Doubles capacity and rehashes all entries
- Maintains O(1) average case performance

### Time Complexity
- **Insert (put)**: O(1) average, O(n) worst case
- **Lookup (get)**: O(1) average, O(n) worst case
- **Delete**: O(1) average, O(n) worst case
- **Resize**: O(n) - happens rarely

### Space Complexity
- O(n) where n is number of entries

### Use in TinyURL
- **Primary storage**: Maps short_code → original_url
- **Fast lookups**: O(1) retrieval during redirects
- **Collision tracking**: Monitors hash collisions for statistics

### Real-World Applications
- Database indexing
- Caching systems (Redis, Memcached)
- Symbol tables in compilers
- Deduplication systems

---

## 2. Collision Detector (collision_detector.py)

### Overview
Detects when short codes collide and provides three resolution strategies.

### Collision Resolution Strategies

#### 1. Linear Probing
```
Original: abc
Collision: abc → abd → abe → abf
```
- Increments the code sequentially
- Simple and predictable
- Can cause clustering

**Time Complexity**: O(k) where k is number of attempts

#### 2. Regeneration
```
Original: abc
Collision: abc → x7K9mP (new random code)
```
- Generates completely new code using timestamp
- Avoids clustering
- Less predictable

**Time Complexity**: O(1) per generation

#### 3. Append Counter
```
Original: abc
Collision: abc → abc1 → abc2 → abc3
```
- Appends numeric suffix
- Preserves original code
- Easy to understand

**Time Complexity**: O(1)

### Use in TinyURL
- **Ensures uniqueness**: Guarantees no duplicate short codes
- **Flexible strategies**: User can choose preferred method
- **Statistics tracking**: Monitors collision rates

### Real-World Applications
- Database unique constraint handling
- File naming systems
- Session ID generation
- Distributed ID generation

---

## 3. Base62 Codec (base62_codec.py)

### Overview
Converts integers to Base62 strings using charset: `0-9a-zA-Z` (62 characters).

### How It Works

#### Encoding Algorithm
```python
number = 125
125 ÷ 62 = 2 remainder 1  → '1'
2 ÷ 62 = 0 remainder 2    → '2'
Result: "21" (reversed) = "21"
```

#### Why Base62?
- **URL-safe**: Only alphanumeric characters
- **Compact**: Shorter than Base10
- **Human-readable**: Unlike Base64 (+, /, =)
- **Case-sensitive**: More combinations than Base36

### Comparison
| ID      | Base10 | Base62 | Base64  |
|---------|--------|--------|---------|
| 1       | 1      | 1      | MQ==    |
| 100     | 100    | 1C     | MTAw    |
| 1000    | 1000   | g8     | MTAwMA== |
| 1000000 | 1000000| 4c92   | MTAwMDAwMA== |

### Time Complexity
- **Encode**: O(log₆₂(n))
- **Decode**: O(m) where m is string length

### Space Complexity
- O(log₆₂(n)) for encoded string

### Use in TinyURL
- **ID to short code**: Converts database auto-increment ID to short URL
- **Compact representation**: 7 characters = 3.5 trillion combinations
- **Reversible**: Can decode back to original ID

### Real-World Applications
- YouTube video IDs (11 chars = 73 quintillion)
- Bitly short URLs
- Database sharding keys
- Unique identifiers in distributed systems

---

## 4. LRU Cache (lru_cache.py)

### Overview
Least Recently Used cache using **doubly linked list** + **hash map** for O(1) operations.

### Data Structure Design

```
Hash Map: key → DLLNode
Doubly Linked List: [Head] ↔ [MRU] ↔ ... ↔ [LRU] ↔ [Tail]
```

#### Why Doubly Linked List?
- **O(1) removal**: Can remove from middle
- **O(1) insertion**: Can insert at front
- **Order tracking**: Maintains access order

#### Why Hash Map?
- **O(1) lookup**: Find node by key instantly
- **Direct access**: No need to traverse list

### Operations

#### Get Operation
1. Lookup key in hash map → O(1)
2. Move node to front (most recent) → O(1)
3. Return value → O(1)

**Total**: O(1)

#### Put Operation
1. Check if key exists → O(1)
2. If exists: update value, move to front → O(1)
3. If new: create node, add to front → O(1)
4. If capacity exceeded: remove LRU (tail) → O(1)

**Total**: O(1)

### Time Complexity
- **Get**: O(1)
- **Put**: O(1)
- **Delete**: O(1)

### Space Complexity
- O(capacity)

### Use in TinyURL
- **Cache popular URLs**: Avoid database queries
- **Fast lookups**: Check if URL already shortened
- **Automatic eviction**: Removes least used entries

### Cache Statistics
- **Hit rate**: Percentage of cache hits
- **Evictions**: Number of items removed
- **Utilization**: Current size vs capacity

### Real-World Applications
- Browser cache
- CDN caching (Cloudflare, Akamai)
- Database query cache
- CPU cache (L1, L2, L3)
- Operating system page replacement

---

## 5. Trie (Prefix Tree) (trie.py)

### Overview
Tree-based data structure for efficient prefix-based searching and autocomplete.

### Structure

```
Root
├── h
│   └── t
│       └── t
│           └── p (https://example.com)
└── w
    └── w
        └── w (www.google.com)
```

### Key Features

#### Prefix Sharing
- Common prefixes share nodes
- Space-efficient for similar strings
- Fast prefix matching

#### Frequency Tracking
- Each end node stores access frequency
- Enables popularity-based sorting
- Useful for autocomplete ranking

### Operations

#### Insert
```python
insert("https://example.com")
```
1. Traverse character by character
2. Create nodes if don't exist
3. Mark end node with URL and frequency

**Time**: O(m) where m = URL length

#### Search Prefix
```python
search_prefix("http", max_results=5)
```
1. Navigate to prefix end node → O(m)
2. Collect all URLs from subtree → O(k)
3. Sort by frequency → O(k log k)
4. Return top results

**Time**: O(m + k log k) where k = number of results

### Time Complexity
- **Insert**: O(m)
- **Search exact**: O(m)
- **Search prefix**: O(m + k) where k is results
- **Delete**: O(m)

### Space Complexity
- O(n × m) where n = number of URLs, m = average length
- Optimized by prefix sharing

### Use in TinyURL
- **URL search**: Find URLs by prefix
- **Autocomplete**: Suggest URLs as user types
- **Frequency ranking**: Show most popular matches

### Real-World Applications
- Autocomplete systems (Google Search)
- Spell checkers
- IP routing tables
- Dictionary implementations
- DNA sequence analysis

---

## 6. Min Heap (min_heap.py)

### Overview
Array-based binary heap for tracking top K URLs by click count.

### Heap Structure

```
Array: [5, 10, 15, 20, 25, 30]

Tree representation:
        5
       / \
      10  15
     / \  /
    20 25 30
```

### Array Indexing
- **Parent**: (i - 1) // 2
- **Left child**: 2i + 1
- **Right child**: 2i + 2

### Heap Property
- **Min Heap**: Parent ≤ Children
- Root contains minimum element
- Partially ordered (not fully sorted)

### Operations

#### Insert
1. Add element to end of array
2. Heapify up (bubble up)
3. Compare with parent, swap if smaller
4. Repeat until heap property restored

**Time**: O(log n)

#### Extract Min
1. Store root (minimum)
2. Move last element to root
3. Heapify down (bubble down)
4. Compare with children, swap with smaller
5. Repeat until heap property restored

**Time**: O(log n)

#### Get Min
- Return root element
**Time**: O(1)

### Top K URLs Algorithm

To track top K URLs:
1. Maintain heap of size K
2. Store (clicks, url_data) tuples
3. If new URL has more clicks than minimum:
   - Remove minimum
   - Insert new URL
4. Heap always contains top K URLs

**Space**: O(K)
**Insert**: O(log K)

### Time Complexity
- **Insert**: O(log n)
- **Extract Min**: O(log n)
- **Get Min**: O(1)
- **Heapify**: O(n)

### Space Complexity
- O(n)

### Use in TinyURL
- **Top K tracking**: Efficiently maintain top 10 URLs
- **Analytics**: Quick access to most popular URLs
- **Memory efficient**: Only stores K items, not all URLs

### Real-World Applications
- Priority queues (task scheduling)
- Dijkstra's shortest path algorithm
- Huffman coding (compression)
- Event-driven simulation
- Top K problems (trending topics)
- Median finding in streams

---

## Performance Comparison

### Time Complexities Summary

| Operation | Hash Map | LRU Cache | Trie | Min Heap | Base62 |
|-----------|----------|-----------|------|----------|--------|
| Insert    | O(1)*    | O(1)      | O(m) | O(log n) | O(log n) |
| Search    | O(1)*    | O(1)      | O(m) | O(n)     | O(m) |
| Delete    | O(1)*    | O(1)      | O(m) | O(log n) | - |
| Get Min   | -        | -         | -    | O(1)     | - |

*Average case, worst case O(n)

### Space Complexities

| Data Structure | Space Complexity |
|----------------|------------------|
| Hash Map       | O(n)            |
| LRU Cache      | O(capacity)     |
| Trie           | O(n × m)        |
| Min Heap       | O(n)            |
| Base62         | O(log n)        |

---

## Integration in TinyURL

### URL Shortening Flow

```
1. User submits URL
   ↓
2. Check LRU Cache (O(1))
   ↓
3. Check Database
   ↓
4. Insert to DB → Get ID
   ↓
5. Base62 Encode ID → short_code (O(log n))
   ↓
6. Collision Detection (O(1))
   ↓
7. If collision → Resolve (O(k))
   ↓
8. Store in HashMap (O(1))
   ↓
9. Store in Trie (O(m))
   ↓
10. Store in LRU Cache (O(1))
   ↓
11. Return short URL
```

### URL Redirect Flow

```
1. User visits short URL
   ↓
2. Check HashMap (O(1))
   ↓
3. If not found → Query DB
   ↓
4. Increment clicks in DB
   ↓
5. Update Trie frequency (O(m))
   ↓
6. Update Top K Heap (O(log k))
   ↓
7. Redirect to original URL
```

---

## Why These DSA Choices?

### Hash Map
- **Need**: Fast short_code → URL lookup
- **Why not array?**: Sparse data, wasted space
- **Why not tree?**: O(log n) slower than O(1)

### LRU Cache
- **Need**: Reduce database queries
- **Why not simple cache?**: No eviction strategy
- **Why not FIFO?**: LRU better for access patterns

### Trie
- **Need**: Prefix-based search
- **Why not hash map?**: Can't do prefix search
- **Why not array?**: O(n) search too slow

### Min Heap
- **Need**: Track top K URLs efficiently
- **Why not sort array?**: O(n log n) every time
- **Why not max heap?**: Need to remove minimum

### Base62
- **Need**: Short, URL-safe codes
- **Why not Base10?**: Longer codes
- **Why not Base64?**: +, /, = not URL-safe

### Collision Detector
- **Need**: Ensure unique short codes
- **Why not UUID?**: Too long (36 chars)
- **Why not random?**: Still need collision check

---

## Learning Outcomes

By implementing these DSAs from scratch, you learn:

1. **Hash Functions**: How to distribute data evenly
2. **Collision Resolution**: Different strategies and trade-offs
3. **Cache Eviction**: LRU vs LFU vs FIFO
4. **Tree Structures**: Prefix trees and traversal
5. **Heap Operations**: Heapify up/down algorithms
6. **Number Systems**: Base conversion algorithms
7. **Time/Space Trade-offs**: When to optimize for speed vs memory

---

## Testing & Validation

### Test Cases

#### Hash Map
- Insert 1000 items, verify all retrievable
- Test collision handling
- Verify dynamic resizing
- Check load factor maintenance

#### LRU Cache
- Fill to capacity, verify eviction
- Test hit/miss rates
- Verify access order maintenance

#### Trie
- Insert similar URLs, verify prefix sharing
- Test autocomplete with various prefixes
- Verify frequency ranking

#### Min Heap
- Insert random values, verify heap property
- Extract all, verify sorted order
- Test top K with updates

#### Base62
- Encode/decode round trip
- Test edge cases (0, 1, large numbers)
- Verify character set

#### Collision Detector
- Force collisions, test all strategies
- Verify uniqueness after resolution
- Check statistics tracking

---

## Performance Benchmarks

### Expected Performance (1M URLs)

| Operation | Time | Notes |
|-----------|------|-------|
| Shorten URL | ~5ms | Including DB insert |
| Redirect | ~1ms | Cache hit |
| Redirect | ~10ms | Cache miss + DB query |
| Search prefix | ~2ms | Top 5 results |
| Get top 10 | ~1ms | From heap |

### Memory Usage

| Component | Memory | For 1M URLs |
|-----------|--------|-------------|
| Hash Map | ~50MB | 50 bytes/entry |
| LRU Cache | ~5KB | 100 entries |
| Trie | ~100MB | Prefix sharing |
| Min Heap | ~1KB | Top 10 only |

---

## Conclusion

This TinyURL implementation demonstrates how fundamental data structures work together to create a production-ready system. Each DSA is chosen for specific performance characteristics and use cases, showing the importance of understanding algorithmic trade-offs in real-world applications.
