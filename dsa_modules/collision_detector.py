"""
Collision Detection and Resolution Module
Detects when short codes collide and provides multiple resolution strategies
"""

import random
import string
import time
from .base62_codec import Base62Codec


class CollisionDetector:
    """
    Detects and resolves short code collisions
    Implements 3 strategies: Linear Probing, Regeneration, Append Counter
    """
    
    def __init__(self, hash_map):
        """
        Initialize collision detector
        
        Args:
            hash_map: HashMap instance to check for collisions
        """
        self.hash_map = hash_map
        self.collision_stats = {
            "total_collisions": 0,
            "linear_probing_used": 0,
            "regeneration_used": 0,
            "append_counter_used": 0,
            "max_attempts": 0
        }
    
    def detect_collision(self, short_code):
        """
        Check if a short code already exists
        
        Args:
            short_code (str): Short code to check
            
        Returns:
            bool: True if collision detected, False otherwise
        """
        return self.hash_map.contains(short_code)
    
    def resolve_collision(self, short_code, strategy='linear', max_attempts=10):
        """
        Resolve collision using specified strategy
        
        Args:
            short_code (str): Original short code that collided
            strategy (str): Resolution strategy ('linear', 'regenerate', 'append')
            max_attempts (int): Maximum number of attempts to find unique code
            
        Returns:
            tuple: (new_short_code, attempts_made, strategy_used)
            
        Raises:
            ValueError: If unable to resolve collision after max_attempts
        """
        attempts = 0
        new_code = short_code
        
        while attempts < max_attempts:
            attempts += 1
            
            if strategy == 'linear':
                new_code = self._linear_probing(short_code, attempts)
                strategy_used = 'linear_probing'
            elif strategy == 'regenerate':
                new_code = self._regenerate_code()
                strategy_used = 'regeneration'
            elif strategy == 'append':
                new_code = self._append_counter(short_code, attempts)
                strategy_used = 'append_counter'
            else:
                raise ValueError(f"Unknown collision resolution strategy: {strategy}")
            
            # Check if new code is unique
            if not self.detect_collision(new_code):
                # Update statistics
                self.collision_stats["total_collisions"] += 1
                self.collision_stats[f"{strategy_used}_used"] += 1
                self.collision_stats["max_attempts"] = max(
                    self.collision_stats["max_attempts"], 
                    attempts
                )
                return new_code, attempts, strategy_used
        
        # Failed to resolve collision
        raise ValueError(
            f"Unable to resolve collision for '{short_code}' after {max_attempts} attempts"
        )
    
    def _linear_probing(self, short_code, attempt):
        """
        Linear probing: Increment the code sequentially
        Example: abc -> abd -> abe -> abf
        
        Args:
            short_code (str): Original short code
            attempt (int): Current attempt number
            
        Returns:
            str: New short code
        """
        # Decode to number, add attempt, encode back
        try:
            number = Base62Codec.decode(short_code)
            new_number = number + attempt
            return Base62Codec.encode(new_number)
        except:
            # If decode fails, use simple character increment
            return self._increment_string(short_code, attempt)
    
    def _increment_string(self, s, increment):
        """
        Increment a string by treating it as a base-62 number
        
        Args:
            s (str): String to increment
            increment (int): Amount to increment
            
        Returns:
            str: Incremented string
        """
        charset = Base62Codec.CHARSET
        result = list(s)
        carry = increment
        
        for i in range(len(result) - 1, -1, -1):
            if carry == 0:
                break
            
            current_idx = charset.index(result[i])
            new_idx = (current_idx + carry) % len(charset)
            carry = (current_idx + carry) // len(charset)
            result[i] = charset[new_idx]
        
        # If still have carry, prepend new character
        while carry > 0:
            result.insert(0, charset[carry % len(charset)])
            carry //= len(charset)
        
        return ''.join(result)
    
    def _regenerate_code(self):
        """
        Regenerate a completely new random code
        Uses timestamp and random characters for uniqueness
        
        Returns:
            str: New random short code
        """
        # Use timestamp for uniqueness
        timestamp = int(time.time() * 1000000)  # Microseconds
        
        # Encode timestamp and add random suffix
        base_code = Base62Codec.encode(timestamp)
        
        # Take last 4-6 characters and add random char
        code_length = random.randint(4, 6)
        if len(base_code) > code_length:
            base_code = base_code[-code_length:]
        
        # Add random character for extra uniqueness
        random_char = random.choice(Base62Codec.CHARSET)
        return base_code + random_char
    
    def _append_counter(self, short_code, attempt):
        """
        Append counter to original code
        Example: abc -> abc1 -> abc2 -> abc3
        
        Args:
            short_code (str): Original short code
            attempt (int): Current attempt number
            
        Returns:
            str: Short code with appended counter
        """
        return f"{short_code}{attempt}"
    
    def get_collision_stats(self):
        """
        Get collision statistics
        
        Returns:
            dict: Statistics about collisions and resolutions
        """
        total = self.collision_stats["total_collisions"]
        
        stats = self.collision_stats.copy()
        
        # Add percentages
        if total > 0:
            stats["linear_probing_percentage"] = round(
                (stats["linear_probing_used"] / total) * 100, 2
            )
            stats["regeneration_percentage"] = round(
                (stats["regeneration_used"] / total) * 100, 2
            )
            stats["append_counter_percentage"] = round(
                (stats["append_counter_used"] / total) * 100, 2
            )
        else:
            stats["linear_probing_percentage"] = 0
            stats["regeneration_percentage"] = 0
            stats["append_counter_percentage"] = 0
        
        return stats
    
    def reset_stats(self):
        """Reset collision statistics"""
        self.collision_stats = {
            "total_collisions": 0,
            "linear_probing_used": 0,
            "regeneration_used": 0,
            "append_counter_used": 0,
            "max_attempts": 0
        }
