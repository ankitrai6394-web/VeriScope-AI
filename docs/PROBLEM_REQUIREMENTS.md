# VeriScope AI — Problem & Requirements Specification
## Problem Statement: PS03 – Multi-Agent Research & Fact-Checking
**Competition:** Hack2skill PromptWars x Agent X 2.0  
**Project:** VeriScope AI  
**Author:** Solo Developer Track  
**Date:** November 2026  
**Status:** Phase 1 – Architecture & Requirements Baselining

---

## 1. Problem Definition
In the era of information abundance and generative AI, research analysts, journalists, students, and decision-makers face severe challenges regarding information accuracy, hallucinations, confirmation bias, and conflicting reporting across the web. Standard generative chatbots frequently hallucinate sources, fabricate statistics, and offer plausible-sounding answers without transparent verification or traceable citations.

**PS03 (Multi-Agent Research & Fact-Checking)** tasks us with engineering a genuine, multi-agent AI research platform that autonomously decomposes a complex research query, gathers primary and secondary empirical evidence from external sources, extracts atomic claims, cross-verifies claims against independent data, detects real-world contradictions, evaluates source reliability, and synthesizes a structured, citation-backed investigative report.

---

## 2. Target Users
1. **Academic Researchers & Students:** Needing fast literature aggregation and verification of empirical findings without manual cross-referencing of dozen-page PDFs.
2. **Journalists & Fact-Checkers:** Requiring multi-source cross-examination, contradiction detection between reports, and auditable proof chains.
3. **Market Analysts & Decision Makers:** Synthesizing industry trends, employment metrics, and technological shifts with clear delineation between verified facts, predictions, and insufficient evidence.

---

## 3. Core Challenges
1. **Source Hallucination Mitigation:** Ensuring no source URL, publication date, quotation, or institution is fabricated by the LLM.
2. **Atomic Claim Extraction:** Isolating factual and statistical claims from contextual prose without altering semantic meaning or polarity.
3. **Epistemic Classification:** Accurately distinguishing between *SUPPORTED*, *CONTRADICTED*, *PARTIALLY_SUPPORTED*, *INSUFFICIENT_EVIDENCE*, and *CONFLICTING_EVIDENCE*.
4. **Contradiction Diagnosis:** Distinguishing between genuine falsehoods and variations resulting from differing reporting years, survey populations, or methodology definitions.
5. **Prompt Injection & Unsafe Retrieval:** Shielding agents from prompt injections embedded in retrieved web pages, preventing SSRF attacks, and isolating research evidence from executable instructions.
6. **Robust Deterministic Fallbacks:** Delivering a reliable, deterministic demo mode when API keys are absent, without pretending synthetic data is live research.

---

## 4. Proposed Solution: VeriScope AI
VeriScope AI is a multi-agent fact-checking and research orchestration engine featuring:
- **7 Specialized Agents:** Each bound by strict input/output Pydantic contracts and single-responsibility execution.
- **Asynchronous Orchestration Engine:** Concurrent execution of non-dependent tasks (Fact Verification & Source Reliability run in parallel after Evidence Extraction).
- **Dual-Mode Operation:** Seamless operation in **Live Mode** (Tavily Search + LLM Provider) and **Demo Mode** (deterministic pre-verified sample datasets for automated evaluation without API keys).
- **Full Traceability:** Every extracted claim references unique source IDs (`SRC-xxx`), claim IDs (`CLM-xxx`), verification explanations, and contradiction notes.
- **SaaS-Grade Modern UI:** Built with Vite, React, TypeScript, Tailwind CSS, Lucide icons, and Recharts, meeting WCAG 2.1 AA accessibility standards.

---

## 5. Functional Requirements (FR)

### FR-01: Research Planning & Decomposition
- **FR-01.1:** Accept a natural language research query (up to 500 characters).
- **FR-01.2:** Deconstruct the root query into 3–5 targeted sub-questions and key search queries.
- **FR-01.3:** Output structured research strategy specifying required source categories (Government, Academic, Industry, News).

### FR-02: Multi-Source Web Discovery
- **FR-02.1:** Execute search queries via configurable provider (Tavily API or Deterministic Mock).
- **FR-02.2:** Extract and deduplicate source metadata: Title, Canonical URL, Domain, Publication Date (if available), and Content Snippet.
- **FR-02.3:** Reject invalid schemes, local IP addresses (SSRF protection), and unreachable sources.

### FR-03: Evidence & Claim Extraction
- **FR-03.1:** Extract discrete factual claims from collected snippets, assigning each a unique identifier (`CLM-001`, `CLM-002`, etc.).
- **FR-03.2:** Associate each claim with one or more source IDs (`SRC-001`).
- **FR-03.3:** Classify evidence type (statistical, empirical, observational, definitional) and model assessment score.

### FR-04: Independent Fact Verification
- **FR-04.1:** Cross-evaluate each claim against all collected sources.
- **FR-04.2:** Assign one of 5 strict statuses:
  - `SUPPORTED`
  - `CONTRADICTED`
  - `PARTIALLY_SUPPORTED`
  - `INSUFFICIENT_EVIDENCE`
  - `CONFLICTING_EVIDENCE`
- **FR-04.3:** Provide justification, supporting source IDs, contradicting source IDs, and limitations.

### FR-05: Source Reliability Assessment
- **FR-05.1:** Evaluate domain reputation, top-level domain (`.gov`, `.edu`, `.org`), publication freshness, and source type (primary vs. secondary).
- **FR-05.2:** Compute a transparent credibility score with rationales; never treat domain name as single proof of truth.

### FR-06: Contradiction Detection & Synthesis
- **FR-06.1:** Detect discrepancies across independent sources (e.g., contrasting numerical adoption rates).
- **FR-06.2:** Analyze root causes of divergences (temporal difference, population sample, definition nuance).

### FR-07: Structured Report Generation
- **FR-07.1:** Synthesize a comprehensive 11-section research dossier:
  1. Research Overview
  2. Executive Summary
  3. Research Methodology
  4. Key Findings
  5. Verified Claims
  6. Contradicted Claims
  7. Conflicting Evidence
  8. Source Reliability Analysis
  9. Research Limitations
  10. Final Conclusion
  11. References
- **FR-07.2:** Export or inspect in interactive UI with direct links and status badges.

### FR-08: Research Session Persistence & Management
- **FR-08.1:** Store research sessions, agent execution logs, sources, claims, and reports in SQLite.
- **FR-08.2:** Provide full history view, session retrieval, and session deletion.

---

## 6. Non-Functional Requirements (NFR)

### NFR-01: Performance & Efficiency
- Non-blocking asynchronous FastAPI execution with immediate session ID return.
- Polling / status endpoint for real-time agent progression updates.
- Parallel execution of Agent 4 (Fact Verification) and Agent 5 (Source Reliability).
- Result caching and bounded search extraction to respect API quotas and execution time.

### NFR-02: Security & Hardening
- Strict Pydantic schema validation on all inputs.
- Query sanitization and prompt injection delimiters separating untrusted web content from system instructions.
- SSRF prevention (blocking RFC 1918 private IPs, loopbacks, and non-HTTP/HTTPS schemes).
- Zero secrets committed to git or exposed through client-facing API responses.

### NFR-03: Accessibility (WCAG 2.1 AA)
- Semantic HTML tags (`<main>`, `<nav>`, `<header>`, `<section>`, `<article>`).
- Dual visual encoding: verification statuses indicated by text, icon, and distinct high-contrast colors (never color alone).
- ARIA live regions for agent progress announcements.
- Full keyboard focus management (`Tab`, `Shift+Tab`, `Enter`, `Escape`).

### NFR-04: Code Quality & Architecture
- Clean layered separation: `agents/`, `api/`, `core/`, `models/`, `providers/`, `schemas/`, `services/`.
- Strict typing (Python type hints + TypeScript interfaces).
- Zero external heavyweight agent framework lock-in (pure lightweight custom orchestrator).

### NFR-05: Submission Restrictions
- Single branch (`main`).
- Git repository size strictly below 10 MB.
- Comprehensive `.gitignore` excluding binaries, virtual environments, node modules, and databases.

---

## 7. Technical Architecture

```
                             +-----------------------+
                             |   User Query (Web)    |
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             | Research Planner      | (Agent 1)
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             | Research Discovery    | (Agent 2)
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             | Evidence Extraction   | (Agent 3)
                             +-----------+-----------+
                                         |
                       +-----------------+-----------------+
                       |                                   |
                       v                                   v
          +-----------------------+           +-----------------------+
          | Fact Verification     |           | Source Reliability    |
          | (Agent 4)             |           | (Agent 5)             |
          +-----------+-----------+           +-----------+-----------+
                       |                                   |
                       +-----------------+-----------------+
                                         |
                                         v
                             +-----------------------+
                             | Contradiction Detect  | (Agent 6)
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             | Report Generation     | (Agent 7)
                             +-----------+-----------+
                                         |
                                         v
                             +-----------------------+
                             | Final Verified Dossier|
                             +-----------------------+
```

---

## 8. Evaluation Criteria Alignment Matrix

| Evaluation Parameter | Architectural Feature / Implementation Strategy | Verification Metric |
| :--- | :--- | :--- |
| **1. Code Quality** | Modular design, Pydantic v2 schemas, strict type annotations, separation of concerns. | Clean linter run, zero unresolved circular imports. |
| **2. Security** | SSRF protection, prompt injection barriers, input length caps, environment variable protection. | Dedicated security test suite for injection & SSRF. |
| **3. Efficiency** | Asynchronous task execution (`asyncio.gather`), query deduplication, token-optimized prompts. | Sub-30s execution for complete multi-agent pipeline in live mode. |
| **4. Testing** | Pytest unit and integration test suite, Vitest frontend tests, deterministic mock providers. | Automated test suite passes with zero paid API requirement. |
| **5. Accessibility** | WCAG 2.1 AA compliant colors, semantic HTML, screen reader labels, keyboard navigable tables. | Axe-core accessibility checklist verified. |
| **6. PS03 Alignment**| Autonomous multi-agent pipeline, claim extraction, verification taxonomy, contradiction explanation. | 100% coverage of all 7 agents and required report sections. |

---

## 9. Official PS03 Problem Statement Alignment Note
The requirements above have been mapped strictly from the Hack2skill PromptWars x Agent X 2.0 PS03 master brief. If any additional competition rubric, scoring sheet, or document is issued by the competition organizers, it will be immediately incorporated into this document.
