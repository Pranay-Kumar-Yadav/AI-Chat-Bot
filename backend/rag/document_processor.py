"""Document processor for RAG - PDF and text extraction and chunking."""

from pathlib import Path
from typing import List, Tuple
import re
from loguru import logger

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf not installed, PDF processing disabled")


class DocumentProcessor:
    """
    Processor for documents including PDF and text files.
    Extracts text and splits into chunks for RAG.
    """

    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128):
        """
        Initialize document processor.

        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"DocumentProcessor initialized: chunk_size={chunk_size}, overlap={chunk_overlap}")

    async def process_file(self, file_path: Path) -> Tuple[str, List[str]]:
        """
        Process a file and return full text and chunks.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (full_text, chunks)
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            file_ext = file_path.suffix.lower()

            if file_ext == ".pdf":
                full_text = await self._process_pdf(file_path)
            elif file_ext in {".txt", ".md"}:
                full_text = await self._process_text_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            # Split into chunks
            chunks = self._split_text(full_text)

            logger.info(f"Processed {file_path.name}: {len(full_text)} chars, {len(chunks)} chunks")

            return full_text, chunks

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    async def _process_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not PYPDF_AVAILABLE:
            raise ImportError("pypdf is required for PDF processing. Install with: pip install pypdf")

        try:
            text_parts = []
            reader = PdfReader(file_path)

            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {len(reader.pages)} pages")

            return full_text

        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise

    async def _process_text_file(self, file_path: Path) -> str:
        """
        Read text from TXT or MD file.

        Args:
            file_path: Path to text file

        Returns:
            File content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Read {len(content)} characters from text file")
            return content

        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            raise

    def _split_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        # Clean text first
        text = self._clean_text(text)

        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Find chunk end
            end = start + self.chunk_size

            # Try to split at sentence boundary
            if end < len(text):
                # Find last period within buffer
                search_end = min(end + 100, len(text))
                last_period = text.rfind(".", start, search_end)

                if last_period > start:
                    end = last_period + 1
                else:
                    # Try to split at newline
                    last_newline = text.rfind("\n", start, search_end)
                    if last_newline > start:
                        end = last_newline + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start position with overlap
            start = end - self.chunk_overlap

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters but keep some punctuation
        text = re.sub(r"[^\w\s\.\,\!\?\'\"\-\:\;\(\)\n]", "", text)

        # Remove extra newlines
        text = re.sub(r"\n\n+", "\n", text)

        return text.strip()

    def get_statistics(self, text: str, chunks: List[str]) -> dict:
        """
        Get document statistics.

        Args:
            text: Full text
            chunks: List of chunks

        Returns:
            Statistics dictionary
        """
        word_count = len(text.split())
        avg_chunk_size = len(text) / len(chunks) if chunks else 0

        return {
            "total_characters": len(text),
            "total_words": word_count,
            "total_chunks": len(chunks),
            "average_chunk_size": int(avg_chunk_size),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }

