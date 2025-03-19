"""Tokenization utilities for document processing."""

import re
from typing import List, Optional, Union
import tiktoken
from app.core.logging_config import get_logger

logger = get_logger(__name__)


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
        logger.debug(f"Initializing tokenizer for model: {model_name}")
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
            logger.debug(f"Using tiktoken encoding for model: {model_name}")
        except KeyError:
            # Fall back to cl100k_base encoding (used for gpt-4, text-embedding-3-*)
            logger.warning(f"No specific encoding found for {model_name}, falling back to cl100k_base")
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
            token_count = len(self.encoding.encode(text))
            logger.debug(f"Counted {token_count} tokens in string (length: {len(text)})")
            return token_count
        elif isinstance(text, list):
            token_counts = [len(self.encoding.encode(t)) for t in text]
            total_tokens = sum(token_counts)
            logger.debug(f"Counted {total_tokens} total tokens across {len(text)} strings")
            return token_counts
        else:
            error_msg = f"Input must be a string or list of strings, got {type(text)}"
            logger.error(error_msg)
            raise TypeError(error_msg)
    
    def tokenize(self, text: str) -> List[int]:
        """
        Tokenize a string into token IDs.
        
        Args:
            text: The text to tokenize
            
        Returns:
            List of token IDs
        """
        tokens = self.encoding.encode(text)
        logger.debug(f"Tokenized string into {len(tokens)} tokens")
        return tokens
    
    def decode(self, tokens: List[int]) -> str:
        """
        Decode token IDs back into a string.
        
        Args:
            tokens: The token IDs to decode
            
        Returns:
            Decoded string
        """
        text = self.encoding.decode(tokens)
        logger.debug(f"Decoded {len(tokens)} tokens into string (length: {len(text)})")
        return text 