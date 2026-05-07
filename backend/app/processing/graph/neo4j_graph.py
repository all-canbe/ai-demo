from neo4j import GraphDatabase, Session, Result
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Neo4jGraphBuilder:
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self):
        """连接Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self.driver.verify_connectivity()
            logger.info(f"成功连接Neo4j数据库: {self.uri}")
        except Exception as e:
            logger.error(f"连接Neo4j失败: {str(e)}")
            raise

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("已关闭Neo4j连接")

    def create_node(self, label: str, properties: Dict[str, Any]) -> str:
        """创建节点"""
        try:
            query = f"CREATE (n:{label} {self._dict_to_cypher(properties)}) RETURN id(n) as node_id"
            result = self._run_query(query)
            node_id = result.single()["node_id"]
            logger.info(f"创建节点成功，ID: {node_id}, 标签: {label}")
            return str(node_id)
        except Exception as e:
            logger.error(f"创建节点失败: {str(e)}")
            raise

    def create_relationship(self, source_id: str, target_id: str, rel_type: str, properties: Dict = None):
        """创建关系"""
        try:
            props = self._dict_to_cypher(properties) if properties else ""
            query = f"""
                MATCH (a), (b)
                WHERE id(a) = {source_id} AND id(b) = {target_id}
                CREATE (a)-[r:{rel_type}{props}]->(b)
                RETURN type(r) as rel_type
            """
            self._run_query(query)
            logger.info(f"创建关系成功: {source_id} -[{rel_type}]-> {target_id}")
        except Exception as e:
            logger.error(f"创建关系失败: {str(e)}")
            raise

    def upsert_entity(self, entity_type: str, unique_key: str, properties: Dict[str, Any]) -> str:
        """更新或插入实体"""
        try:
            query = f"""
                MERGE (n:{entity_type} {{{unique_key}: $unique_value}})
                SET n += $properties
                RETURN id(n) as node_id
            """
            result = self._run_query(query, {
                "unique_value": properties[unique_key],
                "properties": properties
            })
            node_id = result.single()["node_id"]
            return str(node_id)
        except Exception as e:
            logger.error(f"更新/插入实体失败: {str(e)}")
            raise

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取实体（简化实现，实际应用中可使用LLM增强）"""
        entities = []
        
        keywords = ["公司", "产品", "技术", "系统", "项目", "负责人"]
        
        for keyword in keywords:
            if keyword in text:
                entities.append({
                    "type": "Concept",
                    "name": keyword,
                    "context": text[:100]
                })
        
        return entities

    def build_knowledge_graph(self, document_id: str, content: str, metadata: Dict = None):
        """构建知识图谱"""
        try:
            doc_node_id = self.upsert_entity(
                "Document",
                "document_id",
                {"document_id": document_id, "content": content[:5000], **(metadata or {})}
            )

            entities = self.extract_entities(content)
            
            for entity in entities:
                entity_node_id = self.upsert_entity(
                    entity["type"],
                    "name",
                    {"name": entity["name"], "context": entity.get("context", "")}
                )
                self.create_relationship(doc_node_id, entity_node_id, "MENTIONS")

            logger.info(f"知识图谱构建完成，文档ID: {document_id}，实体数: {len(entities)}")
            return {"document_node_id": doc_node_id, "entities_count": len(entities)}
        except Exception as e:
            logger.error(f"构建知识图谱失败: {str(e)}")
            raise

    def query_graph(self, query: str) -> List[Dict[str, Any]]:
        """执行Cypher查询"""
        try:
            result = self._run_query(query)
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"查询失败: {str(e)}")
            raise

    def get_entity_relations(self, entity_name: str) -> List[Dict[str, Any]]:
        """获取实体的关系"""
        try:
            query = f"""
                MATCH (n)-[r]->(m)
                WHERE n.name = $entity_name OR m.name = $entity_name
                RETURN labels(n)[0] as source_label, n.name as source_name,
                       type(r) as relation_type,
                       labels(m)[0] as target_label, m.name as target_name
            """
            result = self._run_query(query, {"entity_name": entity_name})
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"获取实体关系失败: {str(e)}")
            raise

    def get_graph_stats(self) -> Dict[str, int]:
        """获取图谱统计信息"""
        try:
            node_count = self._run_query("MATCH (n) RETURN count(n) as count").single()["count"]
            rel_count = self._run_query("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            label_counts = {}
            result = self._run_query("MATCH (n) RETURN labels(n)[0] as label, count(n) as count")
            for record in result:
                label = record["label"]
                if label:
                    label_counts[label] = record["count"]

            return {
                "total_nodes": node_count,
                "total_relations": rel_count,
                "labels": label_counts
            }
        except Exception as e:
            logger.error(f"获取图谱统计失败: {str(e)}")
            raise

    def clear_graph(self):
        """清空图谱"""
        try:
            self._run_query("MATCH (n) DETACH DELETE n")
            logger.info("图谱已清空")
        except Exception as e:
            logger.error(f"清空图谱失败: {str(e)}")
            raise

    def _run_query(self, query: str, parameters: Dict = None) -> Result:
        """内部查询执行方法"""
        with self.driver.session() as session:
            return session.run(query, parameters or {})

    def _dict_to_cypher(self, properties: Dict) -> str:
        """将字典转换为Cypher属性字符串"""
        if not properties:
            return ""
        
        props = []
        for key, value in properties.items():
            if isinstance(value, str):
                props.append(f'{key}: "{value}"')
            else:
                props.append(f"{key}: {value}")
        
        return "{" + ", ".join(props) + "}"
