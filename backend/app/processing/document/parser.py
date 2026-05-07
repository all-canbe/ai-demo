import io
import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self, tesseract_path: str = None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def parse_pdf(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析PDF文档"""
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                pages = []
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    images = page.images
                    page_data = {
                        "page_number": page_num,
                        "text": text,
                        "images_count": len(images),
                        "has_text": len(text.strip()) > 0
                    }
                    pages.append(page_data)
            logger.info(f"PDF解析完成，共{len(pages)}页")
            return pages
        except Exception as e:
            logger.error(f"PDF解析失败: {str(e)}")
            raise

    def parse_word(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析Word文档"""
        try:
            doc = Document(io.BytesIO(file_content))
            paragraphs = []
            for para_num, paragraph in enumerate(doc.paragraphs, 1):
                text = paragraph.text.strip()
                if text:
                    paragraphs.append({
                        "paragraph_number": para_num,
                        "text": text,
                        "style": paragraph.style.name if paragraph.style else "Normal"
                    })
            
            tables = []
            for table_num, table in enumerate(doc.tables, 1):
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)
                if table_data:
                    tables.append({
                        "table_number": table_num,
                        "data": table_data
                    })
            
            result = {
                "paragraphs": paragraphs,
                "tables": tables,
                "total_paragraphs": len(paragraphs),
                "total_tables": len(tables)
            }
            logger.info(f"Word解析完成，{len(paragraphs)}个段落，{len(tables)}个表格")
            return result
        except Exception as e:
            logger.error(f"Word解析失败: {str(e)}")
            raise

    def parse_image(self, file_content: bytes, lang: str = "chi_sim+eng") -> Dict[str, Any]:
        """解析图片并提取OCR文本"""
        try:
            image = Image.open(io.BytesIO(file_content))
            text = pytesseract.image_to_string(image, lang=lang)
            
            result = {
                "text": text,
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "has_text": len(text.strip()) > 0
            }
            logger.info(f"图片OCR完成，文本长度: {len(text)}")
            return result
        except Exception as e:
            logger.error(f"图片解析失败: {str(e)}")
            raise

    def parse_text(self, file_content: bytes) -> Dict[str, Any]:
        """解析纯文本文件"""
        try:
            text = file_content.decode("utf-8", errors="replace")
            lines = text.split("\n")
            result = {
                "text": text,
                "lines_count": len(lines),
                "char_count": len(text)
            }
            logger.info(f"文本解析完成，{len(lines)}行，{len(text)}字符")
            return result
        except Exception as e:
            logger.error(f"文本解析失败: {str(e)}")
            raise

    def get_file_type(self, filename: str) -> str:
        """根据文件名判断文件类型"""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            return "pdf"
        elif lower_name.endswith((".docx", ".doc")):
            return "word"
        elif lower_name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif")):
            return "image"
        elif lower_name.endswith((".txt", ".md", ".json")):
            return "text"
        else:
            return "unknown"

    def parse(self, filename: str, file_content: bytes) -> Any:
        """统一解析入口"""
        file_type = self.get_file_type(filename)
        logger.info(f"开始解析文件: {filename}, 类型: {file_type}")
        
        if file_type == "pdf":
            return self.parse_pdf(file_content)
        elif file_type == "word":
            return self.parse_word(file_content)
        elif file_type == "image":
            return self.parse_image(file_content)
        elif file_type == "text":
            return self.parse_text(file_content)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
