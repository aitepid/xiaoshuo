from __future__ import annotations

import re

from django.core.exceptions import ValidationError


PROHIBITED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"(?:色情|赌[博博]|毒品|暴力|违禁|走私|枪支|诈骗|代写|外挂)",
        r"(?:未成年人[\s\S]{0,12}(?:色情|裸露|性暗示))",
        r"(?:极端主义|恐怖主义|邪教|仇恨言论)",
    ]
]


def validate_content(value: str, field_name: str = "内容") -> None:
    if not value:
        return

    for pattern in PROHIBITED_PATTERNS:
        match = pattern.search(value)
        if match:
            raise ValidationError(f"{field_name} 含有违规词或敏感内容：{match.group(0)}")


def validate_text_fields(**fields: str) -> None:
    for field_name, value in fields.items():
        validate_content(value, field_name)