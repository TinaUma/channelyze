import json
import os
import re
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

EXPORT_FILE = Path("ChatExport_2026-05-25/result.json")
OUTPUT_FILE = Path("output/services.json")
MODEL = "claude-haiku-4-5-20251001"

# All 18 service post IDs — forced inclusion regardless of markers
SERVICE_POST_IDS = [
    41,
    45,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    84,
    85,
    165,
    170,
    171,
    178,
    179,
    185,
    194,
    195,
    197,
    199,
]

# Multi-post services: these posts describe one service and must be concatenated
MULTI_POST_GROUPS = [
    [84, 85],
    [170, 171],
    [178, 179],
    [194, 195],
]

REQUIRED_CATEGORIES = {
    "Самопознание",
    "Отношения и партнёрство",
    "Карма и судьба",
    "Прогнозы и навигация",
    "Особые запросы",
}

EXTRACTION_PROMPT = """\
Ты — ассистент-аналитик астрологических услуг. Из текста поста Telegram-канала \
"AIстрология" извлеки информацию об одной услуге.

Верни JSON-объект с полями:
- name: название услуги (строка)
- description: краткое описание, 2-3 предложения (строка)
- price: цена в рублях (число или null, если не указана)
- duration: срок выполнения (строка или null)
- format: формат работы — одно из: "письменный", "голосовой", "онлайн", "смешанный", или null
- target_audience: для кого эта услуга (строка)
- category: одна из категорий: \
"Самопознание", "Отношения и партнёрство", "Карма и судьба", \
"Прогнозы и навигация", "Особые запросы"

Отвечай ТОЛЬКО валидным JSON без markdown-блоков и пояснений.

Текст поста:
{text}"""

TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "j",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    " ": "-",
    "«": "",
    "»": "",
    '"': "",
    "'": "",
    "/": "-",
    "(": "",
    ")": "",
    ":": "",
    ",": "",
    ".": "",
}


def slugify(name: str) -> str:
    result = name.lower()
    for ru, en in TRANSLIT.items():
        result = result.replace(ru, en)
    result = re.sub(r"[^a-z0-9\-]", "", result)
    return re.sub(r"-+", "-", result).strip("-")


def extract_text(message: dict) -> str:
    text = message.get("text", "")
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        parts = []
        for item in text:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(item.get("text", ""))
        return "".join(parts)
    return ""


def load_messages() -> dict[int, dict]:
    with open(EXPORT_FILE, encoding="utf-8") as f:
        data = json.load(f)
    messages: dict[int, dict] = {}
    for msg in data.get("messages", []):
        if msg.get("type") == "message":
            msg_id = msg.get("id")
            if msg_id and extract_text(msg).strip():
                messages[msg_id] = msg
    return messages


def build_groups(messages: dict[int, dict]) -> list[dict]:
    multi_ids = {pid for group in MULTI_POST_GROUPS for pid in group}
    groups: list[dict] = []

    for group_ids in MULTI_POST_GROUPS:
        texts = [extract_text(messages[pid]) for pid in group_ids if pid in messages]
        if texts:
            groups.append(
                {"source_post_ids": group_ids, "text": "\n\n---\n\n".join(texts)}
            )

    for pid in SERVICE_POST_IDS:
        if pid not in multi_ids and pid in messages:
            groups.append(
                {"source_post_ids": [pid], "text": extract_text(messages[pid])}
            )

    return groups


def call_claude(client: Anthropic, group: dict) -> dict | None:
    prompt = EXTRACTION_PROMPT.format(text=group["text"])
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [ERR] JSON parse error: {e}\n  Raw: {raw[:300]}")
        return None
    data["id"] = slugify(data.get("name", f"service-{group['source_post_ids'][0]}"))
    data["source_post_ids"] = group["source_post_ids"]
    return data


def validate(services: list[dict]) -> list[str]:
    """Returns warnings (non-blocking). File is saved regardless; fix manually in services.json."""
    warnings: list[str] = []
    if len(services) < 17:
        warnings.append(f"Получено {len(services)} услуг, ожидается минимум 17")
    found_cats = {s.get("category") for s in services}
    missing = REQUIRED_CATEGORIES - found_cats
    if missing:
        warnings.append(
            f"Категории не присвоены Claude: {', '.join(sorted(missing))} — исправь вручную в services.json"
        )
    return warnings


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY не задан в окружении или .env")
        sys.exit(1)

    print(f"Читаем {EXPORT_FILE}...")
    messages = load_messages()
    print(f"Загружено {len(messages)} сообщений с текстом")

    missing = [pid for pid in SERVICE_POST_IDS if pid not in messages]
    if missing:
        print(f"WARNING: посты не найдены в экспорте: {missing}")

    groups = build_groups(messages)
    print(f"Сформировано {len(groups)} групп для обработки\n")

    client = Anthropic(api_key=api_key)
    services: list[dict] = []

    for i, group in enumerate(groups, 1):
        print(f"[{i}/{len(groups)}] посты {group['source_post_ids']}...")
        service = call_claude(client, group)
        if service:
            services.append(service)
            price = service.get("price")
            price_str = f"{price} rub" if price else "-"
            print(f"  >> {service.get('name')} [{service.get('category')}] {price_str}")
        else:
            print(f"  >> ПРОПУЩЕНО")

    warnings = validate(services)
    if warnings:
        print("\nWARNINGS (исправь вручную в services.json):")
        for w in warnings:
            print(f"  - {w}")

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! {len(services)} услуг -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
