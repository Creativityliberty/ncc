from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from ncc.schemas import (
    RedactionFinding,
    QualityGateResult,
    DatasetQualityExampleResult,
    DatasetQualityReport,
)


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?<![\d.])(?:\+|00)?\d{1,3}?[\s.-]?(?:\(?\d{2,4}\)?[\s.-]?){2,4}\d{2,4}(?![\d.])"
)
URL_RE = re.compile(r"https?://[^\s\"']+")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$"
)

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FIELD_PATHS_TO_SKIP_REDACTION = [
    ".timestamp",
]

def looks_like_phone(match_value: str) -> bool:
    digits = re.sub(r"\D", "", match_value)

    if len(digits) < 8:
        return False

    if ISO_DATE_RE.match(match_value):
        return False

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", match_value):
        return False

    if re.fullmatch(r"\d+\.\d+", match_value):
        return False

    return True

SECRET_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{16,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[:=]\s*[^\s\"']+"),
]

DESTRUCTIVE_TERMS = [
    "supprime",
    "supprimer",
    "efface",
    "effacer",
    "delete",
    "remove",
    "rm -rf",
    "wipe",
    "destroy",
    "vider",
    "vide automatiquement",
]

REDACTION_REPLACEMENTS = {
    "email": "[REDACTED_EMAIL]",
    "phone": "[REDACTED_PHONE]",
    "url": "[REDACTED_URL]",
    "ip": "[REDACTED_IP]",
    "secret": "[REDACTED_SECRET]",
}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _preview(value: str, max_len: int = 80) -> str:
    value = value.replace("\n", " ")
    return value[:max_len]


def should_skip_redaction(value: str, field_path: str) -> bool:
    if any(field_path.endswith(path) for path in FIELD_PATHS_TO_SKIP_REDACTION):
        return True

    if ISO_TIMESTAMP_RE.match(value):
        return True

    if ISO_DATE_RE.match(value):
        return True

    return False


def redact_phone_values(redacted: str, field_path: str) -> tuple[str, list[RedactionFinding]]:
    findings: list[RedactionFinding] = []

    def repl(match: re.Match) -> str:
        value = match.group(0)

        if not looks_like_phone(value):
            return value

        findings.append(
            RedactionFinding(
                field_path=field_path,
                finding_type="phone",
                original_preview=_preview(value),
                replacement=REDACTION_REPLACEMENTS["phone"],
            )
        )
        return REDACTION_REPLACEMENTS["phone"]

    return PHONE_RE.sub(repl, redacted), findings


def redact_string(value: str, field_path: str) -> tuple[str, list[RedactionFinding]]:
    if should_skip_redaction(value, field_path):
        return value, []

    findings: list[RedactionFinding] = []
    redacted = value

    redacted, phone_findings = redact_phone_values(redacted, field_path)
    findings.extend(phone_findings)

    patterns = [
        ("email", EMAIL_RE),
        ("url", URL_RE),
        ("ip", IP_RE),
    ]

    for finding_type, pattern in patterns:
        matches = list(pattern.finditer(redacted))
        for match in matches:
            findings.append(
                RedactionFinding(
                    field_path=field_path,
                    finding_type=finding_type,
                    original_preview=_preview(match.group(0)),
                    replacement=REDACTION_REPLACEMENTS[finding_type],
                )
            )

        redacted = pattern.sub(REDACTION_REPLACEMENTS[finding_type], redacted)

    for pattern in SECRET_PATTERNS:
        matches = list(pattern.finditer(redacted))
        for match in matches:
            findings.append(
                RedactionFinding(
                    field_path=field_path,
                    finding_type="secret",
                    original_preview=_preview(match.group(0)),
                    replacement=REDACTION_REPLACEMENTS["secret"],
                )
            )

        redacted = pattern.sub(REDACTION_REPLACEMENTS["secret"], redacted)

    return redacted, findings


def redact_recursive(value: Any, field_path: str = "$") -> tuple[Any, list[RedactionFinding]]:
    findings: list[RedactionFinding] = []

    if isinstance(value, str):
        redacted, local_findings = redact_string(value, field_path)
        findings.extend(local_findings)
        return redacted, findings

    if isinstance(value, list):
        output = []
        for idx, item in enumerate(value):
            redacted_item, item_findings = redact_recursive(item, f"{field_path}[{idx}]")
            output.append(redacted_item)
            findings.extend(item_findings)
        return output, findings

    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            redacted_item, item_findings = redact_recursive(item, f"{field_path}.{key}")
            output[key] = redacted_item
            findings.extend(item_findings)
        return output, findings

    return value, findings


def contains_destructive_intent(example: dict[str, Any]) -> bool:
    text = json.dumps(example, ensure_ascii=False).lower()
    return any(term in text for term in DESTRUCTIVE_TERMS)


def action_is_unsafe(example: dict[str, Any]) -> bool:
    action = example.get("action", {}) or {}
    input_text = str(example.get("input", "")).lower()

    destructive_input = any(term in input_text for term in DESTRUCTIVE_TERMS)

    if destructive_input and action.get("allowed") is True:
        return True

    if action.get("kind") == "blocked" and action.get("allowed") is not False:
        return True

    return False


def layer_separation_is_clean(example: dict[str, Any]) -> bool:
    knowledge_text = json.dumps(example.get("knowledge_records", []), ensure_ascii=False).lower()
    policy_text = " ".join(example.get("learned_policy_rules", []) or []).lower()

    if "destructive_actions_require_backup_and_confirmation" in knowledge_text:
        return False

    if "coala organise les agents de langage" in policy_text:
        return False

    return True


def required_fields_are_present(example: dict[str, Any]) -> bool:
    required = [
        "dataset_version",
        "source",
        "input",
        "observation",
        "intent",
        "gap",
        "stable_output",
        "reasoning",
        "action",
        "labels",
        "target",
    ]

    return all(field in example for field in required)


def target_is_complete(example: dict[str, Any]) -> bool:
    target = example.get("target", {}) or {}

    required = [
        "intent",
        "gap",
        "stable_output",
        "action",
        "state_after_summary",
    ]

    return all(bool(target.get(field)) for field in required)


def quality_gate(example: dict[str, Any], redactions: list[RedactionFinding]) -> QualityGateResult:
    flags: list[str] = []
    reasons: list[str] = []

    if not required_fields_are_present(example):
        flags.append("missing_required_fields")
        reasons.append("L’exemple ne contient pas tous les champs cognitifs requis.")

    if not str(example.get("input", "")).strip():
        flags.append("empty_input")
        reasons.append("L’entrée utilisateur est vide.")

    if not target_is_complete(example):
        flags.append("incomplete_target")
        reasons.append("Le target cognitif est incomplet.")

    if action_is_unsafe(example):
        flags.append("unsafe_action")
        reasons.append("Action destructive autorisée ou blocage incohérent.")

    if not layer_separation_is_clean(example):
        flags.append("layer_separation_violation")
        reasons.append("Mélange détecté entre knowledge_records et policy rules.")

    if redactions:
        flags.append("redacted_sensitive_content")
        reasons.append("Contenu sensible détecté et masqué.")

    score = 1.0

    penalties = {
        "missing_required_fields": 0.4,
        "empty_input": 0.4,
        "incomplete_target": 0.25,
        "unsafe_action": 0.5,
        "layer_separation_violation": 0.4,
        "redacted_sensitive_content": 0.05,
    }

    for flag in flags:
        score -= penalties.get(flag, 0.1)

    score = max(round(score, 3), 0.0)

    hard_fail_flags = {
        "missing_required_fields",
        "empty_input",
        "unsafe_action",
        "layer_separation_violation",
    }

    passed = score >= 0.75 and not any(flag in hard_fail_flags for flag in flags)

    return QualityGateResult(
        passed=passed,
        score=score,
        flags=flags,
        reasons=reasons,
    )


def process_dataset(
    input_path: Path,
    clean_path: Path,
    rejected_path: Path,
    redaction_log_path: Path,
) -> DatasetQualityReport:
    raw_examples = read_jsonl(input_path)

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    redaction_log: list[dict[str, Any]] = []

    example_results: list[DatasetQualityExampleResult] = []

    for example in raw_examples:
        original = deepcopy(example)
        redacted_example, redactions = redact_recursive(original)

        gate = quality_gate(redacted_example, redactions)

        result = DatasetQualityExampleResult(
            source=redacted_example.get("source", {}),
            input_preview=_preview(str(redacted_example.get("input", ""))),
            passed=gate.passed,
            score=gate.score,
            flags=gate.flags,
            reasons=gate.reasons,
            redactions=redactions,
        )

        example_results.append(result)

        if redactions:
            for finding in redactions:
                redaction_log.append({
                    "source": redacted_example.get("source", {}),
                    "field_path": finding.field_path,
                    "finding_type": finding.finding_type,
                    "original_preview": finding.original_preview,
                    "replacement": finding.replacement,
                })

        if gate.passed:
            accepted.append(redacted_example)
        else:
            rejected.append({
                "example": redacted_example,
                "quality": result.model_dump(),
            })

    write_jsonl(clean_path, accepted)
    write_jsonl(rejected_path, rejected)
    write_jsonl(redaction_log_path, redaction_log)

    input_count = len(raw_examples)
    accepted_count = len(accepted)
    rejected_count = len(rejected)

    scores = [result.score for result in example_results]
    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    redacted_findings = len(redaction_log)
    pii_findings = sum(1 for item in redaction_log if item["finding_type"] in {"email", "phone", "url", "ip"})
    secret_findings = sum(1 for item in redaction_log if item["finding_type"] == "secret")

    unsafe_action_findings = sum(
        1 for result in example_results if "unsafe_action" in result.flags
    )

    malformed_examples = sum(
        1 for result in example_results if "missing_required_fields" in result.flags
    )

    return DatasetQualityReport(
        input_examples=input_count,
        accepted_examples=accepted_count,
        rejected_examples=rejected_count,
        pass_rate=round(accepted_count / input_count, 3) if input_count else 0.0,
        average_quality_score=avg_score,
        redacted_findings=redacted_findings,
        pii_findings=pii_findings,
        secret_findings=secret_findings,
        unsafe_action_findings=unsafe_action_findings,
        malformed_examples=malformed_examples,
        output_files=[
            str(clean_path),
            str(rejected_path),
            str(redaction_log_path),
        ],
    )


def write_quality_report_json(report: DatasetQualityReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
