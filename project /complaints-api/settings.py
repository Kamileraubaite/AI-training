"""
Azure settings read from the environment. 
"""
import os

AZURE_SEARCH_DOCUMENT = os.environ.get("AZURE_SEARCH_DOCUMENT", "")

AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "complaints-chunks-v1")

SEMANTIC_SEARCH_INDEX = "complaints_semantic"

RERANK_FLOOR = float(os.environ.get("RERANK_FLOOR", "2.0"))

