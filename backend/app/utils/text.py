from typing import Any, Dict, List

import tiktoken


class TextUtil:
    """
    Utility for text operations.
    """

    @staticmethod
    def split_text(
        text: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ) -> List[str]:
        """
        Split text into chunks with overlap.
        """
        # Implementation will be added later
        pass

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4") -> int:
        """
        Count tokens in a text.
        """
        # Implementation will be added later
        pass

    @staticmethod
    def extract_text_from_file(file_content: bytes, content_type: str) -> str:
        """
        Extract text from various file types.
        """
        # Implementation will be added later
        pass
