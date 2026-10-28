AtlasDocs RAG System Design

AtlasDocs is an internal question-answering application for a fictional company called Northstar Labs. Employees use it to find information in engineering documents, onboarding guides, and incident reports. The system serves 2,000 employees and stores approximately 50,000 source documents.

The application has a web interface, an API service, an ingestion worker, a search service, and an answer-generation service. The API service authenticates users and coordinates requests. The ingestion worker prepares documents for retrieval. The search service retrieves relevant passages. The answer-generation service produces answers using those passages.

Authentication and Access

Employees sign in through the company's identity provider. After authentication, the API service obtains the employee's organization ID and permitted document groups. These values come from the authenticated session. They are not taken from the employee's question.

Every searchable chunk stores its organization ID and access groups. The search service applies access restrictions to both keyword search and vector search. Documents outside the employee's permissions must be excluded before their content is sent to the answer-generation service.

Document Ingestion

Source files are stored in object storage. When a file is uploaded or changed, an ingestion event is added to a queue. A worker reads the event, extracts the document's text, and records its source identifier and version.

AtlasDocs splits extracted text into chunks of approximately 400 tokens with an overlap of 60 tokens. Each chunk includes its section heading so that a passage remains understandable when retrieved independently. Tables are preserved as complete units when they fit within the configured size limit.

Each chunk receives a deterministic identifier based on its organization, source document, section, and content. Reprocessing unchanged content produces the same identifier. This allows the ingestion worker to recognize unchanged chunks and avoid generating their embeddings again.

Embedding and Storage

AtlasDocs uses an embedding model that produces vectors with 384 dimensions. The same model and preprocessing configuration are used for document chunks and search queries. Changing the embedding model requires a new version of the vector index.

Each search record contains the chunk text, its embedding, source document ID, document version, section heading, organization ID, and access groups. Product codes and error codes are stored in additional fields when those identifiers are available from reliable source metadata.

Hybrid Retrieval

AtlasDocs combines BM25 keyword retrieval with vector retrieval. Keyword retrieval helps find specific names, codes, and technical terms. Vector retrieval helps find passages that express a similar meaning using different words.

For each question, the keyword branch retrieves up to 20 candidates and the vector branch retrieves up to 20 candidates. Reciprocal Rank Fusion combines the two rankings using a rank constant of 60. Records appearing in both lists are deduplicated by chunk identifier.

A reranker evaluates the highest-ranked 20 combined candidates. The system selects up to five passages for answer generation. Selection also respects the model's input budget. A high retrieval score indicates ranking preference; it does not prove that a passage answers the question.

Answer Generation

The answer-generation service receives the question and the selected passages. Its instructions require answers to be supported by those passages. Each answer includes references to the source documents used.

When the retrieved passages do not contain enough evidence, AtlasDocs responds that it could not find sufficient information. When two current sources disagree, the response describes the disagreement and cites both sources instead of silently choosing one.

Updates and Deletions

When a source document changes, the ingestion worker prepares a new document generation. It writes new chunks and their embeddings before publishing that generation as active. Searches use the active-generation information to exclude unfinished updates.

After publication, obsolete chunks from the previous generation are removed asynchronously. Only one ingestion worker may publish a generation for a particular source document at a time. Failed ingestion jobs are retried up to three times before being moved to a dead-letter queue for inspection.

Caching

AtlasDocs caches query embeddings for 24 hours. The cache key includes the embedding-model version and the normalized query text.

AtlasDocs does not cache generated answers in its first release. This decision avoids serving answers built from outdated documents or permissions while the team validates its invalidation strategy.

Reliability and Performance

The target ingestion delay is less than five minutes after a source document changes. The target end-to-end response latency is below four seconds at the 95th percentile. These values are engineering targets and have not yet been demonstrated by a production benchmark.

If either retrieval branch fails, AtlasDocs returns a temporary search failure in its first release. It does not silently present results from an incomplete hybrid search. An answer-generation timeout also produces a retryable error.

Evaluation

The evaluation dataset contains 200 questions with expected supporting passages. It includes exact-code questions, paraphrased questions, ambiguous names, conflicting sources, and questions that cannot be answered from the available documents.

The team measures Recall@20 to determine whether the required evidence appears among the first 20 retrieved candidates. It separately measures answer support, citation correctness, access-control violations, response latency, and cost per request.

The initial deployment contains no image retrieval, voice interface, or automatic execution of actions. AtlasDocs retrieves information and generates supported answers. It cannot modify engineering systems or resolve incidents on an employee's behalf.