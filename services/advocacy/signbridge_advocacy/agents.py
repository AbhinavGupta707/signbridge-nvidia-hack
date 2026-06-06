from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .retrieval import LocalRetriever, tokenize


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str
    title: str
    claim: str
    chunk_ids: tuple[str, ...]
    any_terms: tuple[str, ...]
    min_term_hits: int = 1
    priority: int = 50
    policy_domain: str = "housing_repair"


POLICY_RULES: tuple[PolicyRule, ...] = (
    PolicyRule(
        rule_id="emergency-child-asthma",
        title="Child asthma can make damp and mould urgent",
        claim=(
            "Because the report mentions damp or mould affecting a child with asthma, "
            "GOV.UK landlord guidance gives a similar example as a potential emergency hazard, "
            "and the City policy says household vulnerability is part of damp and mould triage."
        ),
        chunk_ids=("govuk-landlord-child-asthma", "col-risk-based-assessment", "col-vulnerable-groups"),
        any_terms=("child", "children", "asthma", "bedroom", "respiratory", "breathing", "health"),
        min_term_hits=2,
        priority=100,
    ),
    PolicyRule(
        rule_id="awaabs-law-timeframes",
        title="Awaab's Law sets social-housing hazard deadlines",
        claim=(
            "For covered social housing tenancies, Awaab's Law guidance says emergency hazards "
            "must be made safe within 24 hours, and significant damp and mould hazards must be "
            "investigated within 10 working days and made safe within 5 working days after investigation."
        ),
        chunk_ids=("govuk-tenant-awaabs-summary", "govuk-tenant-written-summary"),
        any_terms=(
            "awaab",
            "law",
            "deadline",
            "timescale",
            "24",
            "hours",
            "significant",
            "emergency",
            "child",
            "asthma",
            "bedroom",
        ),
        min_term_hits=2,
        priority=95,
    ),
    PolicyRule(
        rule_id="city-report-details",
        title="Report location, extent, and vulnerability",
        claim=(
            "City of London Housing asks City-managed residents to report damp and mould immediately "
            "and include the location, extent, and whether anyone in the household is vulnerable."
        ),
        chunk_ids=("col-report-damp-mould",),
        any_terms=("report", "damp", "mould", "vulnerable", "property", "phone", "online"),
        min_term_hits=2,
        priority=90,
    ),
    PolicyRule(
        rule_id="city-response-aims",
        title="City response aims for damp, mould, and leaks",
        claim=(
            "City of London Housing publishes target response windows: damp and mould inspections "
            "within 10 working days, standard mould treatment within 10 working days, severe mould "
            "treatment within 24 hours, and severe uncontainable leak emergency repair within 24 hours."
        ),
        chunk_ids=("col-web-response-aims", "col-policy-timescales"),
        any_terms=("inspection", "appointment", "treatment", "repair", "leak", "water", "days", "hours"),
        min_term_hits=1,
        priority=85,
    ),
    PolicyRule(
        rule_id="temporary-accommodation",
        title="Ask about temporary accommodation if the home cannot be made safe",
        claim=(
            "City policy says serious health risk cases may require emergency action including temporary "
            "accommodation, and GOV.UK guidance says suitable alternative accommodation must be offered "
            "if a covered home cannot be made safe within Awaab's Law timescales."
        ),
        chunk_ids=("col-temporary-accommodation", "govuk-tenant-alternative-accommodation"),
        any_terms=("unsafe", "temporary", "accommodation", "decant", "cannot", "stay", "health", "risk"),
        min_term_hits=1,
        priority=80,
    ),
    PolicyRule(
        rule_id="accessible-communication",
        title="Accessible communication can include interpretation or transcription",
        claim=(
            "The City damp and mould policy says customers with distinct communication needs should not be "
            "unreasonably or disproportionately affected, and appropriate arrangements may include "
            "interpretation or transcription."
        ),
        chunk_ids=("col-accessible-communication",),
        any_terms=("deaf", "bsl", "interpreter", "interpretation", "caption", "transcription", "accessible", "communication"),
        min_term_hits=1,
        priority=75,
        policy_domain="accessible_communication",
    ),
    PolicyRule(
        rule_id="records-and-follow-up",
        title="Keep evidence and ask for follow-up",
        claim=(
            "The City damp and mould page advises residents to keep photos and reporting dates; the City policy "
            "says damp and mould instances and actions are recorded, and severe cases aim for a six-month revisit."
        ),
        chunk_ids=("col-keep-records", "col-follow-up-records"),
        any_terms=("photo", "record", "evidence", "date", "follow", "six", "months", "writing"),
        min_term_hits=1,
        priority=70,
    ),
    PolicyRule(
        rule_id="no-blame",
        title="Damp and mould reports should not be prejudged",
        claim=(
            "The City policy says residents reporting damp and mould should be treated with empathy and respect "
            "and that the cause should not be prejudged; it also says a condensation finding is not meant to imply blame."
        ),
        chunk_ids=("col-empathy-no-prejudge",),
        any_terms=("blame", "fault", "lifestyle", "condensation", "prejudge", "respect", "empathy"),
        min_term_hits=1,
        priority=65,
    ),
    PolicyRule(
        rule_id="complaints-route",
        title="Use the housing complaints route if unresolved",
        claim=(
            "If the issue is not resolved, City of London Housing says residents can make a formal complaint with "
            "dates, documents, what went wrong, and what should put it right; the page says residents can contact "
            "the Housing Ombudsman Service at any stage of a complaint."
        ),
        chunk_ids=("col-complaint-info-needed", "col-complaint-definition-ombudsman"),
        any_terms=("complaint", "delay", "ignored", "unresolved", "ombudsman", "failed", "unfair", "standard"),
        min_term_hits=1,
        priority=60,
    ),
    PolicyRule(
        rule_id="repairs-performance-context",
        title="Repairs performance is a live regulatory issue",
        claim=(
            "The February 2026 regulatory judgement identifies serious failings in City of London Corporation "
            "repairs, maintenance, and planned improvements; this is context for careful record keeping, not an "
            "individual entitlement."
        ),
        chunk_ids=("rsh-col-repairs-failings", "col-tsm-repairs-context"),
        any_terms=("regulator", "performance", "failings", "repairs", "maintenance", "decent", "targets"),
        min_term_hits=1,
        priority=40,
        policy_domain="regulatory_context",
    ),
)


class PolicyAgent:
    def __init__(self, retriever: LocalRetriever | None = None) -> None:
        self.retriever = retriever or LocalRetriever()

    def generate_cards(
        self,
        text: str,
        *,
        session_id: str | None = None,
        utterance_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        tokens = set(tokenize(text))
        cards: list[dict[str, Any]] = []
        for rule in sorted(POLICY_RULES, key=lambda item: item.priority, reverse=True):
            hits = sum(1 for term in rule.any_terms if term in tokens or term.lower() in text.lower())
            if hits < rule.min_term_hits:
                continue
            citations = [self.retriever.citation_for_chunk_id(chunk_id) for chunk_id in rule.chunk_ids]
            if not citations:
                continue
            if any(not citation["source_url"] or not citation["quote"] for citation in citations):
                continue
            primary = citations[0]
            card = {
                "type": "policy.card",
                "id": f"p-{rule.rule_id}",
                "title": rule.title,
                "claim": rule.claim,
                "source_title": primary["source_title"],
                "source_url": primary["source_url"],
                "quote": primary["quote"],
                "citations": citations,
                "policy_domain": rule.policy_domain,
                "verified": all(citation["verified"] for citation in citations),
            }
            if session_id:
                card["session_id"] = session_id
            if utterance_id:
                card["utterance_id"] = utterance_id
            cards.append(card)
            if len(cards) >= limit:
                break
        return cards


class QuestionAgent:
    def generate_prompts(
        self,
        policy_cards: list[dict[str, Any]],
        *,
        session_id: str | None = None,
        utterance_id: str | None = None,
        limit: int = 4,
    ) -> list[dict[str, Any]]:
        prompts: list[dict[str, Any]] = []
        for card in policy_cards:
            prompt_text = self._prompt_for_card(card)
            if not prompt_text:
                continue
            event = {
                "type": "question.prompt",
                "id": f"q-{card['id'][2:]}",
                "text": prompt_text,
                "policy_card_ids": [card["id"]],
                "citations": card.get("citations", []),
            }
            if session_id:
                event["session_id"] = session_id
            if utterance_id:
                event["utterance_id"] = utterance_id
            prompts.append(event)
            if len(prompts) >= limit:
                break
        return prompts

    @staticmethod
    def _prompt_for_card(card: dict[str, Any]) -> str | None:
        card_id = card["id"]
        if card_id == "p-emergency-child-asthma":
            return (
                "Ask whether this is being treated as an emergency hazard because damp or mould "
                "is affecting your child's asthma, and when someone will attend."
            )
        if card_id == "p-awaabs-law-timeframes":
            return (
                "Ask the officer to confirm whether Awaab's Law applies to your tenancy, and to give "
                "the investigation, make-safe, written-summary, and follow-up-work dates in writing."
            )
        if card_id == "p-city-report-details":
            return (
                "Ask for the report reference number and confirm that the location, extent, and household "
                "vulnerability details have been logged."
            )
        if card_id == "p-city-response-aims":
            return "Ask what risk category has been assigned and the date of the inspection or repair appointment."
        if card_id == "p-temporary-accommodation":
            return (
                "Ask what temporary or alternative accommodation support is available if the home cannot "
                "be made safe within the required timeframe."
            )
        if card_id == "p-accessible-communication":
            return (
                "Ask for all repair appointments, updates, and complaint responses to be provided in writing "
                "or with BSL/interpreting or transcription support."
            )
        if card_id == "p-records-and-follow-up":
            return "Ask which photos, health details, dates, and repair references should be attached to the case record."
        if card_id == "p-no-blame":
            return "Ask for the diagnosis and repair plan to be recorded without blaming you before the cause is investigated."
        if card_id == "p-complaints-route":
            return "Ask how to escalate a formal complaint if the target date is missed, and what evidence the team needs."
        if card_id == "p-repairs-performance-context":
            return "Ask for the repair plan, target date, and owner to be written into the appointment record."
        return None


class AdvocacyPipeline:
    def __init__(
        self,
        retriever: LocalRetriever | None = None,
        policy_agent: PolicyAgent | None = None,
        question_agent: QuestionAgent | None = None,
    ) -> None:
        self.retriever = retriever or LocalRetriever()
        self.policy_agent = policy_agent or PolicyAgent(self.retriever)
        self.question_agent = question_agent or QuestionAgent()

    def run_turn(
        self,
        text: str,
        *,
        session_id: str,
        utterance_id: str,
        card_limit: int = 5,
        question_limit: int = 4,
    ) -> dict[str, list[dict[str, Any]]]:
        cards = self.policy_agent.generate_cards(
            text,
            session_id=session_id,
            utterance_id=utterance_id,
            limit=card_limit,
        )
        questions = self.question_agent.generate_prompts(
            cards,
            session_id=session_id,
            utterance_id=utterance_id,
            limit=question_limit,
        )
        return {"policy_cards": cards, "question_prompts": questions}
