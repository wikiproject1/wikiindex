from typing import Dict, Any, List
from pydantic import BaseModel

class TrustSignal(BaseModel):
    id: str
    title: str
    description: str
    status: str  # 'pass', 'warn', 'fail'
    score_impact: int

class AnalysisResult(BaseModel):
    swahili_title: str
    english_title: str | None
    trust_score: int
    summary: str
    signals: List[TrustSignal]
    references: List[str]
    internal_links: List[str]
    intro_text: str | None
    language_count: int
    swahili_exists: bool
    jamii: List[str]
    last_update: str | None
    image_url: str | None
    details: Dict[str, Any]

class AnalysisService:
    def analyze_article(self, sw_data: Dict[str, Any], en_data: Dict[str, Any] | None, lang_info: Dict[str, Any]) -> AnalysisResult:
        score = 100
        signals = []
        details = {}

        # 1. Existence Check
        if not sw_data:
             return AnalysisResult(
                swahili_title="Unknown",
                english_title=None,
                trust_score=0,
                summary="Article not found or inaccessible.",
                signals=[],
                references=[],
                internal_links=[],
                intro_text=None,
                language_count=0,
                swahili_exists=False,
                jamii=[],
                last_update=None,
                image_url=None,
                details={}
            )
        
        sw_title = sw_data.get("title", "Unknown")
        en_title = en_data.get("title") if en_data else None

        # 2. English Parity Check
        if not en_data:
            score -= 30
            signals.append(TrustSignal(
                id="missing_source",
                title="Missing Source Article",
                description="Could not find a direct link to an English Wikipedia article. Harder to verify translation accuracy.",
                status="fail",
                score_impact=-30
            ))
        else:
            signals.append(TrustSignal(
                id="source_found",
                title="English Source Found",
                description=f"Linked to English article: {en_title}",
                status="pass",
                score_impact=0
            ))

            # 3. Content Length Comparison (Heuristic)
            sw_len = len(sw_data.get("extract", ""))
            en_len = len(en_data.get("extract", ""))
            
            # Avoid division by zero
            # In new version, extract is just intro, so this heuristic is less useful, 
            # but we can use it if we fetched full content. 
            # For now, let's keep it but note it's based on intro.
            ratio = sw_len / en_len if en_len > 0 else 0
            
            details["length_ratio"] = round(ratio, 2)
            
            if ratio < 0.1:
                score -= 20 # Reduced impact since intro-only might vary widely
                signals.append(TrustSignal(
                    id="stub_risk",
                    title="Significantly Shorter",
                    description="The Swahili intro is much shorter than the English version.",
                    status="fail",
                    score_impact=-20
                ))
            else:
                signals.append(TrustSignal(
                    id="good_length",
                    title="Comparable Length",
                    description="Intro content length is reasonable compared to the source.",
                    status="pass",
                    score_impact=0
                ))

        # 4. Reference Check
        link_count = len(sw_data.get("references", []))
        details["external_links"] = link_count
        
        if link_count == 0:
            score -= 20
            signals.append(TrustSignal(
                id="no_refs",
                title="No External References",
                description="This article has no external links or citations usually required for verification.",
                status="fail",
                score_impact=-20
            ))
        elif link_count < 3:
            score -= 5
            signals.append(TrustSignal(
                id="low_refs",
                title="Few References",
                description="The article has very few external references.",
                status="warn",
                score_impact=-5
            ))
        else:
             signals.append(TrustSignal(
                id="good_refs",
                title="References Present",
                description=f"Found {link_count} external links/references.",
                status="pass",
                score_impact=0
            ))

        # 5. Language Diversity Check
        lang_count = lang_info.get("count", 0)
        if lang_count > 50:
            signals.append(TrustSignal(
                id="high_diversity",
                title="Global Topic",
                description=f"This topic is discussed in {lang_count} languages, suggesting high importance and cross-checkability.",
                status="pass",
                score_impact=5
            ))
            score += 5
        elif lang_count < 5:
             signals.append(TrustSignal(
                id="low_diversity",
                title="Limited Distribution",
                description="Topic available in very few languages. Harder to verify across neutral sources.",
                status="warn",
                score_impact=-5
            ))
             score -= 5

        # 6. Machine Translation Detection
        templates = sw_data.get("templates", [])
        machine_indicators = [
            "Tafsiri ya mashine", 
            "Machine translated", 
            "Tafsiri iliyosahihishwa", # Often used when machine translations are "touched up"
            "AI-generated content"
        ]
        is_machine = any(any(ind.lower() in t.lower() for ind in machine_indicators) for t in templates)
        
        if is_machine:
            score -= 50
            signals.append(TrustSignal(
                id="machine_translation",
                title="Machine Translation Detected",
                description="This article has been flagged with a machine translation template. These articles often require significant manual correction for semantic accuracy.",
                status="fail",
                score_impact=-50
            ))
        else:
            signals.append(TrustSignal(
                id="human_translation",
                title="Likely Human-Curated",
                description="No machine translation flags detected. The content structure suggests manual editing or verified translation.",
                status="pass",
                score_impact=0
            ))

        # Final Score Cap
        score = max(0, min(100, score))
        
        # Determine Summary
        if score >= 80:
            summary = "High Reliability. The article appears well-structured and consistent with its source."
        elif score >= 50:
            summary = "Medium Reliability. Some gaps in content or references were detected."
        else:
            summary = "Low Reliability. Significant issues with content length, references, or missing source links."

        return AnalysisResult(
            swahili_title=sw_title,
            english_title=en_title,
            trust_score=score,
            summary=summary,
            signals=signals,
            references=sw_data.get("references", []),
            internal_links=sw_data.get("internal_links", []),
            intro_text=sw_data.get("extract"),
            language_count=lang_count,
            swahili_exists=lang_info.get("sw_exists", False),
            jamii=sw_data.get("jamii", []),
            last_update=sw_data.get("last_update"),
            image_url=sw_data.get("image_url"),
            details=details
        )
