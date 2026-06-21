from __future__ import annotations

import re

from app.config import AppConfig
from app.evaluation.model_benchmark import infer_question_category
from app.models import QuestionItem


RETRIEVAL_CATEGORIES = {
    "economics_finance",
    "computer_science",
    "science",
    "biology_environment",
    "history_geography",
    "general_knowledge",
    "law",
    "law_safety",
}


class RetrievalGate:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def should_retrieve(self, question: QuestionItem) -> bool:
        if self.config.retrieval_mode != "on":
            return False

        category = question.category or infer_question_category(question.question, question.choices)
        if category not in RETRIEVAL_CATEGORIES:
            return False

        normalized = question.question.lower()
        if len(normalized) < 35:
            return False

        if re.fullmatch(r"[\d\s+\-*/().,=]+", question.question.strip()):
            return False

        if re.search(r"\b\d+\s*[\+\-\*/]\s*\d+\b", normalized):
            return False

        numeric_token_count = len(re.findall(r"\d+(?:[.,]\d+)?", normalized))
        if category in {"mathematics", "physics_engineering", "chemistry"}:
            return False
        if category == "economics_finance" and numeric_token_count >= 3:
            return False

        category_keywords = {
            "science": ("di truyền", "tế bào", "hệ sinh thái", "dna", "enzyme", "quang hợp", "tiến hóa"),
            "biology_environment": ("di truyền", "tế bào", "dna", "rna", "enzyme", "hệ sinh thái", "quang hợp"),
            "economics_finance": ("gdp", "lạm phát", "tỷ giá", "npv", "irr", "roe", "pe", "trái phiếu", "chi phí cơ hội", "độ co giãn"),
            "computer_science": ("thuật toán", "cấu trúc dữ liệu", "sql", "tcp/ip", "database", "acid"),
            "history_geography": ("thủ đô", "quốc gia", "hiệp ước", "chiến tranh", "châu lục", "vĩ độ", "kinh độ", "năm "),
            "general_knowledge": ("định nghĩa", "khái niệm", "thuật ngữ", "ai là", "cái nào", "sự kiện", "quốc gia", "thủ đô"),
            "law": ("theo quy định", "pháp luật", "điều ", "khoản ", "nghĩa vụ", "quyền", "hợp đồng", "tuân thủ"),
            "law_safety": ("theo quy định", "pháp luật", "điều ", "khoản ", "nghĩa vụ", "quyền", "hợp đồng", "tuân thủ"),
        }
        helpful_keywords = category_keywords.get(category, ())
        if any(keyword in normalized for keyword in helpful_keywords):
            return True

        global_factual_markers = (
            "định nghĩa",
            "khái niệm",
            "định luật",
            "nguyên lý",
            "là gì",
            "thủ đô",
            "quốc gia",
            "lịch sử",
            "di truyền",
            "bản quyền",
            "hợp đồng",
            "thuật toán",
        )
        return any(marker in normalized for marker in global_factual_markers)
