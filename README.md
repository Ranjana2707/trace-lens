# TraceLens — AI-Assisted Software Incident Investigation & Root-Cause Assistant

An AI-powered system to help developers investigate software failures by analyzing logs, stack traces, code changes, and documentation using retrieval-augmented generation (RAG) and semantic search.

---

## 🎯 Problem Statement

When a production incident occurs, developers face a critical challenge:

**Given multiple pieces of technical evidence from a software failure, identify the most likely root-cause hypotheses, show supporting evidence, and recommend next investigation steps.**

### The Manual Approach (Current State)
- Search through 10,000+ log lines manually
- Cross-reference stack traces with code changes
- Correlate timestamps across services
- Guess what to investigate first
- **Time cost:** 30 minutes to 2+ hours
- **Risk:** Incomplete or incorrect diagnosis

### Why a Naive LLM Isn't Enough
```
Developer: "Here's my 50,000-line log file"
ChatGPT:   "The error appears to be caused by X"
Developer: "Where in the logs did you find that?"
ChatGPT:   [Hallucinates or forgets context]
```

**Problems:**
- No source citations → cannot verify claims
- Context windows overflow → hallucination
- No ranking of evidence quality
- No evaluation framework
- Unclear what's a fact vs. speculation
- High API costs (entire log sent)

---

## 💡 Solution: TraceLens

**TraceLens** is an AI-assisted investigation system that:

1. **Parses** multiple evidence sources (logs, stack traces, code, Git diffs, docs)
2. **Chunks** evidence intelligently with metadata preservation
3. **Embeds** chunks using Sentence Transformers
4. **Retrieves** only relevant evidence via FAISS vector search
5. **Ranks** evidence by relevance and type
6. **Prompts** Gemini API with structured reasoning constraints
7. **Generates** structured investigation reports that distinguish:
   - **FACTS** (observed evidence)
   - **HYPOTHESES** (supported by evidence)
   - **RECOMMENDATIONS** (next investigation steps)
8. **Evaluates** against known root causes using measurable metrics

### Key Differences from a Chatbot

| Aspect | Naive Chatbot | TraceLens |
|--------|---|---|
| **Context** | Entire 50K lines | Top-20 relevant chunks (~8K tokens) |
| **Source Citations** | Hallucinated or missing | Chunk ID + line number for every claim |
| **Evidence Ranking** | None | Semantic relevance + type-based prioritization |
| **Fact vs. Hypothesis** | Blurred | Explicitly structured |
| **Confidence Calibration** | Fake percentages | Grounded in evidence count |
| **Evaluatable** | No | Yes, against known root causes |
| **Cost** | Scales with log size | Scales with retrieval results |
| **Uncertainty Handling** | Hallucinates | Explicitly identifies missing evidence |

---

## 🏗️ Architecture

```
INCIDENT INPUT
├─ Application Logs
├─ Stack Trace
├─ Source Code Files
├─ Git Diff / Commit
├─ Technical Docs
└─ (Optional: Known Root Cause for evaluation)
       ↓
┌──────────────────────────────────────────────┐
│      EVIDENCE PARSING LAYER                   │
├──────────────────────────────────────────────┤
│ Extract: timestamps, exceptions, files,      │
│ line numbers, changed methods, services      │
│ Result: Structured evidence objects          │
└──────────────────────────────────────────��───┘
       ↓
┌──────────────────────────────────────────────┐
│      CHUNKING & METADATA LAYER                │
├──────────────────────────────────────────────┤
│ Chunk logs: sliding window                    │
│ Chunk code: by function/method                │
│ Chunk diffs: by changed section               │
│ Preserve: source, file, line, timestamp       │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│      EMBEDDINGS & INDEXING LAYER              │
├──────────────────────────────────────────────┤
│ Model: sentence-transformers/all-MiniLM-L6   │
│ (384-dimensional vectors)                     │
│ Index: FAISS (flat, L2 distance)              │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│      SEMANTIC RETRIEVAL LAYER                 │
├──────────────────────────────────────────────┤
│ Query embedding → FAISS search → top-K       │
│ Filter by type, metadata                      │
│ Output: [chunk, similarity, metadata, ref]   │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│      LLM REASONING LAYER                      │
├──────────────────────────────────────────────┤
│ Model: Gemini API                             │
│ Input: Retrieved evidence + reasoning rules   │
│ Output: Structured investigation report      │
│ - Summary & affected component               │
│ - Root-cause hypotheses (with evidence)      │
│ - Investigation recommendations              │
│ - Source references & limitations            │
└──────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────┐
│      EVALUATION LAYER                         │
├──────────────────────────────────────────────┤
│ Ground truth: Known root causes               │
│ Metrics:                                       │
│ - Retrieval Recall@K                         │
│ - Root-cause hypothesis match                │
│ - Evidence groundedness                      │
│ - Unsupported claims                         │
└──────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+** — Primary language
- **Sentence Transformers** — Semantic embeddings (384-dim vectors)
- **FAISS** — Vector indexing & similarity search
- **Gemini API** — LLM reasoning
- **FastAPI** — REST API
- **Streamlit** — Web UI
- **PostgreSQL** (optional) — Persistent incident storage

### Supporting Libraries
- **LangChain** — LLM orchestration (after manual pipeline works)
- **NumPy** — Vector operations
- **Pandas** — Data manipulation
- **Pydantic** — Schema validation
- **python-dotenv** — Environment configuration

### Why These Choices?

| Technology | Why | Alternative | Why Not |
|---|---|---|---|
| Sentence Transformers | Fast, free, good semantic quality | Proprietary embeddings API | Cost, dependency, latency |
| FAISS | Efficient vector search, no server needed | Pinecone, Weaviate | Managed, but adds cost/complexity |
| Gemini API | Free tier, good reasoning, competitive | GPT-4, Claude | Cost, latency, API limits |
| FastAPI | Modern, async-ready, auto-docs | Flask, Django | Overkill or old-fashioned |
| Streamlit | Rapid prototyping, no frontend needed | React + backend | Time cost, not needed for MVP |

---

## 📊 Data Flow: Concrete Example

### Input: Payment Service NullPointerException

```
logs/payment-service.log (5000 lines)
stack-trace.txt
  - PaymentService.java:142 NullPointerException
code/PaymentService.java (200 lines)
git-diff (latest commit)
docs/payment-flow.md
```

### Output: Investigation Report

```json
{
  "incident_summary": "NullPointerException in PaymentService.processPayment() at line 142",
  "affected_component": "PaymentService / PaymentRepository integration",
  "root_cause_hypotheses": [
    {
      "hypothesis": "PaymentRepository.findById() is returning null for some transaction IDs",
      "confidence": "high",
      "confidence_rationale": "Stack trace shows NPE at line 142 where payment.process() is called. Code directly calls process() without null check.",
      "supporting_evidence": [
        "stack-trace.txt",
        "logs/payment-service.log (line 2845)"
      ],
      "contradictory_evidence": [],
      "missing_evidence": [
        "Database logs showing transaction lookup results",
        "PaymentRepository implementation"
      ]
    }
  ],
  "recommended_investigation_steps": [
    "1. Add null check before payment.process() to prevent NPE",
    "2. Query database logs for transaction lookup status",
    "3. Review PaymentRepository.findById() for null scenarios",
    "4. Verify recent code change didn't break null-handling"
  ],
  "relevant_files": [
    "PaymentService.java (lines 138-145)",
    "PaymentRepository.java"
  ],
  "limitations": "Evidence does not include PaymentRepository implementation or database query logs, limiting root-cause confirmation."
}
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Gemini API key (free from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Setup

```bash
# Clone repository
git clone https://github.com/Ranjana2707/trace-lens.git
cd trace-lens

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Run Tests
```bash
pytest tests/
```

### Run API
```bash
uvicorn app.api.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Run UI
```bash
streamlit run app/ui/app.py
# UI available at http://localhost:8501
```

---

## 📁 Project Structure

```
trace-lens/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Environment & configuration
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── loader.py             # Load incident packages
│   │
│   ├── parsing/
│   │   ├── __init__.py
│   │   ├── log_parser.py         # Extract errors, timestamps
│   │   ├── trace_parser.py       # Parse stack traces
│   │   ├── code_parser.py        # Extract code structures
│   │   ├── git_parser.py         # Parse Git diffs
│   │   └── evidence.py           # Evidence data class
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── chunker.py            # Split evidence into chunks
│   │   └── strategies.py         # Different chunking approaches
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── embedder.py           # Sentence Transformers wrapper
│   │   └── similarity.py         # Cosine similarity calculations
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── faiss_index.py        # FAISS index management
│   │   └── retriever.py          # Query & retrieve top-K
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── analyzer.py           # Main analysis orchestrator
│   │   ├── llm_client.py         # Gemini API wrapper
│   │   ├── prompts.py            # System prompts
│   │   └── schemas.py            # Output data structures
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── metrics.py            # Recall@K, groundedness, etc.
│   │   ├── evaluator.py          # Test harness
│   │   └── comparisons.py        # Configuration comparisons
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── routes.py             # /analyze, /health endpoints
│   │   └── models.py             # Request/response models
│   │
│   └── ui/
│       ├── __init__.py
│       └── app.py                # Streamlit interface
│
├── data/
│   ├── sample/                   # Synthetic incidents (generated Day 2)
│   │   ├── incident_001.json
│   │   ├── incident_002.json
│   │   └── ...
│   └── evaluation/               # Ground truth & metrics
│       ├── incidents_with_labels.json
│       └── evaluation_results.json
│
├── tests/
│   ├── __init__.py
│   ├── test_parsing.py
│   ├── test_chunking.py
│   ├── test_embeddings.py
│   ├── test_retrieval.py
│   └── test_analysis.py
│
├── evaluation/
│   ├── benchmark.py              # Run evaluation suite
│   └── comparison_configs.py     # Different configurations to test
│
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── main.py                       # Entry point
├── README.md                     # This file
├── ROADMAP.md                    # 7-day development plan
└── ARCHITECTURE.md               # Detailed technical design
```

---

## 📈 Development Roadmap

### Day 1: ✓ Project Setup
- [x] Virtual environment & structure
- [x] Configuration management
- [x] Git initialization

### Day 2: Synthetic Incident Dataset
- [ ] Create 20+ realistic incidents
- [ ] Define root causes & evidence
- [ ] Validate incident schema

### Day 3: Evidence Parsing
- [ ] Log parser (timestamps, levels, services)
- [ ] Stack trace parser (exceptions, files, lines)
- [ ] Code parser (methods, classes, imports)
- [ ] Git diff parser (changes, additions, deletions)

### Day 4: Chunking & Embeddings
- [ ] Implement chunking strategies
- [ ] Generate embeddings (Sentence Transformers)
- [ ] Test semantic similarity

### Day 5: Retrieval & LLM Integration
- [ ] FAISS indexing
- [ ] Semantic search with metadata filtering
- [ ] Gemini API integration
- [ ] Structured output generation

### Day 6: API & UI
- [ ] FastAPI endpoints
- [ ] Streamlit interface
- [ ] End-to-end pipeline testing

### Day 7: Evaluation & Polish
- [ ] Implement evaluation metrics
- [ ] Run test suite
- [ ] Compare configurations
- [ ] Document results
- [ ] Polish README & repo

---

## 🎓 Learning Objectives

By building TraceLens, you'll understand:

### AI/ML Concepts
- ✓ What embeddings are and why they work
- ✓ Semantic similarity & cosine distance
- ✓ Vector indexing (FAISS)
- ✓ Retrieval-Augmented Generation (RAG)
- ✓ Prompt engineering for structured output
- ✓ LLM hallucination prevention
- ✓ Evaluation metrics for generative systems

### System Design
- ✓ Data pipeline architecture
- ✓ Separation of concerns
- ✓ Metadata preservation through pipelines
- ✓ Error handling & validation
- ✓ Configuration management
- ✓ API design (FastAPI)

### Software Engineering
- ✓ Project structure & organization
- ✓ Testing frameworks
- ✓ Version control best practices
- ✓ Environment management
- ✓ Code documentation

---

## 🔒 Security Considerations

TraceLens handles potentially sensitive data:

### Current Mitigations
- [x] API keys in `.env`, not committed to git
- [x] `.gitignore` prevents accidental secret leaks
- [x] Environment-based configuration

### Recommended for Production
- [ ] Scan logs for API keys, secrets before processing
- [ ] Redact PII before indexing
- [ ] Audit trail for who accessed which incidents
- [ ] Encryption at rest for incident data
- [ ] VPN/private endpoint for Gemini API calls
- [ ] Input validation & sanitization

### Current Limitations
- No built-in secret redaction
- Source code is sent to Gemini API (consider data residency)
- No user authentication
- No audit logging

---

## 📊 Evaluation Methodology

TraceLens is evaluated against a labeled dataset of incidents:

### Metrics

**1. Retrieval Recall@K**
```
Of all evidence relevant to the known root cause,
did the system retrieve it in top-K results?

Recall@5 = (relevant chunks retrieved) / (all relevant chunks)
```

**2. Root-Cause Hypothesis Match**
```
Did the top generated hypothesis mention the known root cause?
(Binary: yes/no or partial match)
```

**3. Evidence Groundedness**
```
% of claims in the report that cite retrieved evidence
(vs. hallucinated or unsubstantiated claims)
```

**4. False Positives**
```
Did the system generate hypotheses unsupported by evidence?
```

### Configuration Comparisons
- Different chunk sizes (256, 512, 1024 tokens)
- Different top-K values (3, 5, 10)
- Different embedding models
- With/without metadata filtering

---

## 📝 Example Incident

### Input

**logs/payment-service.log**
```
2024-01-15T10:32:45.123Z ERROR [PaymentService] Payment processing failed for transaction TX123
2024-01-15T10:32:45.145Z ERROR [PaymentService] java.lang.NullPointerException
2024-01-15T10:32:45.200Z ERROR [PaymentService] at com.payment.PaymentService.processPayment(PaymentService.java:142)
```

**stack-trace.txt**
```
Exception in thread "payment-worker-1":
java.lang.NullPointerException
  at com.payment.PaymentService.processPayment(PaymentService.java:142)
  at com.payment.PaymentController.handleRequest(PaymentController.java:87)
```

**code/PaymentService.java**
```java
public class PaymentService {
  public Payment processPayment(String transactionId) {
    PaymentRepository repo = getRepository();
    Payment payment = repo.findById(transactionId);
    return payment.process();  // Line 142 - NPE here
  }
}
```

**git-diff**
```diff
- PaymentRepository repo = cachedRepository;
+ PaymentRepository repo = getRepository();
```

### Output

```json
{
  "incident_summary": "NullPointerException at PaymentService.java:142 in processPayment()",
  "affected_component": "Payment Service / PaymentRepository",
  "severity": "high",
  "observed_evidence": [
    {
      "type": "exception",
      "content": "NullPointerException at PaymentService.java:142",
      "source": "stack-trace.txt"
    },
    {
      "type": "log",
      "content": "Payment processing failed for transaction TX123",
      "source": "logs/payment-service.log",
      "timestamp": "2024-01-15T10:32:45.123Z"
    },
    {
      "type": "code",
      "content": "payment.process() called without null check",
      "source": "code/PaymentService.java:142"
    }
  ],
  "root_cause_hypotheses": [
    {
      "hypothesis": "PaymentRepository.findById() returned null",
      "confidence": "high",
      "rationale": "Stack trace shows NPE at line 142 where payment.process() is called. Code does not check for null before calling process().",
      "supporting_evidence": [
        "stack-trace.txt",
        "code/PaymentService.java:142"
      ],
      "missing_evidence": [
        "PaymentRepository.findById() implementation",
        "Database transaction TX123 lookup status"
      ]
    }
  ],
  "recommended_investigation_steps": [
    "1. Add null check: if (payment != null) before payment.process()",
    "2. Query database for transaction TX123 status",
    "3. Review recent change to getRepository() method",
    "4. Check if cached repository was thread-safe"
  ],
  "limitations": "Repository implementation not provided. Cannot confirm why null was returned."
}
```

---

## 🎯 Interview Preparation

### Questions You Should Be Able to Answer

**On the Problem**
- Why is this better than pasting logs into ChatGPT?
- Who actually benefits from this tool?
- What's the real problem you're solving?

**On the Architecture**
- Why use embeddings instead of keyword search?
- Why use FAISS?
- What does the chunking layer actually do?
- Why do logs and code need different chunking?

**On the Implementation**
- How do you preserve evidence metadata through the pipeline?
- How do you know retrieval is working?
- How do you prevent the LLM from hallucinating?
- How do you distinguish facts from hypotheses?

**On Evaluation**
- How did you measure Recall@K?
- What were your actual results?
- What configurations did you compare?
- What's the biggest limitation of your approach?

---

## 🚨 Important Limitations

- **Not a definitive root-cause finder** — Generates hypotheses, not certainties
- **Requires good evidence** — If the actual root cause isn't captured in logs/code, system won't find it
- **LLM dependent** — Output quality depends on Gemini's reasoning
- **No historical learning** — Doesn't learn from past incidents (Phase 2)
- **No duplicate detection** — Doesn't find similar incidents (Phase 2)
- **Single-service focused** — Designed for single-service incidents (distributed tracing is Phase 2)

---

## 📚 References & Resources

### Embeddings & Vector Search
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [Understanding Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [FAISS Github](https://github.com/facebookresearch/faiss)

### RAG (Retrieval-Augmented Generation)
- [LangChain Documentation](https://docs.langchain.com/)
- [RAG Fundamentals](https://arxiv.org/abs/2005.11401)

### LLMs & Prompting
- [Gemini API Docs](https://ai.google.dev/)
- [Prompt Engineering Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)

### System Design
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Designing Data-Intensive Applications](https://dataintensive.net/)

---

## 👤 Author

Built as a portfolio project for a Generative AI / AI Engineer role.

**Learning Focus:**
- Embeddings & vector search
- Retrieval-augmented generation
- LLM reasoning & structured output
- System design & engineering

---

## 📄 License

MIT License — See LICENSE file

---

## 📞 Questions?

For issues, questions, or suggestions, open a GitHub issue.

---

**Last Updated:** January 2024  
**Status:** 🚧 In Development (Day 1)
