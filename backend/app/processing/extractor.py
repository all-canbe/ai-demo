from typing import Any
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class ExtractionResult:
    def __init__(self):
        self.entities: list[dict[str, Any]] = []
        self.relations: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": self.entities,
            "relations": self.relations,
        }


EXTRACTION_PROMPT = """你是一个信息提取专家。请从以下文本中提取结构化信息。

请提取以下类型的实体：
- Person（人物）
- Organization（组织）
- Location（地点）
- Concept（概念）

以及实体之间的关系。

请以JSON格式返回，格式如下：
{
    "entities": [
        {"id": "ent_1", "type": "Person", "name": "实体名称", "description": "描述"}
    ],
    "relations": [
        {"source": "ent_1", "target": "ent_2", "type": "RELATED_TO", "description": "关系描述"}
    ]
}

文本内容：
{text}
"""


def extract_info(parse_result_dict: dict[str, Any], document_id: str) -> ExtractionResult:
    result = ExtractionResult()

    raw_text = parse_result_dict.get("raw_text", "")
    if not raw_text:
        logger.warning(f"文档 {document_id} 无文本内容，跳过信息提取")
        return result

    try:
        result = _extract_with_langextract(raw_text, document_id)
    except ImportError:
        logger.info("LangExtract未安装，尝试LLM提取")
        try:
            result = _extract_with_llm(raw_text, document_id)
        except Exception as e:
            logger.error(f"LLM信息提取失败: {e}, 使用规则降级方案")
            result = _extract_with_rules(raw_text, document_id)
    except Exception as e:
        logger.error(f"LangExtract提取失败: {e}, 尝试LLM提取")
        try:
            result = _extract_with_llm(raw_text, document_id)
        except Exception as llm_e:
            logger.error(f"LLM信息提取也失败: {llm_e}, 使用规则降级方案")
            result = _extract_with_rules(raw_text, document_id)

    for entity in result.entities:
        entity["document_id"] = document_id

    logger.info(f"信息提取完成: 文档 {document_id}, 实体 {len(result.entities)} 个, 关系 {len(result.relations)} 条")
    return result


def _extract_with_langextract(text: str, document_id: str) -> ExtractionResult:
    result = ExtractionResult()

    from langextract import extract as langextract_extract

    chunk_size = 3000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    entity_counter = 0
    for chunk in chunks:
        extraction = langextract_extract(
            text=chunk,
            model="openai",
            entity_types=["Person", "Organization", "Location", "Concept"],
        )

        for entity in extraction.get("entities", []):
            entity_counter += 1
            result.entities.append({
                "id": f"ent_{document_id}_{entity_counter}",
                "type": entity.get("type", "Concept"),
                "name": entity.get("name", ""),
                "description": entity.get("description", ""),
            })

        for relation in extraction.get("relations", []):
            result.relations.append({
                "source": relation.get("source", ""),
                "target": relation.get("target", ""),
                "type": relation.get("type", "RELATED_TO"),
                "description": relation.get("description", ""),
            })

    logger.info(f"LangExtract提取完成: {len(result.entities)} 个实体")
    return result


def _extract_with_llm(text: str, document_id: str) -> ExtractionResult:
    result = ExtractionResult()

    from app.integrations.llm import llm_service

    chunk_size = 3000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    entity_counter = 0
    for chunk in chunks:
        prompt = EXTRACTION_PROMPT.format(text=chunk)
        response = llm_service.generate(prompt)

        parsed = _parse_extraction_response(response)
        for entity in parsed.get("entities", []):
            entity_counter += 1
            entity["id"] = f"ent_{document_id}_{entity_counter}"
            result.entities.append(entity)

        for relation in parsed.get("relations", []):
            result.relations.append(relation)

    logger.info(f"LLM提取完成: {len(result.entities)} 个实体")
    return result


def _extract_with_rules(text: str, document_id: str) -> ExtractionResult:
    result = ExtractionResult()

    import re

    patterns = {
        "Person": [
            re.compile(r'[\u4e00-\u9fa5]{2,4}(?=说|表示|认为|指出|强调|透露|称)'),
        ],
        "Organization": [
            re.compile(r'[\u4e00-\u9fa5]+(?:公司|集团|机构|委员会|部门|大学|学院|研究所|银行|基金)'),
        ],
        "Location": [
            re.compile(r'[\u4e00-\u9fa5]+(?:省|市|区|县|镇|村|路|街|道)'),
        ],
    }

    entity_counter = 0
    for entity_type, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = pattern.findall(text)
            seen = set()
            for match in matches:
                if match not in seen and len(match) >= 2:
                    seen.add(match)
                    entity_counter += 1
                    result.entities.append({
                        "id": f"ent_{document_id}_{entity_counter}",
                        "type": entity_type,
                        "name": match,
                        "description": f"从文档中提取的{entity_type}实体",
                        "document_id": document_id,
                    })

    logger.info(f"规则提取完成: {len(result.entities)} 个实体")
    return result


def _parse_extraction_response(response: str) -> dict[str, Any]:
    import json

    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        logger.warning("LLM返回的JSON解析失败")

    return {"entities": [], "relations": []}
