# ChromaDB Integration with Gemini Embedding 2

ChromaDB has a native embedding function for Gemini models, which means ChromaDB handles the embedding calls automatically — you just pass raw text/content and it embeds for you.

## Table of Contents

1. [Setup](#setup)
2. [Using the Native Embedding Function](#using-the-native-embedding-function)
3. [Controlling Dimensions](#controlling-dimensions)
4. [Manual Embedding for Multimodal](#manual-embedding-for-multimodal)
5. [TypeScript Examples](#typescript-examples)

## Setup

```bash
# Python
pip install google-genai chromadb

# TypeScript
npm install @google/genai @chroma-core/google-gemini chromadb
```

## Using the Native Embedding Function

ChromaDB's `GoogleGeminiEmbeddingFunction` handles embedding automatically when you add or query documents:

```python
import chromadb
import chromadb.utils.embedding_functions as embedding_functions

google_ef = embedding_functions.GoogleGeminiEmbeddingFunction(
    model_name="gemini-embedding-2-preview",
    task_type="RETRIEVAL_DOCUMENT",
)

client = chromadb.Client()

# Create collection with the Gemini embedding function
collection = client.create_collection(
    name="my_collection",
    embedding_function=google_ef,
)

# Add documents — ChromaDB calls Gemini automatically
collection.add(
    documents=[
        "Gemini Embedding 2 supports multimodal inputs.",
        "ChromaDB is an open-source vector database.",
        "RAG systems improve LLM responses with retrieved context.",
    ],
    ids=["doc1", "doc2", "doc3"],
)

# Query — also uses Gemini automatically
results = collection.query(
    query_texts=["What databases support Gemini?"],
    n_results=2,
)

print(results["documents"])
```

To retrieve an existing collection with the same embedding function:

```python
collection = client.get_collection(
    name="my_collection",
    embedding_function=google_ef,
)
```

## Controlling Dimensions

```python
google_ef = embedding_functions.GoogleGeminiEmbeddingFunction(
    model_name="gemini-embedding-2-preview",
    task_type="RETRIEVAL_DOCUMENT",
    dimension=768,
)
```

## Manual Embedding for Multimodal

ChromaDB's native embedding function only handles text automatically. For images, audio, video, and PDFs, generate the embedding manually with the Gemini SDK and pass the vector to ChromaDB:

```python
import chromadb
from google import genai
from google.genai import types

gemini = genai.Client()
client = chromadb.Client()

collection = client.create_collection(name="multimodal_collection")

# Embed an image manually
with open("photo.jpg", "rb") as f:
    image_bytes = f.read()

result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
    ],
)

# Add to ChromaDB with pre-computed embedding
collection.add(
    embeddings=[result.embeddings[0].values],
    metadatas=[{"type": "image", "file": "photo.jpg"}],
    ids=["img1"],
)

# Text query against multimodal collection
query_result = gemini.models.embed_content(
    model="gemini-embedding-2-preview",
    contents="a beautiful landscape",
    config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
)

results = collection.query(
    query_embeddings=[query_result.embeddings[0].values],
    n_results=5,
)
```

## TypeScript Examples

### Native embedding function

```typescript
import { ChromaClient } from "chromadb";
import { GoogleGeminiEmbeddingFunction } from "@chroma-core/google-gemini";

const embedder = new GoogleGeminiEmbeddingFunction({
    apiKey: process.env.GEMINI_API_KEY,
    modelName: "gemini-embedding-2-preview",
});

const client = new ChromaClient();

const collection = await client.createCollection({
    name: "my_collection",
    embeddingFunction: embedder,
});

await collection.add({
    documents: [
        "Gemini Embedding 2 supports multimodal inputs.",
        "ChromaDB is an open-source vector database.",
    ],
    ids: ["doc1", "doc2"],
});

const results = await collection.query({
    queryTexts: ["What supports multimodal?"],
    nResults: 2,
});

console.log(results.documents);
```

### Manual multimodal embedding (TypeScript)

```typescript
import { GoogleGenAI } from "@google/genai";
import { ChromaClient } from "chromadb";
import * as fs from "node:fs";

const gemini = new GoogleGenAI({});
const client = new ChromaClient();

const collection = await client.createCollection({ name: "multimodal" });

// Embed an image
const imgBase64 = fs.readFileSync("photo.png", { encoding: "base64" });

const result = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: [{
        inlineData: { mimeType: "image/png", data: imgBase64 },
    }],
});

await collection.add({
    embeddings: [result.embeddings[0].values],
    metadatas: [{ type: "image", file: "photo.png" }],
    ids: ["img1"],
});

// Query with text
const queryResult = await gemini.models.embedContent({
    model: "gemini-embedding-2-preview",
    contents: "a landscape photo",
    config: { taskType: "RETRIEVAL_QUERY" },
});

const searchResults = await collection.query({
    queryEmbeddings: [queryResult.embeddings[0].values],
    nResults: 5,
});

console.log(searchResults.documents);
```
