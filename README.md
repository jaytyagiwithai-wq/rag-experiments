# RAG experiments

A collection of Python scripts I put together while learning retrieval-augmented generation. They cover a basic RAG pipeline, hybrid search with BM25 and vectors, semantic chunking, and contextual compression.

The examples are small scripts so the retrieval steps are easy to follow. There is no API or frontend here.

## What's inside

```text
rag-experiments/
├── examples/
│   ├── basic_rag/
│   │   └── basic_rag_pipeline.py
│   ├── hybrid_search/
│   │   └── prod_hybrid_search.py
│   ├── contextual_compression/
│   │   └── advanced_rag_chunking.py
│   └── chunking/
│       └── semantic_chunking.py
├── data/
│   ├── BASE.md
│   ├── neurowave.md
│   └── atlasdocs.md
├── .env.example
├── pyproject.toml
└── uv.lock
```

All three sample documents describe fictional projects or products. The architecture described in `atlasdocs.md` is material for the retriever to search, not a list of features implemented by this repository.

## Setup

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jaytyagiwithai-wq/rag-experiments.git
cd rag-experiments
uv sync --locked
```

For the OpenAI and Chroma Cloud examples, copy `.env.example` to `.env` in the repository root and fill in the values:

```dotenv
OPENAI_API_KEY=your_openai_key
CHROMA_API_KEY=your_chroma_key
CHROMA_TENANT=your_chroma_tenant
CHROMA_DATABASE=your_chroma_database
```

Create a database in Chroma Cloud and use its tenant and database values. Use a separate database for these experiments. The cloud examples create collections called `rag_experiments_aurora` and `rag_experiments_atlas`.

| Example | OpenAI key | Chroma Cloud |
| --- | --- | --- |
| Basic RAG | Required | Required |
| Hybrid search | Not required | Not required |
| Semantic chunking | Required | Not required |
| Contextual compression | Required | Required |

The scripts load `.env` and sample files relative to their own location. The commands below are run from the repository root. OpenAI calls incur API usage charges; Chroma Cloud usage depends on your account. Chroma's default local embedding model may download on its first use.

## 1. Basic RAG

```bash
uv run examples/basic_rag/basic_rag_pipeline.py
```

This loads `BASE.md`, a fictional ocean-sensor project briefing. It splits the text into 500-character chunks with 50 characters of overlap, stores them in Chroma Cloud, retrieves three chunks, and passes their text to `gpt-4.1-mini`.

The example question asks why a monitoring system missed readings during a storm and how the issue was resolved. The prompt asks the model to use the retrieved context and say it doesn't know when the answer is missing.

## 2. Hybrid search

```bash
uv run examples/hybrid_search/prod_hybrid_search.py
```

This searches `neurowave.md`, a fictional networking-equipment support document, using two retrievers:

- BM25 for keywords and exact product identifiers.
- Chroma vector search for similar meaning.

Each retriever returns five candidates. `EnsembleRetriever` combines their rankings using weighted reciprocal rank fusion with equal weights. The tokenizer keeps identifiers such as `SKU-7742M` together.

The script asks about that product's warranty and prints previews of the combined results. It demonstrates retrieval only; there is no answer-generation step. Its Chroma collection is in memory and is rebuilt for each run.

## 3. Semantic chunking

```bash
uv run examples/chunking/semantic_chunking.py
```

This also uses `neurowave.md`. `SemanticChunker` uses OpenAI embeddings to find changes in meaning, with a percentile breakpoint threshold of 90. If semantic chunking fails, the script falls back to recursive splitting with 400-character chunks and 50 characters of overlap.

The chunks go into a local, in-memory Chroma collection. Three sample questions exercise product compatibility, shipping rules and troubleshooting. The script prints the top retrieved chunk for each question. Change the `strategy` argument in `build_knowledge_base()` to `"recursive"` to try the other splitting method directly.

The OpenAI embeddings here determine the semantic chunk boundaries. Chroma's default embedding function handles vector storage and retrieval; these are separate steps.

## 4. Contextual compression

```bash
uv run examples/contextual_compression/advanced_rag_chunking.py
```

This loads `atlasdocs.md`, uses semantic chunking with a recursive fallback, and stores the chunks in Chroma Cloud. For each question, it retrieves up to five chunks. `LLMChainExtractor` then uses `gpt-4.1-mini` to extract relevant portions before the final answer is generated.

The script prints the original context, compressed context, document and character counts, and the final answer. This makes it possible to inspect what the compression step kept or removed.

This example implements **contextual compression after retrieval**. It does not generate document-level context to prepend to chunks before indexing.

## Current limitations

- Questions are hardcoded near the bottom of the scripts. Edit them to try your own questions.
- These are learning examples, not a production service. There is no authentication, deployment setup, automated retrieval evaluation or measured accuracy claim.
- The basic example upserts numbered chunks on each run. If the document becomes shorter, old chunks can remain. Start with a fresh experiment collection after changing its source document.
- The compression example reuses its cloud collection whenever it is nonempty. Changing the source document requires rebuilding that experiment collection.
- The compression demonstration runs extraction once to display the comparison and again inside the answer chain. This means extra model calls.
- The answer scripts print plain text, without source citations. Asking a model to stay within the context does not guarantee a correct answer.
- Some setup happens at module level. Run these as scripts; importing them can initialize clients or trigger indexing.

Credentials belong in `.env`, which is ignored by Git. Only fictional sample data is included.
