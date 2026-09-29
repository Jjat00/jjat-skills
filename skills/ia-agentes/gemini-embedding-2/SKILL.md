---
name: gemini-embedding-2
description: "Use this skill when generating embeddings with Google's Gemini Embedding 2 model (gemini-embedding-2-preview), building semantic search systems, creating multimodal embeddings (text, images, audio, video, PDF), integrating embeddings with vector databases like Qdrant or ChromaDB, or implementing RAG pipelines with Gemini embeddings. Trigger this skill whenever the user mentions Gemini embeddings, multimodal embeddings, semantic search with Google models, vector search with Gemini, embedding images/audio/video/PDFs, or cross-modal retrieval — even if they don't explicitly say 'embedding'."
---

# Gemini Embedding 2 — Multimodal Embeddings & Semantic Search

Gemini Embedding 2 (`gemini-embedding-2-preview`) is Google's first **multimodal embedding model**. Its key differentiator is that it accepts **5 types of input** — text, images, audio, video, and PDFs — and maps all of them into a **single unified vector space** of 3,072 dimensions. This enables cross-modal search, classification, and clustering across 100+ languages.

What this means in practice:
- A text query like "sunset over the ocean" can find matching **images** in your database
- An **audio** recording of a meeting can be matched to a **text** question about what was discussed
- A **PDF** document can be indexed and retrieved alongside **video** clips — all using the same embedding model and vector space
- No need for intermediate processing (no Whisper for audio, no OCR for PDFs) — the model handles raw bytes directly

## When to use which model

| Model | Input types | Max tokens | Use case |
|---|---|---|---|
| `gemini-embedding-2-preview` | Text, images, audio, video, PDF | 8,192 | Multimodal search, cross-modal retrieval |
| `gemini-embedding-001` | Text only | 2,048 | Text-only search, classification, clustering |

The embedding spaces between these models are **incompatible** — you cannot compare embeddings from one model with embeddings from the other. If migrating, re-embed all existing data.

<setup>

## Environment Setup

```bash
# Required
GEMINI_API_KEY=your_api_key_here
```

```bash
# Python
pip install google-genai

# TypeScript
npm install @google/genai
```

Initialize the client:

```python
from google import genai
from google.genai import types

client = genai.Client()  # Reads GEMINI_API_KEY from env
```

```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({});  // Reads GEMINI_API_KEY from env
```

</setup>

<text_embeddings>

## Text Embeddings

Single text:

```python
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="What is the meaning of life?"
)

print(len(result.embeddings[0].values))  # 3072
```

Multiple texts in one call:

```python
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        "What is the meaning of life?",
        "What is the purpose of existence?",
        "How do I bake a cake?"
    ]
)

for embedding in result.embeddings:
    print(len(embedding.values))  # 3072 each
```

```typescript
const response = await ai.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: [
        "What is the meaning of life?",
        "What is the purpose of existence?",
        "How do I bake a cake?"
    ],
});

console.log(response.embeddings);
```

</text_embeddings>

<multimodal_embeddings>

## Multimodal Embeddings

This is the core capability of `gemini-embedding-2-preview`. All modalities — text, images, audio, video, and PDFs — produce vectors in the **same semantic space**. An image embedding can be compared directly with a text embedding using cosine similarity, because both represent meaning in the same coordinate system.

```
Text  "a cat on a couch"  ──→  [0.12, -0.34, 0.56, ...]  ─┐
                                                             ├─ Same vector space → comparable via cosine similarity
Image  cat_photo.jpg       ──→  [0.11, -0.31, 0.58, ...]  ─┘
Audio  meeting.mp3         ──→  [0.45, 0.23, -0.12, ...]
Video  demo.mp4            ──→  [0.38, 0.19, -0.08, ...]
PDF    report.pdf           ──→  [0.67, -0.15, 0.42, ...]
```

The API pattern is the same for all modalities: read the file as bytes and pass it via `types.Part.from_bytes` with the correct MIME type. No preprocessing, no intermediate models.

### Image Embedding

```python
with open("photo.png", "rb") as f:
    image_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    ]
)
```

```typescript
import * as fs from "node:fs";

const imgBase64 = fs.readFileSync("photo.png", { encoding: "base64" });

const response = await ai.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: [{
        inlineData: { mimeType: "image/png", data: imgBase64 },
    }],
});
```

### Audio Embedding

```python
with open("audio.mp3", "rb") as f:
    audio_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=audio_bytes, mime_type="audio/mpeg"),
    ]
)
```

### Video Embedding

```python
with open("clip.mp4", "rb") as f:
    video_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=video_bytes, mime_type="video/mp4"),
    ]
)
```

For videos longer than 128 seconds, chunk into overlapping segments and embed individually.

### PDF Document Embedding

```python
with open("document.pdf", "rb") as f:
    pdf_bytes = f.read()

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
    ]
)
```

### Aggregated Multimodal Embedding

Combine multiple parts into a single `Content` entry to get **one unified embedding** that represents all of them together. This is useful for objects like a product listing with an image and a description:

```python
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Content(
            parts=[
                types.Part(text="A red vintage car in the rain"),
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ]
        )
    ]
)

# result.embeddings has ONE embedding for the combined input
```

In contrast, passing items as separate entries in `contents` produces **separate embeddings** — one per entry:

```python
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        "A red vintage car in the rain",
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
    ]
)

# result.embeddings has TWO embeddings (text and image separately)
```

</multimodal_embeddings>

<task_types>

## Task Types

Specifying a task type optimizes the embedding for the intended relationship. This matters — using the right task type improves retrieval accuracy significantly.

| Task type | Use for | Pair with |
|---|---|---|
| `RETRIEVAL_DOCUMENT` | Indexing documents, articles, web pages | `RETRIEVAL_QUERY` |
| `RETRIEVAL_QUERY` | Search queries | `RETRIEVAL_DOCUMENT` |
| `SEMANTIC_SIMILARITY` | Comparing text similarity | Same type on both sides |
| `CLASSIFICATION` | Sentiment analysis, spam detection | — |
| `CLUSTERING` | Document organization, anomaly detection | — |
| `CODE_RETRIEVAL_QUERY` | Natural language → code search | `RETRIEVAL_DOCUMENT` for code |
| `QUESTION_ANSWERING` | Q&A systems | `RETRIEVAL_DOCUMENT` for docs |
| `FACT_VERIFICATION` | Claim verification | `RETRIEVAL_DOCUMENT` for evidence |

The key pairing rule: for search/retrieval, always use `RETRIEVAL_QUERY` for the query side and `RETRIEVAL_DOCUMENT` for the corpus side. Mixing them up degrades results.

```python
# Indexing documents
doc_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=["Document text here..."],
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
)

# Querying
query_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="What is this document about?",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
)
```

```typescript
// Indexing documents
const docResult = await ai.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: ["Document text here..."],
    taskType: "RETRIEVAL_DOCUMENT",
});

// Querying
const queryResult = await ai.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: "What is this document about?",
    taskType: "RETRIEVAL_QUERY",
});
```

</task_types>

<dimensionality>

## Controlling Embedding Size

Both models are trained with Matryoshka Representation Learning (MRL), which means you can truncate embeddings to smaller dimensions without significant quality loss. This saves storage and speeds up similarity computation.

Recommended dimensions: **768**, **1536**, or **3072** (default).

```python
result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="Hello world",
    config=types.EmbedContentConfig(output_dimensionality=768)
)

print(len(result.embeddings[0].values))  # 768
```

```typescript
const response = await ai.models.embedContent({
    model: "gemini-embedding-2-preview",
    content: "Hello world",
    outputDimensionality: 768,
});
```

### Normalizing smaller dimensions

The default 3,072-dimension embedding is already normalized. For smaller dimensions, normalize manually to ensure accurate cosine similarity:

```python
import numpy as np

embedding_values = np.array(result.embeddings[0].values)
normed = embedding_values / np.linalg.norm(embedding_values)
```

### Quality vs size tradeoff

| Dimensions | MTEB Score | Storage per vector |
|---|---|---|
| 3072 | ~68.2 | 12 KB |
| 1536 | ~68.2 | 6 KB |
| 768 | ~68.0 | 3 KB |
| 256 | ~66.2 | 1 KB |

The sweet spot is often **768** — nearly the same quality at 1/4 the storage.

</dimensionality>

<vector_databases>

## Vector Database Integration

For detailed integration code with vector databases, read the appropriate reference file:

- **Qdrant**: `references/qdrant-integration.md` — Full workflow: create collection, index documents (text + multimodal), search. Python and TypeScript.
- **ChromaDB**: `references/chromadb-integration.md` — Native embedding function integration. Python and TypeScript.

### Quick start: Qdrant (most common pattern)

```python
from google.genai import Client, types
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

gemini = Client()
qdrant = QdrantClient(url="http://localhost:6333")

# 1. Create collection
qdrant.create_collection(
    collection_name="my_collection",
    vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
)

# 2. Embed and index documents
texts = ["First document", "Second document", "Third document"]
result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=texts,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)

points = [
    PointStruct(id=idx, vector=emb.values, payload={"text": text})
    for idx, (emb, text) in enumerate(zip(result.embeddings, texts))
]
qdrant.upsert("my_collection", points)

# 3. Search
query = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="What is the first document about?",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

results = qdrant.query_points(
    collection_name="my_collection",
    query=query.embeddings[0].values,
)
```

</vector_databases>

<similarity>

## Computing Similarity

Cosine similarity is the standard metric for comparing Gemini embeddings. Values range from -1 (opposite) to 1 (most similar).

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

texts = [
    "What is the meaning of life?",
    "What is the purpose of existence?",
    "How do I bake a cake?",
]

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=texts,
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)

vectors = [e.values for e in result.embeddings]
sim_matrix = cosine_similarity(vectors)

# texts[0] vs texts[1] → high similarity (same concept)
# texts[0] vs texts[2] → low similarity (different topics)
```

### Cross-modal similarity

Because all modalities share the same vector space, you can compute similarity between, say, a text query and an image:

```python
text_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="a cat sleeping on a couch"
)

image_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[types.Part.from_bytes(data=cat_image_bytes, mime_type="image/jpeg")]
)

similarity = cosine_similarity(
    [text_result.embeddings[0].values],
    [image_result.embeddings[0].values]
)[0][0]
```

</similarity>

<use_cases>

## Advanced Use Cases

### Prototype-based Classification (no ML model needed)

Embed labeled examples with `CLASSIFICATION` task type, average the embeddings per category to create prototype vectors, then classify new items by finding the nearest prototype:

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define labeled examples per category
categories = {
    "soporte_tecnico": [
        "Mi aplicación se cierra sola",
        "No puedo iniciar sesión desde ayer",
        "Error 500 al cargar el dashboard",
    ],
    "facturacion": [
        "Me cobraron dos veces este mes",
        "Necesito una factura con RFC diferente",
        "¿Cuándo se aplica el descuento?",
    ],
    "ventas": [
        "¿Tienen plan empresarial?",
        "Quiero una demo del producto",
        "¿Cuál es el precio para 50 usuarios?",
    ],
}

# Create prototype vector per category (average of its examples)
prototypes = {}
for category, examples in categories.items():
    result = client.models.embed_content(
        model="gemini-embedding-2-preview",
        contents=examples,
        config=types.EmbedContentConfig(task_type="CLASSIFICATION"),
    )
    vectors = [e.values for e in result.embeddings]
    prototypes[category] = np.mean(vectors, axis=0)

# Classify a new ticket
new_ticket = "La página de pagos no carga y necesito pagar hoy"
ticket_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=new_ticket,
    config=types.EmbedContentConfig(task_type="CLASSIFICATION"),
)

ticket_vector = ticket_result.embeddings[0].values
similarities = {
    cat: cosine_similarity([ticket_vector], [proto])[0][0]
    for cat, proto in prototypes.items()
}

predicted = max(similarities, key=similarities.get)
# → "soporte_tecnico" (correctly identifies it as a tech support issue)
```

### Unsupervised Clustering

Discover latent topics in your data without predefined labels:

```python
from sklearn.cluster import KMeans

comments = [
    "El sistema es muy lento últimamente",
    "Me encanta la nueva interfaz",
    "¿Cómo integro la API con mi sistema?",
    "El cobro no se refleja en mi estado de cuenta",
    # ... more comments
]

result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=comments,
    config=types.EmbedContentConfig(task_type="CLUSTERING"),
)

vectors = np.array([e.values for e in result.embeddings])
kmeans = KMeans(n_clusters=4, random_state=42).fit(vectors)

for i, (comment, label) in enumerate(zip(comments, kmeans.labels_)):
    print(f"Cluster {label}: {comment}")
```

### Cross-Modal Search with Weighted Scoring

For richer results, combine text-to-text and text-to-image similarity with weighted scoring:

```python
# Index items with BOTH text and image embeddings stored separately
text_embeddings = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=captions,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)

image_embeddings = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=img, mime_type="image/jpeg")
        for img in image_bytes_list
    ],
)

# Search with weighted combination
query_emb = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="a dog playing in the park",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

text_sims = cosine_similarity([query_emb.embeddings[0].values], text_vectors)[0]
image_sims = cosine_similarity([query_emb.embeddings[0].values], image_vectors)[0]

# Weighted: 60% text relevance + 40% visual relevance
combined_scores = 0.6 * text_sims + 0.4 * image_sims
top_indices = combined_scores.argsort()[::-1][:5]
```

### Basic RAG Pipeline

Combine embeddings with a generative model for grounded answers:

```python
# 1. Index your knowledge base
documents = [
    "Gemini Embedding 2 supports text, images, audio, video, and PDF.",
    "The model outputs 3072-dimension vectors by default.",
    "Task types optimize embeddings for specific use cases.",
]

doc_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=documents,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
)

# 2. Query and retrieve
query = "What input types does the embedding model support?"
query_result = client.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=query,
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

sims = cosine_similarity(
    [query_result.embeddings[0].values],
    [e.values for e in doc_result.embeddings]
)[0]
best_doc = documents[sims.argmax()]

# 3. Generate grounded answer
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"Based on this context: '{best_doc}'\n\nAnswer: {query}",
)
print(response.text)
```

</use_cases>

<best_practices>

## Best Practices for Production

1. **Always configure TaskType — never generate "generic" embeddings.** Use `RETRIEVAL_QUERY` for user queries and `RETRIEVAL_DOCUMENT` for your corpus. This optimizes the mathematical precision of the latent space for your specific use case. Omitting task types or using the wrong pair visibly degrades search quality.

2. **Leverage MRL to save costs at scale.** The model outputs 3,072 dimensions by default, but you can truncate to 1,536 or 768 with minimal quality loss. For massive databases, this means 2-4x savings in storage, memory, and query latency in your vector DB. Always normalize after truncation.

3. **Exploit interleaved multimodal input.** The killer feature is sending multiple modalities in a single request to create one enriched embedding. Combine a text description with an image, or a ticket text with a screenshot — this captures richer semantics than either modality alone. Ideal for product listings, support tickets with screenshots, or reports with charts.

4. **Skip intermediate models for audio and video.** Don't pipe audio through Whisper or other STT models before embedding. Gemini Embedding 2 processes audio and video natively, capturing semantic intent and tone directly into the vector. This is faster, cheaper, and preserves information that transcription loses.

5. **Batch your embed calls.** Pass multiple contents in a single `embed_content` call instead of one call per document. This reduces API latency and cost. For very large corpora, use the Batch API endpoint at 50% of the default price.

6. **Chunk long texts** to stay within the 8,192 token limit. For documents longer than this, split into overlapping chunks (e.g., 500 tokens with 50-token overlap) and embed each chunk separately.

7. **Store the API key in `.env`**, never hardcode it. The SDK reads `GEMINI_API_KEY` from the environment automatically.

</best_practices>

<troubleshooting>

## Troubleshooting

**Embedding dimensions don't match collection size** → Make sure `output_dimensionality` in the embed call matches the `size` in your vector DB collection config. Mismatches cause upsert errors.

**Low search quality** → Check that you're using `RETRIEVAL_DOCUMENT` for indexing and `RETRIEVAL_QUERY` for searching. Using the same task type for both reduces retrieval accuracy.

**"Model not found" error** → The model ID is `gemini-embedding-2-preview` (not `gemini-2-embedding` or other variations). Verify the region supports it — currently only `us-central1`.

**Cosine similarity always near 1** → Your embeddings may not be normalized. Apply L2 normalization when using dimensions smaller than 3,072.

**Video embedding fails** → Check duration limits: 128 seconds max (80 seconds if audio track included). For longer videos, chunk into overlapping segments.

**PDF embedding returns unexpected results** → Maximum 6 pages per PDF. For longer documents, split into chunks of 6 pages or less.

</troubleshooting>

<specifications>

## Technical Specifications

For complete technical limits and supported MIME types, read `references/specifications.md`.

Quick reference:

| Modality | Limit | Formats |
|---|---|---|
| Text | 8,192 tokens | — |
| Images | 6 per request | PNG, JPEG |
| Audio | 80 seconds | MP3, WAV |
| Video | 128s (no audio) / 80s (with audio) | MP4, MPEG |
| PDF | 1 file, 6 pages | application/pdf |

</specifications>
