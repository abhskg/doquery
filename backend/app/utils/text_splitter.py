"""Text splitting utilities for document processing."""

from typing import List, Optional

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class TextSplitter:
    """
    Utility for splitting text into smaller, semantically meaningful chunks.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separator: str = "\n",
    ):
        """
        Initialize the text splitter.

        Args:
            chunk_size: Target size of each text chunk (in characters)
            chunk_overlap: Number of characters of overlap between chunks
            separator: Default separator to split on if needed
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        logger.debug(
            f"Initialized TextSplitter with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )

    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with reasonable boundaries.

        Args:
            text: The text to split

        Returns:
            List of text chunks
        """
        logger.debug(f"Splitting text of length {len(text)} characters")

        # Special case: text is shorter than chunk size
        if len(text) <= self.chunk_size:
            logger.debug("Text is shorter than chunk size, returning as single chunk")
            return [text]

        chunks = []
        start_idx = 0

        while start_idx < len(text):
            # If we're near the end, just take the rest
            if start_idx + self.chunk_size >= len(text):
                chunks.append(text[start_idx:])
                logger.debug(f"Added final chunk from index {start_idx} to end")
                break

            # Try to find a good stopping point
            end_idx = start_idx + self.chunk_size

            # Try to break at paragraph
            paragraph_break = text.rfind("\n\n", start_idx, end_idx)
            if (
                paragraph_break != -1
                and paragraph_break > start_idx + self.chunk_size // 2
            ):
                end_idx = paragraph_break + 2  # Include the double newline
                logger.debug(f"Found paragraph break at index {paragraph_break}")
            else:
                # Try to break at sentence
                sentence_break = self._find_sentence_end(text, start_idx, end_idx)
                if sentence_break != -1:
                    end_idx = sentence_break + 1  # Include the period
                    logger.debug(f"Found sentence break at index {sentence_break}")
                else:
                    # Just break at a space if possible
                    space_break = text.rfind(" ", start_idx, end_idx)
                    if (
                        space_break != -1
                        and space_break > start_idx + self.chunk_size // 2
                    ):
                        end_idx = space_break + 1
                        logger.debug(f"Found space break at index {space_break}")
                    else:
                        logger.debug(
                            f"No clean break found, using hard cutoff at index {end_idx}"
                        )

            # Add the chunk
            chunks.append(text[start_idx:end_idx])
            logger.debug(
                f"Added chunk from index {start_idx} to {end_idx} (length: {end_idx - start_idx})"
            )

            # Move to next chunk with overlap
            start_idx = end_idx - self.chunk_overlap

            # Make sure we're making progress
            if start_idx >= end_idx:
                start_idx = end_idx
                logger.debug("No progress made, moving to next position")

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def _find_sentence_end(self, text: str, start: int, end: int) -> int:
        """Find the end of a sentence within the given range."""
        # Look for periods followed by space or newline
        for i in range(end - 1, start, -1):
            if (
                i < len(text) - 1
                and text[i] == "."
                and (text[i + 1] == " " or text[i + 1] == "\n")
            ):
                return i

        # Also check for other sentence-ending punctuation
        for punct in ["!", "?"]:
            last_idx = text.rfind(punct, start, end)
            if last_idx != -1 and last_idx > start + self.chunk_size // 2:
                return last_idx

        return -1
