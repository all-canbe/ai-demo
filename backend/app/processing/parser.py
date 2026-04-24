import os
from typing import Any
from app.config.logging_config import get_logger

logger = get_logger(__name__)

SUPPORTED_TYPES = {"pdf", "docx", "doc", "png", "jpg", "jpeg", "txt", "md", "html"}


class ParseResult:
    def __init__(self):
        self.sections: list[dict[str, Any]] = []
        self.tables: list[dict[str, Any]] = []
        self.images: list[dict[str, Any]] = []
        self.formulas: list[dict[str, Any]] = []
        self.raw_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sections": self.sections,
            "tables": self.tables,
            "images": self.images,
            "formulas": self.formulas,
            "raw_text": self.raw_text,
        }


def parse_document(file_path: str) -> ParseResult:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    ext = file_path.rsplit(".", 1)[-1].lower()

    if ext not in SUPPORTED_TYPES:
        raise ValueError(f"不支持的文件类型: {ext}")

    logger.info(f"开始解析文档: {file_path} (类型: {ext})")

    if ext == "pdf":
        return _parse_pdf(file_path)
    elif ext in ("docx", "doc"):
        return _parse_docx(file_path)
    elif ext in ("png", "jpg", "jpeg"):
        return _parse_image(file_path)
    elif ext in ("txt", "md"):
        return _parse_text(file_path)
    elif ext == "html":
        return _parse_html(file_path)

    raise ValueError(f"无法解析的文件类型: {ext}")


def _parse_pdf(file_path: str) -> ParseResult:
    result = ParseResult()

    try:
        from magic_pdf.data.data_reader_writer import FileBasedDataReader, FileBasedDataWriter
        from magic_pdf.data.dataset import PymuDocDataset

        reader = FileBasedDataReader("")
        pdf_bytes = reader.read(file_path)
        ds = PymuDocDataset(pdf_bytes)

        if ds.classify() == "ocr":
            pipe = ds.apply_ocr()
        else:
            pipe = ds.apply_txt()

        output_dir = os.path.join(os.path.dirname(file_path), "images")
        os.makedirs(output_dir, exist_ok=True)
        content_list = pipe.get_content_list(FileBasedDataWriter, output_dir)

        page_num = 0
        for item in content_list:
            item_type = item.get("type", "")
            text = item.get("text", "")

            if item_type == "text":
                result.sections.append({
                    "id": f"sec_{page_num}_{len(result.sections)}",
                    "title": "",
                    "content": text,
                    "page": page_num,
                })
                result.raw_text += text + "\n"
            elif item_type == "table":
                result.tables.append({
                    "id": f"tab_{page_num}_{len(result.tables)}",
                    "content": text,
                    "page": page_num,
                })
            elif item_type == "image":
                result.images.append({
                    "id": f"img_{page_num}_{len(result.images)}",
                    "url": item.get("img_path", ""),
                    "description": text,
                    "page": page_num,
                })
            elif item_type == "equation":
                result.formulas.append({
                    "id": f"for_{page_num}_{len(result.formulas)}",
                    "content": text,
                    "page": page_num,
                })

            page_num += 1

        logger.info(f"MinerU解析PDF完成: {file_path}, 提取{len(result.sections)}个段落")
    except ImportError:
        logger.warning("MinerU未安装，使用PyMuPDF降级解析")
        result = _parse_pdf_fallback(file_path)
    except Exception as e:
        logger.error(f"MinerU解析失败: {e}, 使用降级方案")
        result = _parse_pdf_fallback(file_path)

    return result


def _parse_pdf_fallback(file_path: str) -> ParseResult:
    result = ParseResult()

    try:
        import fitz

        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if text.strip():
                result.sections.append({
                    "id": f"sec_{page_num}_0",
                    "title": "",
                    "content": text.strip(),
                    "page": page_num,
                })
                result.raw_text += text.strip() + "\n"

            try:
                tables = page.find_tables()
                for idx, table in enumerate(tables):
                    table_data = table.extract()
                    result.tables.append({
                        "id": f"tab_{page_num}_{idx}",
                        "content": str(table_data),
                        "page": page_num,
                    })
            except Exception:
                pass

        doc.close()
        logger.info(f"PyMuPDF解析PDF完成: {file_path}")
    except ImportError:
        logger.error("PyMuPDF未安装，无法解析PDF")
        raise

    return result


def _parse_docx(file_path: str) -> ParseResult:
    result = ParseResult()

    try:
        from docx import Document

        doc = Document(file_path)
        for idx, para in enumerate(doc.paragraphs):
            if para.text.strip():
                result.sections.append({
                    "id": f"sec_0_{idx}",
                    "title": "",
                    "content": para.text.strip(),
                    "page": 0,
                })
                result.raw_text += para.text.strip() + "\n"

        for idx, table in enumerate(doc.tables):
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            result.tables.append({
                "id": f"tab_0_{idx}",
                "content": str(rows),
                "page": 0,
            })

        logger.info(f"解析DOCX完成: {file_path}")
    except ImportError:
        logger.error("python-docx未安装，无法解析DOCX")
        raise

    return result


def _parse_image(file_path: str) -> ParseResult:
    result = ParseResult()

    try:
        from PIL import Image

        img = Image.open(file_path)

        try:
            import pytesseract
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        except (ImportError, Exception) as e:
            logger.warning(f"pytesseract不可用: {e}, 尝试基础OCR")
            text = ""

        if text.strip():
            result.sections.append({
                "id": "sec_0_0",
                "title": "",
                "content": text.strip(),
                "page": 0,
            })
            result.raw_text = text.strip()

        result.images.append({
            "id": "img_0_0",
            "url": file_path,
            "description": text.strip(),
            "page": 0,
        })

        logger.info(f"OCR解析图片完成: {file_path}")
    except ImportError:
        logger.error("Pillow未安装，无法解析图片")
        raise

    return result


def _parse_text(file_path: str) -> ParseResult:
    result = ParseResult()

    encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
    text = None

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read()
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if text is None:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    if text.strip():
        result.sections.append({
            "id": "sec_0_0",
            "title": "",
            "content": text.strip(),
            "page": 0,
        })
        result.raw_text = text.strip()

    logger.info(f"解析文本文件完成: {file_path}")
    return result


def _parse_html(file_path: str) -> ParseResult:
    result = ParseResult()

    try:
        from bs4 import BeautifulSoup

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        if text.strip():
            result.sections.append({
                "id": "sec_0_0",
                "title": "",
                "content": text.strip(),
                "page": 0,
            })
            result.raw_text = text.strip()

        logger.info(f"解析HTML完成: {file_path}")
    except ImportError:
        logger.error("beautifulsoup4未安装，无法解析HTML")
        raise

    return result
