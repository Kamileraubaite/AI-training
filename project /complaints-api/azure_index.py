from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration, 
    HnswParameters,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch, 
    SimpleField,
    VectorSearch, 
    VectorSearchProfile
)

import settings

DIMENSIONS = 512 #voyage-3-lite produces 512 numbers per text
VECTOR_PROFILE = "complaints_vector_profile"
ALGORITHM = "complaints-hnsw"

def key_for(chunk_id: str) -> str:
    return chunk_id.replace("#", "_")

def index_definition(name: str) -> SearchIndex:
    fields = [
        SimpleField(name="chunk_key", type=SearchFieldDataType.String, key=True),
        SimpleField(name="chunk_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="doc_id", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SearchableField(name="text", type=SearchFieldDataType.String),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=DIMENSIONS,     
            vector_search_profile_name=VECTOR_PROFILE,
        ),
    ]
    
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name=ALGORITHM, parameters=HnswParameters(metric="cosine"))],
        profiles=[VectorSearchProfile(name=VECTOR_PROFILE, algorithm_configuration_name=ALGORITHM)]
    )

    semantic_search = SemanticSearch(configurations=[SemanticConfiguration(
        name=settings.SEMANTIC_CONFIG,
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="text")],
        )

    )])
    return SearchIndex(name=name, fields=fields, vector_search=vector_search, semantic_search=semantic_search)

