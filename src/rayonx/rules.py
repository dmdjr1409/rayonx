from dataclasses import dataclass
from enum import Enum
import re
from typing import Pattern


class IssueKind(str, Enum):
    TRIVIAL_COMMENT = "trivial_comment"
    AI_VERBOSITY = "ai_verbosity"
    AI_SIGNATURE = "ai_signature"
    GHOST_BLOCK = "ghost_block"
    MARKDOWN_SLOP = "markdown_slop"
    GOD_FILE = "god_file"


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
    Rule(
        code="RX109",
        kind=IssueKind.TRIVIAL_COMMENT,
        description="Commentaire trivial redondant en français",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(import(er)?\s+(tous\s+les\s+|les\s+)?(modules|librairies|bibliothèques|packages|dépendances)|"
            r"initialis(er|ation)\s+(des\s+|les\s+|de\s+la\s+|l')?(variables?|état|constantes?|données|valeurs?)|"
            r"retourn(er|e)\s+(le\s+|la\s+|les\s+)?(résultats?|réponse|valeur|données|vrai|faux)|"
            r"boucl(er|e)\s+(sur|à\s+travers)|parcour(ir|t)\s+(chaque|la\s+liste|le\s+tableau)|"
            r"pour\s+chaque\s+(élément|item|ligne|entrée)|"
            r"gér(er|e)\s+(les?\s+)?(erreurs?|exceptions?)|"
            r"exécut(er|ion)\s+du\s+script|point\s+d'entrée|fonction\s+principale|"
            r"fin\s+de\s+(fichier|classe|fonction|module))\b",
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
    Rule(
        code="RX204",
        kind=IssueKind.AI_VERBOSITY,
        description="Résidu de conversation ou verbiage d'IA en français",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(voici\s+(le\s+code|la\s+solution|l'implémentation|le\s+script|la\s+mise\s+à\s+jour)|"
            r"en\s+tant\s+que\s+modèle\s+d'ia|"
            r"afin\s+d'assurer\s+une\s+(exécution|gestion)\s+robuste|"
            r"n'hésitez\s+pas\s+à\s+personnaliser|"
            r"cette\s+fonction\s+permet\s+d'optimiser\s+et\s+d'assurer)\b",
            re.IGNORECASE,
        ),
        is_removable=True,
    ),
]

AI_SIGNATURE_RULES: list[Rule] = [
    Rule(
        code="RX205",
        kind=IssueKind.AI_SIGNATURE,
        description="Explicit AI assistant watermark or tool signature in comments",
        pattern=re.compile(
            r"^\s*(#|//|/\*)\s*(co-authored-by:\s*(claude|codex|chatgpt|copilot|cursor|anthropic|openai)|"
            r"(generated|fixed|patched|created|written)\s+by\s+(claude|codex|chatgpt|copilot|cursor|ai|gpt)|"
            r"(généré|corrigé|créé|modifié|écrit)\s+par\s+(claude|codex|chatgpt|copilot|cursor|ia)|"
            r"(prompt|instruction|demande\s+utilisateur)\s*:\s+)\b",
            re.IGNORECASE,
        ),
        is_removable=True,
    ),
    Rule(
        code="RX206",
        kind=IssueKind.AI_SIGNATURE,
        description="AI assistant identity or email marker in source code",
        pattern=re.compile(
            r"(apiCaller\s*:\s*[\"'](CODEX|CLAUDE|CHATGPT)[^\"']*[\"']|"
            r"Co-Authored-By:\s*(Claude|Codex|ChatGPT|Copilot|Cursor)\b|"
            r"noreply@(anthropic|openai)\.com)",
            re.IGNORECASE,
        ),
        is_removable=False,
    ),
]

MARKDOWN_SLOP_RULES: list[Rule] = [
    Rule(
        code="RX301",
        kind=IssueKind.MARKDOWN_SLOP,
        description="Generic AI marketing introduction",
        pattern=re.compile(
            r"\b(in\s+today's\s+(fast-paced|rapidly\s+evolving)\s+digital\s+world|"
            r"dans\s+le\s+monde\s+numérique\s+actuel\s+en\s+constante\s+évolution|"
            r"welcome\s+to\s+the\s+ultimate\s+guide|"
            r"bienvenue\s+dans\s+le\s+guide\s+ultime|"
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
            r"insérez\s+votre\s+clé\s+api\s+ici|"
            r"replace\s+this\s+with\s+your|your-api-key-here|TODO:\s*add\s+description)\b",
            re.IGNORECASE,
        ),
        is_removable=False,
    ),
]

GOD_FILE_THRESHOLD_LINES = 1500

GOD_FILE_RULE = Rule(
    code="RX401",
    kind=IssueKind.GOD_FILE,
    description="God File: Monster single-file stacking typical of repeated AI edits (> 1,500 lines)",
    pattern=re.compile(r"$^"),
    is_removable=False,
)
