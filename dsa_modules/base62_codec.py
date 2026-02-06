"""
Base62 Encoding/Decoding Implementation
Character set: 0-9a-zA-Z (62 characters)
Used to convert database IDs to short codes
Time Complexity: O(log₆₂(n)) for both encode and decode
"""

class Base62Codec:
    """
    Base62 encoder/decoder for converting integers to short strings
    """
    
    # Character set: digits + lowercase + uppercase = 62 chars
    CHARSET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BASE = 62
    
    @classmethod
    def encode(cls, number):
        """
        Encode a positive integer to base62 string
        
        Args:
            number (int): Positive integer to encode
            
        Returns:
            str: Base62 encoded string
            
        Example:
            encode(125) -> "2D"
            encode(1000) -> "g8"
        """
        if number == 0:
            return cls.CHARSET[0]
        
        if number < 0:
            raise ValueError("Cannot encode negative numbers")
        
        result = []
        while number > 0:
            remainder = number % cls.BASE
            result.append(cls.CHARSET[remainder])
            number //= cls.BASE
        
        # Reverse because we built it backwards
        return ''.join(reversed(result))
    
    @classmethod
    def decode(cls, encoded_string):
        """
        Decode a base62 string to integer
        
        Args:
            encoded_string (str): Base62 encoded string
            
        Returns:
            int: Decoded integer
            
        Example:
            decode("2D") -> 125
            decode("g8") -> 1000
        """
        if not encoded_string:
            raise ValueError("Cannot decode empty string")
        
        result = 0
        for char in encoded_string:
            if char not in cls.CHARSET:
                raise ValueError(f"Invalid character '{char}' in base62 string")
            
            result = result * cls.BASE + cls.CHARSET.index(char)
        
        return result
    
    @classmethod
    def validate(cls, encoded_string):
        """
        Validate if a string is a valid base62 encoded string
        
        Args:
            encoded_string (str): String to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not encoded_string:
            return False
        
        return all(char in cls.CHARSET for char in encoded_string)
