from typing import Any, Optional
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


class Neo4jClient:
    def __init__(self):
        self._driver = None
        self._connected = False

    def _get_driver(self):
        if self._driver is None:
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=30,
                )
                self._driver.verify_connectivity()
                self._connected = True
                logger.info(f"Neo4j连接成功: {settings.NEO4J_URI}")
            except Exception as e:
                self._connected = False
                logger.error(f"Neo4j连接失败: {e}")
                raise
        return self._driver

    @property
    def driver(self):
        return self._get_driver()

    def is_connected(self) -> bool:
        if not self._connected or self._driver is None:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            self._connected = False
            return False

    def verify_connectivity(self):
        self._get_driver()
        self._driver.verify_connectivity()

    def _reconnect(self):
        self.close()
        try:
            self._get_driver()
            logger.info("Neo4j重连成功")
        except Exception as e:
            logger.error(f"Neo4j重连失败: {e}")
            raise

    def close(self):
        if self._driver:
            try:
                self._driver.close()
            except Exception:
                pass
            self._driver = None
            self._connected = False

    def execute_query(self, query: str, parameters: dict | None = None) -> list[dict]:
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j查询执行失败: {e}")
            self._connected = False
            try:
                self._reconnect()
                with self.driver.session() as session:
                    result = session.run(query, parameters or {})
                    return [record.data() for record in result]
            except Exception as retry_e:
                logger.error(f"Neo4j重试查询失败: {retry_e}")
                raise

    def create_document_node(self, document_id: str, name: str, doc_type: str) -> None:
        query = """
        MERGE (d:Document {id: $id})
        SET d.name = $name, d.type = $type, d.upload_time = datetime()
        """
        self.execute_query(query, {"id": document_id, "name": name, "type": doc_type})
        logger.info(f"创建文档节点: {document_id}")

    def create_section_node(self, section: dict[str, Any], document_id: str) -> None:
        query = """
        MERGE (s:Section {id: $id})
        SET s.title = $title, s.content = $content, s.page = $page
        WITH s
        MATCH (d:Document {id: $doc_id})
        MERGE (d)-[:CONTAINS]->(s)
        """
        self.execute_query(query, {
            "id": section.get("id", ""),
            "title": section.get("title", ""),
            "content": section.get("content", ""),
            "page": section.get("page", 0),
            "doc_id": document_id,
        })

    def create_table_node(self, table: dict[str, Any], document_id: str) -> None:
        query = """
        MERGE (t:Table {id: $id})
        SET t.content = $content, t.page = $page
        WITH t
        MATCH (d:Document {id: $doc_id})
        MERGE (d)-[:CONTAINS]->(t)
        """
        self.execute_query(query, {
            "id": table.get("id", ""),
            "content": table.get("content", ""),
            "page": table.get("page", 0),
            "doc_id": document_id,
        })

    def create_image_node(self, image: dict[str, Any], document_id: str) -> None:
        query = """
        MERGE (i:Image {id: $id})
        SET i.url = $url, i.description = $description, i.page = $page
        WITH i
        MATCH (d:Document {id: $doc_id})
        MERGE (d)-[:CONTAINS]->(i)
        """
        self.execute_query(query, {
            "id": image.get("id", ""),
            "url": image.get("url", ""),
            "description": image.get("description", ""),
            "page": image.get("page", 0),
            "doc_id": document_id,
        })

    def create_entity_node(self, entity: dict[str, Any]) -> None:
        entity_type = entity.get("type", "Concept")
        safe_label = "".join(c for c in entity_type if c.isalnum() or c == "_")
        if not safe_label:
            safe_label = "Concept"
        query = f"""
        MERGE (e:{safe_label} {{id: $id}})
        SET e.name = $name, e.description = $description
        """
        self.execute_query(query, {
            "id": entity.get("id", ""),
            "name": entity.get("name", ""),
            "description": entity.get("description", ""),
        })

    def create_relation(self, relation: dict[str, Any]) -> None:
        rel_type = relation.get("type", "RELATED_TO")
        safe_rel = "".join(c for c in rel_type if c.isalnum() or c == "_")
        if not safe_rel:
            safe_rel = "RELATED_TO"
        query = f"""
        MATCH (a {{id: $source}})
        MATCH (b {{id: $target}})
        MERGE (a)-[:{safe_rel}]->(b)
        """
        self.execute_query(query, {
            "source": relation.get("source", ""),
            "target": relation.get("target", ""),
        })

    def link_entity_to_section(self, entity_id: str, section_id: str, rel_type: str = "REFERENCES") -> None:
        safe_rel = "".join(c for c in rel_type if c.isalnum() or c == "_") or "REFERENCES"
        query = f"""
        MATCH (e {{id: $entity_id}})
        MATCH (s:Section {{id: $section_id}})
        MERGE (s)-[:{safe_rel}]->(e)
        """
        self.execute_query(query, {"entity_id": entity_id, "section_id": section_id})

    def link_document_to_folder(self, document_id: str, folder_id: str) -> None:
        query = """
        MATCH (d:Document {id: $doc_id})
        MERGE (f:Folder {id: $folder_id})
        MERGE (d)-[:BELONGS_TO]->(f)
        """
        self.execute_query(query, {"doc_id": document_id, "folder_id": folder_id})

    def search_entities(
        self,
        document_ids: list[str],
        keywords: list[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        if not document_ids or not keywords:
            return []
        query = """
        MATCH (d:Document)-[:CONTAINS]->(s:Section)-[:REFERENCES]->(e)
        WHERE d.id IN $doc_ids
          AND ANY(kw IN $keywords WHERE e.name CONTAINS kw OR e.description CONTAINS kw)
        RETURN DISTINCT e.id AS id, labels(e) AS type, e.name AS name, e.description AS description
        LIMIT $limit
        """
        return self.execute_query(query, {"doc_ids": document_ids, "keywords": keywords, "limit": limit})

    def get_document_graph(self, document_id: str) -> dict[str, Any]:
        query = """
        MATCH (d:Document {id: $doc_id})-[r]->(n)
        RETURN d.id AS source, type(r) AS relation, n.id AS target, labels(n) AS target_type, n.name AS target_name
        """
        results = self.execute_query(query, {"doc_id": document_id})
        return {"nodes": results}

    def delete_document_graph(self, document_id: str) -> None:
        query = """
        MATCH (d:Document {id: $doc_id})
        DETACH DELETE d
        """
        self.execute_query(query, {"doc_id": document_id})
        logger.info(f"删除文档图谱: {document_id}")

    def store_extraction_results(
        self,
        parse_result_dict: dict[str, Any],
        extraction_result_dict: dict[str, Any],
        document_id: str,
    ) -> None:
        for section in parse_result_dict.get("sections", []):
            self.create_section_node(section, document_id)

        for table in parse_result_dict.get("tables", []):
            self.create_table_node(table, document_id)

        for image in parse_result_dict.get("images", []):
            self.create_image_node(image, document_id)

        for entity in extraction_result_dict.get("entities", []):
            self.create_entity_node(entity)
            if entity.get("section_id"):
                self.link_entity_to_section(entity["id"], entity["section_id"])

        for relation in extraction_result_dict.get("relations", []):
            self.create_relation(relation)

        logger.info(f"知识图谱存储完成: 文档 {document_id}")


neo4j_client = Neo4jClient()
