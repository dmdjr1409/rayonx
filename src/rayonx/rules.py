from dataclasses import dataclass
from enum import Enum
import re
from typing import Pattern


class IssueKind(str, Enum):
    TRIVIAL_COMMENT = "trivial_comment"
    AI_VERBOSITY = "ai_verbosity"
    GHOST_BLOCK = "ghost_block"
    MARKDOWN_SLOP = "markdown_slop"


@dataclass(frozen=True)
class Rule:
    code: str
    kind: IssueKind
    description: str
    pattern: Pattern[str]
    is_removable: bool = True


TRIVIAL_COMMENT_RULES: list[Rule] = [
    Rule(
        code="RX101",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant import comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(import\s+(all\s+)?(libraries|modules|packages|dependencies)|dependencies|imports)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX102",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant variable initialization comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(initialize|init|setup|define|declare)\s+(the\s+)?(variables?|state|constants?|values?)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX103",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant return statement comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*return\s+(the\s+)?(result|response|value|output|data|true|false)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX104",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant loop explanation comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(loop\s+(through|over)|iterate\s+(over|through)|for\s+each\s+(item|element|row))\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX105",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant conditional statement comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*check\s+if\s+.*(is\s+none|is\s+null|exists|is\s+valid|matches|empty)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX106",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant error handling comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(handle|catch|log|print)\s+(the\s+)?(errors?|exceptions?|failures?)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX107",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant EOF or section marker comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(end\s+of\s+(file|class|function|module|script)|---+\s*end)\b",
            re.IGNORECASE,
        ),
    ),
    Rule(
        code="RX108",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Redundant main function / entry point comment",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(main\s+(function|entry\s*point|execution)|entrypoint|run\s+the\s+script)\b",
            re.IGNORECASE,
        ),
    ),
]

AI_VERBOSITY_RULES: list[Rule] = [
    Rule(
        code="RX201",
        kind=IssueKind.AI_VERBOSITY,
        description="Hallmark LLM buzzword / filler phrasing",
        pattern=re.compile(
            r"\b(this\s+(function|method|class|module)\s+leverages|"
            r"delve\s+into|"
            r"in\s+order\s+to\s+ensure\s+robust|"
            r"robust\s+and\s+scalable\s+solution|"
            r"seamlessly\s+integrates?|"
            r"as\s+an\s+ai\s+(language\s+)?model|"
            r"note\s+that\s+this\s+implementation\s+assumes|"
            r"feel\s+free\s+to\s+customize)\b",
            re.IGNORECASE,
        ),
        is_removable=False,
    ),
    Rule(
        code="RX202",
        kind=IssueKind.AI_VERBOSITY,
        description="Chat conversational residue left in source code",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(here\s+is\s+(the\s+)?(code|implementation|solution|updated\s+code)|sure[,!]|certainly[!.]|i\s+have\s+modified)\b",
            re.IGNORECASE,
        ),
        is_removable=True,
    ),
]

MARKDOWN_SLOP_RULES: list[Rule] = [
    Rule(
        code="RX301",
        kind=IssueKind.MARKDOWN_SLOP,
        description="Generic AI marketing introduction",
        pattern=re.compile(
            r"\b(in\s+today's\s+(fast-paced|rapidly\s+evolving)\s+digital\s+world|"
            r"welcome\s+to\s+the\s+ultimate\s+guide|"
            r"dive\s+deep\s+into\s+the\s+world\s+of)\b",
            re.IGNORECASE,
        ),
        is_removable=False,
    ),
    Rule(
        code="RX302",
        kind=IssueKind.MARKDOWN_SLOP,
        description="Unfilled AI template placeholder",
        pattern=re.compile(
            r"\b(insert\s+your\s+(api\s+key|token|username|repo)\s+here|"
            r"replace\s+this\s+with\s+your|your-api-key-here|TODO:\s*add\s+description)\b",
            re.IGNORECASE,
        ),
        is_removable=False,
    ),
]
