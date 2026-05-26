import json
import sys
from pathlib import Path

SERVICES_FILE = Path("output/services.json")
OUTPUT_HTML = Path("output/price.html")
OUTPUT_PDF = Path("output/price.pdf")

CATEGORY_ORDER = [
    "Самопознание",
    "Отношения и партнёрство",
    "Карма и судьба",
    "Прогнозы и навигация",
    "Особые запросы",
]

CATEGORY_COLORS = {
    "Самопознание": "#7B52B8",
    "Отношения и партнёрство": "#5B6DAE",
    "Карма и судьба": "#3D4A8F",
    "Прогнозы и навигация": "#6B3FA0",
    "Особые запросы": "#9B4E8A",
}

CATEGORY_ICONS = {
    "Самопознание": "✦",
    "Отношения и партнёрство": "❋",
    "Карма и судьба": "◈",
    "Прогнозы и навигация": "◎",
    "Особые запросы": "✧",
}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Прайс-лист — AIстрология</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Montserrat', sans-serif;
    background: #F5F0FF;
    color: #2D1F4E;
    padding: 40px 24px;
  }}

  .page-header {{
    text-align: center;
    margin-bottom: 56px;
  }}

  .page-header .channel {{
    font-size: 13px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #9B89CC;
    margin-bottom: 10px;
  }}

  .page-header h1 {{
    font-size: 32px;
    font-weight: 700;
    color: #5B2D8E;
    margin-bottom: 12px;
  }}

  .page-header .subtitle {{
    font-size: 15px;
    font-weight: 300;
    color: #6B5A8A;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.6;
  }}

  .category-section {{
    margin-bottom: 48px;
  }}

  .category-header {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid;
  }}

  .category-num {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.5;
  }}

  .category-icon {{
    font-size: 18px;
  }}

  .category-title {{
    font-size: 20px;
    font-weight: 700;
  }}

  .cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 16px;
  }}

  .card {{
    background: #fff;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(91, 45, 142, 0.08);
    border: 1px solid rgba(91, 45, 142, 0.1);
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}

  .card-name {{
    font-size: 16px;
    font-weight: 700;
    color: #2D1F4E;
    line-height: 1.3;
  }}

  .card-desc {{
    font-size: 13px;
    font-weight: 300;
    color: #5A4B72;
    line-height: 1.65;
    flex: 1;
  }}

  .card-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
  }}

  .badge {{
    font-size: 12px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    white-space: nowrap;
  }}

  .badge-price {{
    background: #5B2D8E;
    color: #fff;
  }}

  .badge-price-empty {{
    background: #EDE6FF;
    color: #5B2D8E;
  }}

  .badge-duration {{
    background: #F0EBF9;
    color: #5B2D8E;
  }}

  .how-to-order {{
    background: #fff;
    border-radius: 16px;
    padding: 36px 40px;
    box-shadow: 0 2px 16px rgba(91, 45, 142, 0.10);
    border: 1px solid rgba(91, 45, 142, 0.12);
    margin-top: 56px;
    max-width: 640px;
    margin-left: auto;
    margin-right: auto;
    text-align: center;
  }}

  .how-to-order h2 {{
    font-size: 22px;
    font-weight: 700;
    color: #5B2D8E;
    margin-bottom: 24px;
  }}

  .steps {{
    display: flex;
    flex-direction: column;
    gap: 14px;
    text-align: left;
    margin-bottom: 28px;
  }}

  .step {{
    display: flex;
    align-items: flex-start;
    gap: 14px;
  }}

  .step-num {{
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #5B2D8E;
    color: #fff;
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .step-text {{
    font-size: 14px;
    font-weight: 400;
    color: #3D2A60;
    line-height: 1.55;
    padding-top: 4px;
  }}

  .contacts {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-top: 4px;
  }}

  .contact-line {{
    font-size: 14px;
    font-weight: 600;
    color: #5B2D8E;
  }}

  .footer {{
    text-align: center;
    margin-top: 40px;
    font-size: 12px;
    color: #9B89CC;
    letter-spacing: 0.05em;
  }}

  @media print, (max-width: 600px) {{
    body {{ padding: 24px 16px; }}
    .cards-grid {{ grid-template-columns: 1fr; }}
    .how-to-order {{ padding: 28px 24px; }}
  }}
</style>
</head>
<body>

<header class="page-header">
  <p class="channel">Telegram-канал</p>
  <h1>AIстрология</h1>
  <p class="subtitle">Астрология и нумерология: разборы натальных карт, прогнозы, кармические аудиты и синастрии — письменно, глубоко, без шаблонов.</p>
</header>

{categories_html}

<section class="how-to-order">
  <h2>Как заказать</h2>
  <div class="steps">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-text">Напишите мне в Telegram — выберите услугу и обсудим детали.</div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-text">Отправьте данные: дата, время и место рождения (для астрологического разбора).</div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-text">Внесите предоплату 50% — реквизиты пришлю в личных сообщениях.</div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-text">Получите готовый разбор в оговорённые сроки после полной оплаты.</div>
    </div>
  </div>
  <div class="contacts">
    <span class="contact-line">Telegram: @tina_yuma</span>
    <span class="contact-line">Email: gooz@mail.ru</span>
  </div>
</section>

<footer class="footer">
  AIстрология · @tina_yuma
</footer>

</body>
</html>
"""

CATEGORY_SECTION_TEMPLATE = """\
<section class="category-section">
  <div class="category-header" style="border-color: {color}; color: {color};">
    <span class="category-num">{num:02d}</span>
    <span class="category-icon">{icon}</span>
    <span class="category-title">{title}</span>
  </div>
  <div class="cards-grid">
    {cards}
  </div>
</section>
"""

CARD_TEMPLATE = """\
<div class="card">
  <div class="card-name">{name}</div>
  <div class="card-desc">{description}</div>
  <div class="card-meta">
    {price_badge}
    {duration_badge}
  </div>
</div>
"""


def format_price(price) -> str:
    if price is None:
        return '<span class="badge badge-price-empty">по запросу</span>'
    return f'<span class="badge badge-price">{price:,} ₽</span>'.replace(",", " ")


def format_duration(duration) -> str:
    if not duration:
        return ""
    return f'<span class="badge badge-duration">{duration}</span>'


def build_card(service: dict) -> str:
    return CARD_TEMPLATE.format(
        name=service.get("name", ""),
        description=service.get("description", ""),
        price_badge=format_price(service.get("price")),
        duration_badge=format_duration(service.get("duration")),
    )


def build_categories_html(services: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {cat: [] for cat in CATEGORY_ORDER}
    for s in services:
        cat = s.get("category", "")
        if cat in grouped:
            grouped[cat].append(s)
        else:
            grouped.setdefault(cat, []).append(s)

    sections = []
    for i, cat in enumerate(CATEGORY_ORDER, 1):
        items = grouped.get(cat, [])
        if not items:
            continue
        cards_html = "\n    ".join(build_card(s) for s in items)
        sections.append(
            CATEGORY_SECTION_TEMPLATE.format(
                num=i,
                icon=CATEGORY_ICONS.get(cat, "✦"),
                title=cat,
                color=CATEGORY_COLORS.get(cat, "#5B2D8E"),
                cards=cards_html,
            )
        )
    return "\n".join(sections)


def generate_html(services: list[dict]) -> str:
    return HTML_TEMPLATE.format(categories_html=build_categories_html(services))


def generate_pdf(html_path: Path, pdf_path: Path) -> None:
    # Try WeasyPrint first, fall back to xhtml2pdf (pure Python, no system libs)
    try:
        from weasyprint import HTML

        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        print(f"PDF -> {pdf_path} (WeasyPrint)")
        return
    except Exception:
        pass

    try:
        from xhtml2pdf import pisa

        with open(html_path, encoding="utf-8") as src, open(pdf_path, "wb") as dst:
            result = pisa.CreatePDF(src.read(), dest=dst, encoding="utf-8")
        if result.err:
            print(f"PDF ошибка xhtml2pdf: {result.err}")
        else:
            print(f"PDF -> {pdf_path} (xhtml2pdf)")
    except ImportError:
        print("PDF пропущен: pip install weasyprint или pip install xhtml2pdf")


def main() -> None:
    if not SERVICES_FILE.exists():
        print(f"ERROR: {SERVICES_FILE} не найден. Сначала запусти parse.py.")
        sys.exit(1)

    with open(SERVICES_FILE, encoding="utf-8") as f:
        services = json.load(f)

    print(f"Загружено {len(services)} услуг из {SERVICES_FILE}")

    html = generate_html(services)
    OUTPUT_HTML.parent.mkdir(exist_ok=True)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"HTML -> {OUTPUT_HTML}")

    generate_pdf(OUTPUT_HTML, OUTPUT_PDF)
    print("Готово!")


if __name__ == "__main__":
    main()
