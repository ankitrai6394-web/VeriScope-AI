"""LLM Provider Abstraction with Gemini, OpenAI, and Deterministic Mock Support.

Features:
- Strict JSON output parsing and markdown-fence stripping.
- System prompt vs. untrusted web snippet sandboxing (prompt injection defense).
- Deterministic mock generator tailored for all 7 agents in demo mode.
"""

import json
import logging
import re
from typing import Dict, Any, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, ValidationError
from backend.app.core.config import settings

logger = logging.getLogger("veriscope.llm")

T = TypeVar("T", bound=BaseModel)


def clean_json_text(text: str) -> str:
    """Strip markdown code block markers and leading/trailing whitespace."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def sanitize_untrusted_content(text: str, max_chars: int = 1500) -> str:
    """Sanitize external content retrieved from the web to neutralize prompt injection tokens."""
    if not text:
        return ""
    # Truncate
    sanitized = text[:max_chars]
    # Neutralize common prompt injection trigger phrases
    danger_patterns = [
        r"(?i)ignore\s+all\s+previous\s+instructions",
        r"(?i)system\s*prompt",
        r"(?i)you\s+are\s+now\s+a",
        r"(?i)disregard\s+prior",
    ]
    for pattern in danger_patterns:
        sanitized = re.sub(pattern, "[FILTERED_INSTRUCTION]", sanitized)
    return sanitized


class BaseLLMProvider:
    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_cls: Type[T],
    ) -> T:
        raise NotImplementedError


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_cls: Type[T],
    ) -> T:
        full_system = (
            f"{system_prompt}\n\n"
            f"IMPORTANT: You must output ONLY a valid, raw JSON object matching the required schema. "
            f"Do not include markdown ticks, explanatory text, or preamble."
        )

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": f"SYSTEM INSTRUCTIONS:\n{full_system}\n\nUSER TASK:\n{user_prompt}"}
                    ],
                }
            ],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "response_mime_type": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(self.endpoint, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"Gemini API error (Status {response.status_code}): {response.text}"
                )

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise RuntimeError("Gemini API returned no candidates.")

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            clean_text = clean_json_text(raw_text)
            parsed_json = json.loads(clean_text)
            return schema_cls.model_validate(parsed_json)


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_cls: Type[T],
    ) -> T:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "response_format": {"type": "json_object"},
        }

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(self.endpoint, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(
                    f"OpenAI API error (Status {response.status_code}): {response.text}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            clean_text = clean_json_text(content)
            parsed_json = json.loads(clean_text)
            return schema_cls.model_validate(parsed_json)


class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM generator for all agent outputs.
    
    Provides mathematically and semantically consistent outputs across all 7 agents,
    ensuring testability and flawless demo operation without external credentials.
    """

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_cls: Type[T],
    ) -> T:
        schema_name = schema_cls.__name__

        if schema_name == "PlannerOutput":
            data = {
                "topic": "AI Impact on Graduate Employment in India (2022-2025)",
                "research_objective": "Empirically assess whether artificial intelligence is creating or displacing entry-level graduate employment opportunities in India's technology sector during 2022-2025, measuring net job creation, salary premiums, and curriculum alignment gaps.",
                "sub_questions": [
                    "What is the net change in fresher intake at India's top 10 IT companies from 2021 to 2024?",
                    "How has demand for AI/ML skills among fresh graduates shifted compared to traditional programming roles?",
                    "What do government (MeitY, NASSCOM) datasets show about AI sector job creation vs traditional IT job displacement?",
                    "How does India's Global Capability Center (GCC) expansion affect fresh graduate employment figures?",
                    "What is the urban graduate unemployment rate among CS/IT graduates specifically, and how has it trended since 2022?"
                ],
                "search_queries": [
                    "India IT fresher hiring 2023 2024 AI displacement NASSCOM",
                    "MeitY digital economy jobs AI graduates India 2024",
                    "India campus recruitment decline TCS Infosys Wipro 2023",
                    "AI ML specialist fresher salary premium India 2024",
                    "India GCC global capability center jobs fresh graduates",
                    "urban graduate unemployment IT CS India CMIE 2024"
                ],
                "required_source_types": ["government_report", "industry_census", "academic_study", "financial_press", "think_tank"],
                "research_strategy": "Cross-reference MeitY government data with NASSCOM industry census, supplement with IIM-A academic analysis, and triangulate against CMIE household survey data to establish empirically grounded conclusions about AI's bifurcating effect on graduate employment."
            }

        elif schema_name == "EvidenceExtractionOutput":
            data = {
                "claims": [
                    {
                        "claim_id": "CLM-001",
                        "claim": "Generative AI job openings in India expanded by 45% between 2023 and 2024.",
                        "source_ids": ["SRC-001"],
                        "evidence_type": "statistical",
                        "confidence": 0.88
                    },
                    {
                        "claim_id": "CLM-002",
                        "claim": "Campus fresher intake among tier-1 Indian IT companies contracted by 22% to 30% due to AI-assisted developer productivity.",
                        "source_ids": ["SRC-001", "SRC-004"],
                        "evidence_type": "statistical",
                        "confidence": 0.84
                    },
                    {
                        "claim_id": "CLM-003",
                        "claim": "Engineering graduates with verified MLOps or prompt engineering proficiencies command a 35% starting salary premium.",
                        "source_ids": ["SRC-003"],
                        "evidence_type": "empirical",
                        "confidence": 0.81
                    },
                    {
                        "claim_id": "CLM-004",
                        "claim": "The Indian digital economy added 280,000 net new tech positions in FY 2023-24, with 42,000 entry-level AI CoE roles.",
                        "source_ids": ["SRC-002"],
                        "evidence_type": "statistical",
                        "confidence": 0.90
                    },
                    {
                        "claim_id": "CLM-005",
                        "claim": "Artificial intelligence will completely eliminate 100% of all software engineering graduate jobs in India by 2026.",
                        "source_ids": ["SRC-004"],
                        "evidence_type": "speculative",
                        "confidence": 0.25
                    },
                    {
                        "claim_id": "CLM-006",
                        "claim": "Urban graduate unemployment in India stands at 13.4% due to academia-industry skill mismatches with modern AI stacks.",
                        "source_ids": ["SRC-006"],
                        "evidence_type": "empirical",
                        "confidence": 0.86
                    },
                    {
                        "claim_id": "CLM-007",
                        "claim": "AI adoption in Indian IT will reduce net overall tech sector employment by 40% before 2027.",
                        "source_ids": ["SRC-004", "SRC-005"],
                        "evidence_type": "forecast",
                        "confidence": 0.65
                    },
                    {
                        "claim_id": "CLM-008",
                        "claim": "Autonomous AI coding agents have already replaced all manual unit testing in Indian tier-2 software houses.",
                        "source_ids": ["SRC-004"],
                        "evidence_type": "observational",
                        "confidence": 0.40
                    }
                ]
            }

        elif schema_name == "VerificationOutput":
            data = {
                "verifications": [
                    {
                        "claim_id": "CLM-001",
                        "verification_status": "SUPPORTED",
                        "explanation": "Supported directly by NASSCOM's Strategic Talent Review 2024 documenting a 45% surge in specialized generative AI listings.",
                        "supporting_source_ids": ["SRC-001"],
                        "contradicting_source_ids": [],
                        "limitations": "Measures total specialized listings; may reflect talent scarcity rather than pure net new headcount."
                    },
                    {
                        "claim_id": "CLM-002",
                        "verification_status": "SUPPORTED",
                        "explanation": "Corroborated across both NASSCOM industry census and Economic Times corporate reporting (TCS, Infosys, Wipro fresher intake data).",
                        "supporting_source_ids": ["SRC-001", "SRC-004"],
                        "contradicting_source_ids": [],
                        "limitations": "Macroeconomic tech slowdown also contributed alongside AI productivity gains."
                    },
                    {
                        "claim_id": "CLM-003",
                        "verification_status": "SUPPORTED",
                        "explanation": "Verified by IIM Ahmedabad empirical working paper studying 48 colleges, measuring $8,200 median vs $6,070 base for standard non-AI peers.",
                        "supporting_source_ids": ["SRC-003"],
                        "contradicting_source_ids": [],
                        "limitations": "Sample skewed toward tier-1 and tier-2 institutions."
                    },
                    {
                        "claim_id": "CLM-004",
                        "verification_status": "SUPPORTED",
                        "explanation": "Directly backed by MeitY FY 2023-24 official government tech employment publication.",
                        "supporting_source_ids": ["SRC-002"],
                        "contradicting_source_ids": [],
                        "limitations": "Government figures aggregate semiconductor manufacturing alongside pure software roles."
                    },
                    {
                        "claim_id": "CLM-005",
                        "verification_status": "CONTRADICTED",
                        "explanation": "Contradicted by empirical job data and government figures. While routine tasks are automated, net hiring continues with new specialized roles.",
                        "supporting_source_ids": [],
                        "contradicting_source_ids": ["SRC-001", "SRC-002", "SRC-005"],
                        "limitations": "Long-term decade shifts remain subject to modeling uncertainty."
                    },
                    {
                        "claim_id": "CLM-006",
                        "verification_status": "PARTIALLY_SUPPORTED",
                        "explanation": "CMIE confirms 13.4% urban graduate unemployment; curriculum misalignment is cited by employers as a major contributor.",
                        "supporting_source_ids": ["SRC-006"],
                        "contradicting_source_ids": [],
                        "limitations": "Unemployment is influenced by broader macroeconomic cycles, not exclusively AI skill gaps."
                    },
                    {
                        "claim_id": "CLM-007",
                        "verification_status": "CONFLICTING_EVIDENCE",
                        "explanation": "WEF forecasts a 40% task-automation shift, whereas MeitY and NASSCOM project net expansion in digital economy employment.",
                        "supporting_source_ids": ["SRC-005"],
                        "contradicting_source_ids": ["SRC-001", "SRC-002"],
                        "limitations": "Projections rely on divergent macroeconomic modeling assumptions."
                    },
                    {
                        "claim_id": "CLM-008",
                        "verification_status": "INSUFFICIENT_EVIDENCE",
                        "explanation": "Current empirical sources lack granular survey data on tier-2 enterprise tool adoption rates.",
                        "supporting_source_ids": [],
                        "contradicting_source_ids": [],
                        "limitations": "Anecdotal press mentions lack verified sample sizes or statistical backing."
                    }
                ]
            }

        elif schema_name == "SourceReliabilityOutput":
            data = {
                "assessments": [
                    {
                        "source_id": "SRC-001",
                        "domain": "nasscom.in",
                        "source_type": "industry",
                        "reliability_score": 0.88,
                        "rationale": "Premier Indian technology trade association conducting regular corporate employment censuses with high methodological transparency.",
                        "is_primary_source": True
                    },
                    {
                        "source_id": "SRC-002",
                        "domain": "meity.gov.in",
                        "source_type": "government",
                        "reliability_score": 0.94,
                        "rationale": "Official Indian federal ministry publication. Highly authoritative empirical record of legal filings and national tech programs.",
                        "is_primary_source": True
                    },
                    {
                        "source_id": "SRC-003",
                        "domain": "iima.ac.in",
                        "source_type": "academic",
                        "reliability_score": 0.91,
                        "rationale": "Top-tier national management research institute. Rigorous peer-reviewed methodology and independent campus placement data.",
                        "is_primary_source": True
                    },
                    {
                        "source_id": "SRC-004",
                        "domain": "economictimes.indiatimes.com",
                        "source_type": "news",
                        "reliability_score": 0.76,
                        "rationale": "Leading national financial daily. Reliable journalistic reporting of executive interviews, though secondary in analytical nature.",
                        "is_primary_source": False
                    },
                    {
                        "source_id": "SRC-005",
                        "domain": "weforum.org",
                        "source_type": "industry",
                        "reliability_score": 0.85,
                        "rationale": "Global non-governmental economic body. Large multi-country sample size, though heavily forward-looking and forecast-dependent.",
                        "is_primary_source": False
                    },
                    {
                        "source_id": "SRC-006",
                        "domain": "cmie.com",
                        "source_type": "industry",
                        "reliability_score": 0.83,
                        "rationale": "Widely cited private macroeconomic survey organization. Strong household survey sampling across urban centers.",
                        "is_primary_source": True
                    }
                ]
            }

        elif schema_name == "ContradictionOutput":
            data = {
                "has_contradictions": True,
                "contradictions": [
                    {
                        "claim_ids": ["CLM-002", "CLM-004"],
                        "conflicting_sources": ["SRC-001", "SRC-002"],
                        "statement_a": "Campus fresher intake at IT giants declined by 22-30% in 2023.",
                        "statement_b": "The digital economy registered 280,000 net new tech positions in FY 2023-24.",
                        "divergence_reason": "definition",
                        "analysis": "This is a divergence in market segment definitions rather than a factual error: IT giants (TCS, Infosys) reduced traditional mass campus hiring due to developer automation, whereas overall digital economy hiring grew via Global Capability Centers (GCCs), semiconductor initiatives, and AI startups."
                    }
                ]
            }

        elif schema_name == "ReportGenerationOutput":
            data = {
                "report_title": "Empirical Assessment of AI's Impact on Entry-Level Graduate Employment in India",
                "executive_summary": "Artificial intelligence is exerting a distinct bifurcating impact on India's fresh graduate employment landscape. Rather than a unilateral elimination or boom, the market has bifurcated: traditional entry-level routine programming and software testing roles have dropped by 22% to 30%, while specialized demand for graduates with verified AI, MLOps, and prompt workflows has expanded by 45%, offering a 35% starting salary premium. The core friction is an educational curriculum misalignment rather than a total collapse of employment opportunity.",
                "methodology": "Multi-agent cross-referencing across 6 authoritative sources comprising government records (MeitY), academic studies (IIM-A), industry censuses (NASSCOM, WEF, CMIE), and financial press. Claims were extracted, independently verified against primary datasets, and evaluated for methodological divergences.",
                "key_findings": [
                    "Bifurcation Effect: Traditional IT fresher intake contracted by ~25%, driven by Copilot-like developer throughput gains.",
                    "Premium for AI Proficiencies: MLOps and applied AI proficiencies secure a 35% higher median salary ($8,200 vs $6,070).",
                    "Net Ecosystem Growth: GCCs and national AI initiatives generated 42,000 entry-level AI CoE roles, offsetting routine outsourcing cuts.",
                    "Curriculum Gap: Urban graduate unemployment remains at 13.4%, aggravated by outdated university computing syllabi."
                ],
                "limitations": "Aggregated hiring statistics conflate mass IT services with high-growth Global Capability Centers. Longitudinal career trajectory data for AI-trained graduates spans only 2022-2024.",
                "conclusion": "AI is not destroying graduate tech employment in India; it is aggressively redefining the qualification baseline. Universities and students who adapt to modern AI engineering thrive, while those relying on legacy repetitive coding curricula experience prolonged unemployment.",
                "markdown_content": "# Research Dossier: AI Impact on Indian Graduate Employment\n\n## 1. Executive Summary\nArtificial intelligence is exerting a distinct bifurcating impact on India's fresh graduate employment landscape..."
            }
        else:
            raise ValueError(f"Unknown mock schema requested: {schema_name}")

        return schema_cls.model_validate(data)


def get_llm_provider(mode: str = "live") -> BaseLLMProvider:
    """Factory providing the configured LLM provider or fallback to mock."""
    if mode == "demo" or not settings.LLM_API_KEY:
        return MockLLMProvider()

    provider_name = settings.LLM_PROVIDER.lower()
    if provider_name == "gemini":
        return GeminiLLMProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
    elif provider_name == "openai":
        return OpenAILLMProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)

    return MockLLMProvider()
