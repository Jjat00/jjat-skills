# Qdrant Integration with Gemini Embedding 2

Complete guide for using Gemini Embedding 2 with Qdrant vector database.

## Table of Contents

1. [Setup](#setup)
2. [Create Collection](#create-collection)
3. [Index Text Documents](#index-text-documents)
4. [Index Multimodal Content](#index-multimodal-content)
5. [Search](#search)
6. [Cross-Modal Search](#cross-modal-search)
7. [TypeScript Examples](#typescript-examples)

## Setup

```bash
# Python
pip install google-genai qdrant-client

# TypeScript
npm install @google/genai @qdrant/js-client-rest
```

```python
from google.genai import Client, types
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

gemini = Client()  # Reads GEMINI_API_KEY from env
qdrant = QdrantClient(url="http://localhost:6333")
```

## Create Collection

Match the vector `size` to your chosen `output_dimensionality` (default: 3072).

```python
COLLECTION = "documents"
DIMENSIONS = 3072  # or 768, 1536

qdrant.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(
        size=DIMENSIONS,
        distance=Distance.COSINE,
    ),
)
```

For reduced dimensions:

```python
DIMENSIONS = 768

qdrant.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(
        size=DIMENSIONS,
        distance=Distance.COSINE,
    ),
)
```

## Index Text Documents

```python
texts = [
    "Qdrant is a vector database optimized for similarity search.",
    "Gemini Embedding 2 supports multimodal inputs.",
    "RAG systems combine retrieval with generation for better answers.",
]

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=texts,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)

points = [
    PointStruct(
        id=idx,
        vector=embedding.values,
        payload={"text": text, "source": "manual"},
    )
    for idx, (embedding, text) in enumerate(zip(result.embeddings, texts))
]

qdrant.upsert(COLLECTION, points)
```

### Batching large document sets

For large corpora, batch in groups to stay within API limits:

```python
import itertools

def batch(iterable, size):
    it = iter(iterable)
    while chunk := list(itertools.islice(it, size)):
        yield chunk

all_texts = [...]  # Your full document list
point_id = 0

for text_batch in batch(all_texts, 100):
    result = gemini.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=text_batch,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )

    points = [
        PointStruct(
            id=point_id + idx,
            vector=emb.values,
            payload={"text": text},
        )
        for idx, (emb, text) in enumerate(zip(result.embeddings, text_batch))
    ]

    qdrant.upsert(COLLECTION, points)
    point_id += len(text_batch)
```

## Index Multimodal Content

### Images

```python
import uuid

with open("photo.jpg", "rb") as f:
    image_bytes = f.read()

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
    ],
)

qdrant.upsert(COLLECTION, [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=result.embeddings[0].values,
        payload={"type": "image", "file": "photo.jpg"},
    )
])
```

### PDFs

```python
with open("report.pdf", "rb") as f:
    pdf_bytes = f.read()

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
    ],
)

qdrant.upsert(COLLECTION, [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=result.embeddings[0].values,
        payload={"type": "pdf", "file": "report.pdf"},
    )
])
```

### Audio

```python
with open("recording.mp3", "rb") as f:
    audio_bytes = f.read()

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/mpeg"),
    ],
)

qdrant.upsert(COLLECTION, [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=result.embeddings[0].values,
        payload={"type": "audio", "file": "recording.mp3"},
    )
])
```

### Aggregated (text + image as one embedding)

```python
with open("product.jpg", "rb") as f:
    img_bytes = f.read()

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Content(
            parts=[
                types.Part(text="Red vintage sports car"),
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
            ]
        )
    ],
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)

# One embedding representing both text + image
qdrant.upsert(COLLECTION, [
    PointStruct(
        id=str(uuid.uuid4()),
        vector=result.embeddings[0].values,
        payload={"type": "product", "description": "Red vintage sports car", "image": "product.jpg"},
    )
])
```

## Search

### Text query

```python
query_result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="How does vector search work?",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

hits = qdrant.query_points(
    collection_name=COLLECTION,
    query=query_result.embeddings[0].values,
    limit=5,
)

for hit in hits.points:
    print(f"Score: {hit.score:.4f} | {hit.payload}")
```

### With metadata filtering

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

hits = qdrant.query_points(
    collection_name=COLLECTION,
    query=query_result.embeddings[0].values,
    query_filter=Filter(
        must=[FieldCondition(key="type", match=MatchValue(value="pdf"))]
    ),
    limit=5,
)
```

## Cross-Modal Search

Search images using a text query (or vice versa) — this works because all modalities share the same embedding space:

```python
# Text query to find relevant images
text_query = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="sunset over the ocean",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

image_results = qdrant.query_points(
    collection_name=COLLECTION,
    query=text_query.embeddings[0].values,
    query_filter=Filter(
        must=[FieldCondition(key="type", match=MatchValue(value="image"))]
    ),
    limit=5,
)
```

```python
# Image query to find relevant text documents
with open("query_image.jpg", "rb") as f:
    query_img = f.read()

img_query = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[types.Part.from_bytes(data=query_img, mime_type="image/jpeg")],
)

text_results = qdrant.query_points(
    collection_name=COLLECTION,
    query=img_query.embeddings[0].values,
    query_filter=Filter(
        must=[FieldCondition(key="type", match=MatchValue(value="text"))]
    ),
    limit=5,
)
```

## TypeScript Examples

### Full workflow

```typescript
import { GoogleGenAI } from "@google/genai";
import { QdrantClient } from "@qdrant/js-client-rest";

const gemini = new GoogleGenAI({});
const qdrant = new QdrantClient({ url: "http://localhost:6333" });

const COLLECTION = "documents";

// Create collection
await qdrant.createCollection(COLLECTION, {
    vectors: { size: 3072, distance: "Cosine" },
});

// Index documents
const texts = [
    "Qdrant is a vector database.",
    "Gemini Embedding 2 is multimodal.",
];

const embedResult = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: texts,
    config: { taskType: "RETRIEVAL_DOCUMENT" },
});

const points = texts.map((text, idx) => ({
    id: idx,
    vector: embedResult.embeddings[idx].values,
    payload: { text },
}));

await qdrant.upsert(COLLECTION, { points });

// Search
const queryResult = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: "What is Qdrant?",
    config: { taskType: "RETRIEVAL_QUERY" },
});

const searchResult = await qdrant.query(COLLECTION, {
    query: queryResult.embeddings[0].values,
    limit: 5,
});

console.log(searchResult);
```

### Embedding an image (TypeScript)

```typescript
import * as fs from "node:fs";

const imgBase64 = fs.readFileSync("photo.png", { encoding: "base64" });

const result = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: [{
        inlineData: { mimeType: "image/png", data: imgBase64 },
    }],
});

await qdrant.upsert(COLLECTION, {
    points: [{
        id: crypto.randomUUID(),
        vector: result.embeddings[0].values,
        payload: { type: "image", file: "photo.png" },
    }],
});
```

### Embedding a PDF (TypeScript)

```typescript
const pdfBase64 = fs.readFileSync("document.pdf", { encoding: "base64" });

const result = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: [{
        inlineData: { mimeType: "application/pdf", data: pdfBase64 },
    }],
});

await qdrant.upsert(COLLECTION, {
    points: [{
        id: crypto.randomUUID(),
        vector: result.embeddings[0].values,
        payload: { type: "pdf", file: "document.pdf" },
    }],
});
```
