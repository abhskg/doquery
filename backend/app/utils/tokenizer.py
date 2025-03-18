"""Tokenization utilities for document processing."""

import re
from typing import List, Optional, Union
import tiktoken


class Tokenizer:
    """
    Utility for tokenizing text and counting tokens.
    """
    
    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the tokenizer with the specified model.
        
        Args:
            model_name: The name of the model to use for tokenization
        """
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fall back to cl100k_base encoding (used for gpt-4, text-embedding-3-*)
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: Union[str, List[str]]) -> Union[int, List[int]]:
        """
        Count the number of tokens in a string or list of strings.
        
        Args:
            text: String or list of strings to count tokens for
            
        Returns:
            Token count or list of token counts
        """
        if isinstance(text, str):
            return len(self.encoding.encode(text))
        elif isinstance(text, list):
            return [len(self.encoding.encode(t)) for t in text]
        else:
            raise TypeError("Input must be a string or list of strings")
    
    def tokenize(self, text: str) -> List[int]:
        """
        Tokenize a string into token IDs.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of token IDs
        """
        return self.encoding.encode(text)
    
    def decode(self, tokens: List[int]) -> str:
        """
        Decode token IDs back into a string.
        
        Args:
            tokens: The token IDs to decode
            
        Returns:
            Decoded string
        """
        return self.encoding.decode(tokens) 