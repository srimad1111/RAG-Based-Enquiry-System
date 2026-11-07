import re
from typing import Any, Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.logging import logger
from app.models.schemas import ChunkDetail, ChunkMetadata
from app.services.parser_service import DocumentContentBlock

settings = get_settings()


class ChunkingService:
    """
    Configurable recursive chunker that breaks document content blocks
    into clean, normalized text chunks with preserved metadata.
    """

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace, remove carriage returns, and clean repetitive newlines."""
        if not text:
            return ""
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse excessive inline spaces and tabs
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse more than two consecutive newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def split_blocks(
        self,
        blocks: List[DocumentContentBlock],
        document_id: str,
        document_name: str,
        product_name: str,
        product_version: str,
        category: str,
        document_type: str,
        upload_timestamp: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[ChunkDetail]:
        """
        Split a list of extracted DocumentContentBlocks into structured Chunks
        with full metadata preservation.
        """
        effective_chunk_size = chunk_size or settings.DEFAULT_CHUNK_SIZE
        effective_overlap = chunk_overlap or settings.DEFAULT_CHUNK_OVERLAP

        # Validate overlap constraint
        if effective_overlap >= effective_chunk_size:
            effective_overlap = max(0, effective_chunk_size // 4)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=effective_chunk_size,
            chunk_overlap=effective_overlap,
            separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
            keep_separator=True
        )

        chunks: List[ChunkDetail] = []
        chunk_index = 0

        for block in blocks:
            cleaned_block_text = self.clean_text(block.text)
            if not cleaned_block_text:
                continue

            # Split block text into sub-chunks
            raw_chunks = splitter.split_text(cleaned_block_text)

            for raw_chunk in raw_chunks:
                cleaned_chunk = self.clean_text(raw_chunk)
                # Requirement 8: Remove empty or trivial chunks
                if not cleaned_chunk or len(cleaned_chunk) < 15:
                    continue

                chunk_index += 1
                chunk_id = f"{document_id}_c{chunk_index:04d}"

                metadata = ChunkMetadata(
                    document_id=document_id,
                    document_name=document_name,
                    product_name=product_name,
                    product_version=product_version,
                    document_type=document_type,
                    section_title=block.section_title or "General",
                    page_number=block.page_number or 1,
                    upload_timestamp=upload_timestamp,
                    chunk_id=chunk_id,
                    category=category
                )

                chunk_obj = ChunkDetail(
                    id=chunk_id,
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text_content=cleaned_chunk,
                    char_count=len(cleaned_chunk),
                    section_title=block.section_title,
                    page_number=block.page_number,
                    metadata=metadata
                )
                chunks.append(chunk_obj)

        logger.info(
            f"Chunking complete for '{document_name}': generated {len(chunks)} chunks "
            f"(chunk_size={effective_chunk_size}, overlap={effective_overlap})"
        )
        return chunks


chunking_service = ChunkingService()

