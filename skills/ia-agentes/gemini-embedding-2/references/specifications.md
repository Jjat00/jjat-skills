# Gemini Embedding 2 — Technical Specifications

## Model Comparison

| Property | gemini-embedding-2-preview | gemini-embedding-001 |
|---|---|---|
| Input types | Text, Images, Audio, Video, PDF | Text only |
| Max input tokens | 8,192 | 2,048 |
| Default dimensions | 3,072 | 3,072 |
| Dimension range | 128 – 3,072 (MRL) | 128 – 3,072 (MRL) |
| Release stage | Public Preview | Stable |
| Knowledge cutoff | November 2025 | June 2025 |
| Region | us-central1 | Multiple |

## Input Limits by Modality

### Text
- Max tokens: 8,192
- Supports 100+ languages

### Images
- Max per request: 6
- Max file size: No limit (inline or GCS)
- Supported MIME types: `image/png`, `image/jpeg`

### Audio
- Max duration: 80 seconds
- Max files per request: 1
- Supported MIME types: `audio/mp3`, `audio/wav`

### Video
- Max duration with audio: 80 seconds
- Max duration without audio: 120 seconds
- Max videos per request: 1
- Supported MIME types: `video/mpeg`, `video/mp4`
- Supported codecs: H264, H265, AV1, VP9
- Audio tracks are extracted and interleaved with video frames

### PDF Documents
- Max files per request: 1
- Max pages per file: 6
- Supported MIME type: `application/pdf`
- Includes OCR processing

## Embedding Output

- Default: 3,072 dimensions (float32)
- Configurable via `output_dimensionality` parameter
- Recommended sizes: 768, 1536, 3072
- Full 3,072 output is pre-normalized (L2 norm = 1)
- Smaller dimensions require manual normalization

## Quality by Dimension (MTEB Benchmark)

| Dimensions | MTEB Score |
|---|---|
| 2048 | 68.16 |
| 1536 | 68.17 |
| 768 | 67.99 |
| 512 | 67.55 |
| 256 | 66.19 |
| 128 | 63.31 |

## API Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent
```

Batch endpoint:

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:batchEmbedContents
```

## Pricing

- Available under Standard PayGo
- Batch API available at 50% of default price
- Not compatible with: Provisioned Throughput, Flex PayGo, Priority PayGo, Batch Prediction

## Task Types Reference

| Task Type | Description |
|---|---|
| `RETRIEVAL_DOCUMENT` | Optimize for document indexing |
| `RETRIEVAL_QUERY` | Optimize for search queries |
| `SEMANTIC_SIMILARITY` | Optimize for text comparison |
| `CLASSIFICATION` | Optimize for label classification |
| `CLUSTERING` | Optimize for grouping similar items |
| `CODE_RETRIEVAL_QUERY` | Optimize for natural language → code search |
| `QUESTION_ANSWERING` | Optimize for Q&A retrieval |
| `FACT_VERIFICATION` | Optimize for claim verification retrieval |

## REST API Examples

### Single text embedding

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
        "model": "models/gemini-embedding-2-preview",
        "content": {
            "parts": [{"text": "What is the meaning of life?"}]
        }
    }'
```

### With task type and reduced dimensions

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
        "content": {
            "parts": [{"text": "Document text here"}]
        },
        "taskType": "RETRIEVAL_DOCUMENT",
        "output_dimensionality": 768
    }'
```

### Image embedding via REST

```bash
IMG_BASE64=$(base64 -w0 "photo.png")

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:embedContent" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
        "content": {
            "parts": [{
                "inline_data": {
                    "mime_type": "image/png",
                    "data": "'"${IMG_BASE64}"'"
                }
            }]
        }
    }'
```

### Batch embeddings

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2-preview:batchEmbedContents" \
    -H "Content-Type: application/json" \
    -H "x-goog-api-key: ${GEMINI_API_KEY}" \
    -d '{
        "requests": [
            {
                "model": "models/gemini-embedding-2-preview",
                "content": {"parts": [{"text": "First document"}]}
            },
            {
                "model": "models/gemini-embedding-2-preview",
                "content": {"parts": [{"text": "Second document"}]}
            }
        ]
    }'
```
