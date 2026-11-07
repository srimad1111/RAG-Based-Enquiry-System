import re
from pathlib import Path
from typing import List, NamedTuple, Optional
import docx
import pymupdf as fitz  # PyMuPDF
from app.core.logging import logger


class DocumentContentBlock(NamedTuple):
    """Represents an extracted structural text block with metadata."""
    text: str
    section_title: str
    page_number: int


class DocumentParserService:
    """
    Extracts text and structural metadata (headings, page numbers)
    from PDF, DOCX, TXT, and Markdown files.
    """

    @staticmethod
    def extract_pdf(file_path: Path) -> List[DocumentContentBlock]:
        """
        Extract text from PDF using PyMuPDF, preserving page numbers
        and detecting section headings from text layout.
        """
        blocks: List[DocumentContentBlock] = []
        try:
            doc = fitz.open(str(file_path))
            current_section = file_path.stem.replace("_", " ").title()

            for page_idx, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if not page_text or not page_text.strip():
                    continue

                # Scan lines for potential section headings
                lines = [line.strip() for line in page_text.splitlines() if line.strip()]
                for line in lines[:5]:
                    # Heuristic for headings: short line, capitalized, or markdown #
                    if (line.startswith("#") or (len(line) < 70 and line.isupper()) or
                            (len(line) < 60 and line.istitle() and not line.endswith("."))):
                        current_section = line.lstrip("#").strip()
                        break

                blocks.append(DocumentContentBlock(
                    text=page_text,
                    section_title=current_section,
                    page_number=page_idx
                ))
            doc.close()
        except Exception as e:
            logger.error(f"Error extracting PDF content from {file_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse PDF file: {e}")

        return blocks

    @staticmethod
    def extract_docx(file_path: Path) -> List[DocumentContentBlock]:
        """
        Extract text from DOCX using python-docx, preserving paragraph styles,
        headings, and table contents.
        """
        blocks: List[DocumentContentBlock] = []
        try:
            doc = docx.Document(str(file_path))
            current_section = file_path.stem.replace("_", " ").title()
            current_buffer: List[str] = []
            page_counter = 1
            char_count = 0

            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue

                style_name = para.style.name.lower() if para.style else ""
                # Check for Word heading styles
                if "heading" in style_name or text.startswith("#"):
                    if current_buffer:
                        combined_text = "\n\n".join(current_buffer)
                        blocks.append(DocumentContentBlock(
                            text=combined_text,
                            section_title=current_section,
                            page_number=page_counter
                        ))
                        char_count += len(combined_text)
                        if char_count > 3000:
                            page_counter += 1
                            char_count = 0
                        current_buffer = []
                    current_section = text.lstrip("#").strip()
                else:
                    current_buffer.append(text)

            # Process tables in DOCX
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        table_lines.append(" | ".join(row_cells))
                if table_lines:
                    current_buffer.append("\nTable Data:\n" + "\n".join(table_lines))

            if current_buffer:
                combined_text = "\n\n".join(current_buffer)
                blocks.append(DocumentContentBlock(
                    text=combined_text,
                    section_title=current_section,
                    page_number=page_counter
                ))
        except Exception as e:
            logger.error(f"Error extracting DOCX content from {file_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse DOCX file: {e}")

        return blocks

    @staticmethod
    def extract_markdown(file_path: Path) -> List[DocumentContentBlock]:
        """
        Extract text from Markdown, breaking on #, ##, and ### section headings.
        """
        blocks: List[DocumentContentBlock] = []
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            default_title = file_path.stem.replace("_", " ").title()

            # Split on markdown headings while capturing heading lines
            heading_pattern = re.compile(r"^(#{1,3}\s+.+)$", re.MULTILINE)
            parts = heading_pattern.split(content)

            current_section = default_title
            page_counter = 1

            for part in parts:
                part_clean = part.strip()
                if not part_clean:
                    continue
                if part_clean.startswith("#"):
                    current_section = part_clean.lstrip("#").strip()
                else:
                    blocks.append(DocumentContentBlock(
                        text=part_clean,
                        section_title=current_section,
                        page_number=page_counter
                    ))
                    if len(part_clean) > 2500:
                        page_counter += 1
        except Exception as e:
            logger.error(f"Error extracting Markdown from {file_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse Markdown file: {e}")

        return blocks

    @staticmethod
    def extract_txt(file_path: Path) -> List[DocumentContentBlock]:
        """
        Extract plain text, detecting major section separators (===, ---, [Section]).
        """
        blocks: List[DocumentContentBlock] = []
        try:
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="latin-1", errors="replace")

            default_title = file_path.stem.replace("_", " ").title()
            paragraphs = content.split("\n\n")

            current_section = default_title
            current_buffer: List[str] = []
            page_counter = 1
            char_count = 0

            for para in paragraphs:
                p_strip = para.strip()
                if not p_strip:
                    continue

                # Detect header lines: e.g. [Section], === Header ===, or single short uppercase line
                if (re.match(r"^\[.+\]$", p_strip) or
                        re.match(r"^={3,}.+={3,}$", p_strip) or
                        (len(p_strip) < 60 and p_strip.isupper() and "\n" not in p_strip)):
                    if current_buffer:
                        text_joined = "\n\n".join(current_buffer)
                        blocks.append(DocumentContentBlock(
                            text=text_joined,
                            section_title=current_section,
                            page_number=page_counter
                        ))
                        char_count += len(text_joined)
                        if char_count > 2500:
                            page_counter += 1
                            char_count = 0
                        current_buffer = []
                    current_section = p_strip.strip("=[] -")
                else:
                    current_buffer.append(p_strip)

            if current_buffer:
                text_joined = "\n\n".join(current_buffer)
                blocks.append(DocumentContentBlock(
                    text=text_joined,
                    section_title=current_section,
                    page_number=page_counter
                ))
        except Exception as e:
            logger.error(f"Error extracting TXT from {file_path}: {e}", exc_info=True)
            raise ValueError(f"Failed to parse text file: {e}")

        return blocks

    def parse_document(self, file_path: Path) -> List[DocumentContentBlock]:
        """Main dispatcher based on file extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self.extract_pdf(file_path)
        elif suffix in (".docx", ".doc"):
            return self.extract_docx(file_path)
        elif suffix in (".md", ".markdown"):
            return self.extract_markdown(file_path)
        elif suffix in (".txt", ".text", ".log"):
            return self.extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported document format: {suffix}. Supported: PDF, DOCX, TXT, MD")


parser_service = DocumentParserService()
