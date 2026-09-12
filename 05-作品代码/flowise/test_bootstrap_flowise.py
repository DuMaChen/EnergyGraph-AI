import json
import unittest

from bootstrap_flowise import transform_flow


class FlowBootstrapTests(unittest.TestCase):
    def test_template_is_rewired_without_secret_material(self):
        template = {
            "nodes": [
                {"id": "chatMistralAI_0", "data": {"id": "chatMistralAI_0", "name": "chatMistralAI", "type": "ChatMistralAI", "inputs": {}}},
                {"id": "openAIEmbeddings_0", "data": {"id": "openAIEmbeddings_0", "name": "openAIEmbeddings", "type": "OpenAIEmbeddings", "inputs": {}}},
                {"id": "faiss_0", "data": {"id": "faiss_0", "name": "faiss", "type": "Faiss", "inputs": {}}},
                {"id": "conversationalRetrievalQAChain_0", "data": {"id": "conversationalRetrievalQAChain_0", "name": "conversationalRetrievalQAChain", "type": "ConversationalRetrievalQAChain", "inputs": {}}},
                {"id": "textFile_0", "data": {"id": "textFile_0", "name": "textFile", "type": "Document", "inputs": {}}},
            ],
            "edges": [
                {"source": "faiss_0", "target": "conversationalRetrievalQAChain_0"},
                {"source": "textFile_0", "target": "faiss_0"},
            ],
        }
        graph = transform_flow(
            template,
            "storage-course-qa",
            llm_base_path="http://model-gateway:8080/v1",
            llm_model="mock-model",
            embedding_base_path="http://model-gateway:8080/v1",
            embedding_model="mock-embedding",
            qdrant_url="http://qdrant:6333",
            qdrant_collection="storage-course-v1",
            qdrant_dimension=64,
            openai_credential_id="openai-credential-id",
            qdrant_credential_id="qdrant-credential-id",
        )
        self.assertEqual({node["id"] for node in graph["nodes"]}, {"chatOpenAI_0", "openAIEmbeddings_0", "qdrant_0", "conversationalRetrievalQAChain_0"})
        self.assertEqual(len(graph["edges"]), 1)
        serialized = json.dumps(graph, ensure_ascii=False)
        self.assertNotIn("sk-", serialized)
        self.assertIn("contentPayloadKey", serialized)
        self.assertIn("metadataPayloadKey", serialized)


if __name__ == "__main__":
    unittest.main()
