"""
generate_quiz.py — читает output/services.json, генерирует output/quiz/index.html.
Тест: 3 блока (Контекст, Намерение, Формат), scoring → рекомендация услуги.
Чистый HTML + CSS + Vanilla JS, деплоится на GitHub Pages.
"""

import json
import sys
from pathlib import Path

SERVICES_FILE = Path("output/services.json")
OUTPUT_DIR = Path("output/quiz")
OUTPUT_HTML = OUTPUT_DIR / "index.html"

# Scoring weights: answer_key -> {service_id: score}
# Higher score = stronger match between this answer and this service
SCORING: dict[str, dict[str, int]] = {
    # Q1: Что сейчас происходит в вашей жизни?
    "q1_a": {  # Переломный момент, ищу ориентиры
        "trojnoj-portret": 3,
        "energeticheskij-portret": 2,
        "osnovnye-aspekty": 2,
        "rasshifrovka-solyara": 1,
        "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": 1,
    },
    "q1_b": {  # Сложности в отношениях
        "sinastriya": 3,
        "vedicheskaya-sinastriya-karmicheskij-kod-pary": 3,
        "astrologicheskij-audit-partnyorstva": 2,
        "mayak-spetsialnyj-paket": 2,
    },
    "q1_c": {  # Хожу по кругу, старые сценарии
        "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": 3,
        "astro-detoks-rasputyvanie-vetvej-sudby": 3,
        "negordiev-uzel": 2,
        "karmicheskij-audit": 2,
    },
    "q1_d": {  # Хочу понять, что меня ждёт
        "rasshifrovka-solyara": 3,
        "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": 3,
        "trojnoj-portret": 1,
        "razbor-natalnoj-karty": 1,
    },
    "q1_e": {  # Особая ситуация (ребёнок или питомец)
        "razbor-natalnoj-karty-rebyonka": 3,
        "karma-lap": 3,
    },
    # Q2: Какая сфера требует внимания?
    "q2_a": {  # Моя личность и путь
        "trojnoj-portret": 2,
        "energeticheskij-portret": 2,
        "razbor-natalnoj-karty": 2,
        "osnovnye-aspekty": 1,
    },
    "q2_b": {  # Любовь и партнёрство
        "sinastriya": 2,
        "vedicheskaya-sinastriya-karmicheskij-kod-pary": 2,
        "mayak-spetsialnyj-paket": 1,
        "astrologicheskij-audit-partnyorstva": 1,
    },
    "q2_c": {  # Прошлое, карма
        "karmicheskij-audit": 2,
        "negordiev-uzel": 2,
        "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": 2,
        "astro-detoks-rasputyvanie-vetvej-sudby": 1,
    },
    "q2_d": {  # Будущее и планы
        "rasshifrovka-solyara": 2,
        "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": 2,
    },
    # Q3: Что беспокоит прямо сейчас?
    "q3_a": {  # Не понимаю себя и своих реакций
        "trojnoj-portret": 2,
        "energeticheskij-portret": 2,
        "razbor-natalnoj-karty": 1,
    },
    "q3_b": {  # Напряжение в отношениях
        "sinastriya": 2,
        "mayak-spetsialnyj-paket": 2,
        "vedicheskaya-sinastriya-karmicheskij-kod-pary": 1,
    },
    "q3_c": {  # Хожу по одним граблям
        "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": 2,
        "negordiev-uzel": 2,
        "karmicheskij-audit": 1,
        "astro-detoks-rasputyvanie-vetvej-sudby": 1,
    },
    "q3_d": {  # Не знаю какое решение принять
        "rasshifrovka-solyara": 2,
        "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": 2,
        "razbor-natalnoj-karty": 1,
    },
    # Q4: Зачем вы здесь? (Намерение)
    "q4_a": {  # Понять себя глубже
        "trojnoj-portret": 2,
        "energeticheskij-portret": 2,
        "razbor-natalnoj-karty": 1,
        "osnovnye-aspekty": 1,
    },
    "q4_b": {  # Получить прогноз / навигацию
        "rasshifrovka-solyara": 2,
        "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": 2,
    },
    "q4_c": {  # Разобраться в конкретной ситуации
        "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": 1,
        "sinastriya": 1,
        "astro-detoks-rasputyvanie-vetvej-sudby": 1,
        "astrologicheskij-audit-partnyorstva": 1,
    },
    "q4_d": {  # Найти точку опоры, ресурс
        "negordiev-uzel": 2,
        "karmicheskij-audit": 1,
        "trojnoj-portret": 1,
    },
    # Q5: Формат работы
    "q5_a": {  # Письменный разбор
        "trojnoj-portret": 1,
        "energeticheskij-portret": 1,
        "razbor-natalnoj-karty": 1,
        "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": 1,
        "rasshifrovka-solyara": 1,
    },
    "q5_b": {  # Живое общение, голос
        "karmicheskij-audit": 1,
        "mayak-spetsialnyj-paket": 1,
    },
    "q5_c": {  # Не важно — главное результат
        # neutral, no bias
    },
}

# Reason texts shown in the quiz result
REASONS: dict[str, str] = {
    "trojnoj-portret": "Ты в переломной точке и хочешь понять себя — три ключевых параметра карты дадут быстрый и точный ориентир.",
    "energeticheskij-portret": "Ты чувствуешь потерю сил и хочешь разобраться в своей энергии — этот разбор покажет где утечка и что делать.",
    "osnovnye-aspekty": "Ты хочешь получить глубокий разбор с ответами на конкретные вопросы — Основные Аспекты дают именно это.",
    "razbor-natalnoj-karty": "Ты готов(а) к полноценному погружению в свою натальную карту с кармическим разбором и ответами на вопросы.",
    "sinastriya": "Твоя главная тема — отношения. Синастрия покажет динамику пары через числа и натальные карты.",
    "vedicheskaya-sinastriya-karmicheskij-kod-pary": "Ты хочешь понять кармические основы ваших отношений — Ведическая синастрия раскрывает это на глубинном уровне.",
    "astrologicheskij-audit-partnyorstva": "Тебя интересует деловое партнёрство — этот аудит покажет совместимость ролей, решений и финансовых паттернов.",
    "mayak-spetsialnyj-paket": "Судя по ответам, тебе нужна помощь в выходе из тяжёлой ситуации в отношениях — Маяк создан именно для этого.",
    "karmicheskij-audit": "Ты чувствуешь груз прошлого — Кармический аудит поможет разобраться с 3 прошлыми жизнями и найти путь к свободе.",
    "negordiev-uzel": "Твои Лунные Узлы — ключ к пониманию повторяющихся сценариев. Этот разбор даст чёткие шаги к внутренней свободе.",
    "karta-urokov-astrologicheskij-analiz-povtoryayuschihsya-stsenariev": "Ты ходишь по кругу и хочешь разорвать паттерн — Карта Уроков покажет механику твоих ловушек и как их обойти.",
    "astro-detoks-rasputyvanie-vetvej-sudby": "Тебя преследуют мысли о непрожитых сценариях — этот разбор поможет понять закономерности и освободиться от них.",
    "rasshifrovka-solyara": "Ты хочешь понять год вперёд и синхронизироваться со своим циклом — Соляр даст точные даты и темы года.",
    "vedicheskij-slepok-tvoya-zvyozdnaya-zadacha": "Ты хочешь понять не только себя, но и кармическую траекторию — Ведический слепок раскрывает механику времени твоей жизни.",
    "razbor-natalnoj-karty-rebyonka": "Ты хочешь понять своего ребёнка глубже — разбор натальной карты покажет его потенциал, таланты и как их поддержать.",
    "karma-lap": "Твоя связь с питомцем — это кармическая история. Этот разбор поможет понять миссию животного в твоей жизни.",
}

QUESTIONS = [
    {
        "block": 1,
        "block_title": "Контекст",
        "id": "q1",
        "text": "Что сейчас происходит в вашей жизни?",
        "options": [
            {"key": "q1_a", "text": "Переломный момент — теряю ориентиры"},
            {"key": "q1_b", "text": "Сложности в отношениях или с партнёром"},
            {"key": "q1_c", "text": "Хожу по кругу — старые сценарии повторяются"},
            {"key": "q1_d", "text": "Хочу понять, что меня ждёт впереди"},
            {"key": "q1_e", "text": "Особая ситуация — с ребёнком или питомцем"},
        ],
    },
    {
        "block": 1,
        "block_title": "Контекст",
        "id": "q2",
        "text": "Какая сфера жизни требует внимания прямо сейчас?",
        "options": [
            {"key": "q2_a", "text": "Я сам(а) — личность, путь, самореализация"},
            {"key": "q2_b", "text": "Любовь, семья или деловое партнёрство"},
            {"key": "q2_c", "text": "Прошлое, родовые сценарии, карма"},
            {"key": "q2_d", "text": "Будущее — планы, важные решения"},
        ],
    },
    {
        "block": 1,
        "block_title": "Контекст",
        "id": "q3",
        "text": "Что беспокоит вас прямо сейчас больше всего?",
        "options": [
            {"key": "q3_a", "text": "Не понимаю себя, своих реакций и выборов"},
            {"key": "q3_b", "text": "Напряжение в отношениях или трудный выбор"},
            {"key": "q3_c", "text": "Снова наступаю на те же грабли"},
            {"key": "q3_d", "text": "Не знаю, какое решение принять"},
        ],
    },
    {
        "block": 2,
        "block_title": "Намерение",
        "id": "q4",
        "text": "Зачем вы здесь? Что важнее всего получить?",
        "options": [
            {"key": "q4_a", "text": "Понять себя глубже"},
            {"key": "q4_b", "text": "Получить прогноз или навигацию на будущее"},
            {"key": "q4_c", "text": "Разобраться в конкретной ситуации"},
            {"key": "q4_d", "text": "Найти точку опоры и внутренний ресурс"},
        ],
    },
    {
        "block": 3,
        "block_title": "Формат",
        "id": "q5",
        "text": "Как вам комфортнее работать?",
        "options": [
            {"key": "q5_a", "text": "Письменный разбор — читаю в своём темпе"},
            {"key": "q5_b", "text": "Живое общение, голос, диалог"},
            {"key": "q5_c", "text": "Не важно — главное результат"},
        ],
    },
]

HTML = """\
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Тест — AIстрология</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Montserrat', sans-serif;
    background: #F5F0FF;
    color: #2D1F4E;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 16px 60px;
  }}

  .quiz-wrap {{
    width: 100%;
    max-width: 640px;
  }}

  .quiz-header {{
    text-align: center;
    margin-bottom: 40px;
  }}

  .quiz-header .channel {{
    font-size: 12px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #9B89CC;
    margin-bottom: 8px;
  }}

  .quiz-header h1 {{
    font-size: 26px;
    font-weight: 700;
    color: #5B2D8E;
    margin-bottom: 10px;
  }}

  .quiz-header p {{
    font-size: 14px;
    font-weight: 300;
    color: #6B5A8A;
    line-height: 1.6;
  }}

  /* Progress bar */
  .progress-bar {{
    height: 4px;
    background: #E8DEFF;
    border-radius: 4px;
    margin-bottom: 32px;
    overflow: hidden;
  }}

  .progress-fill {{
    height: 100%;
    background: #5B2D8E;
    border-radius: 4px;
    transition: width 0.4s ease;
    width: 0%;
  }}

  /* Block label */
  .block-label {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #9B89CC;
    margin-bottom: 8px;
  }}

  /* Questions */
  .question {{
    display: none;
    animation: fadeIn 0.3s ease;
  }}

  .question.active {{ display: block; }}

  @keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}

  .question-text {{
    font-size: 20px;
    font-weight: 700;
    color: #2D1F4E;
    margin-bottom: 24px;
    line-height: 1.4;
  }}

  .options {{
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 32px;
  }}

  .option {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 20px;
    background: #fff;
    border: 2px solid transparent;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 15px;
    font-weight: 400;
    color: #3D2A60;
    text-align: left;
    box-shadow: 0 1px 6px rgba(91,45,142,0.06);
  }}

  .option:hover {{
    border-color: #C4ABEE;
    background: #FAF7FF;
  }}

  .option.selected {{
    border-color: #5B2D8E;
    background: #F0E8FF;
    color: #5B2D8E;
    font-weight: 600;
  }}

  .option-dot {{
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 2px solid #C4ABEE;
    transition: all 0.2s;
    position: relative;
  }}

  .option.selected .option-dot {{
    border-color: #5B2D8E;
    background: #5B2D8E;
  }}

  .option.selected .option-dot::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #fff;
  }}

  /* Navigation */
  .nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }}

  .btn {{
    padding: 14px 28px;
    border-radius: 10px;
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
  }}

  .btn-back {{
    background: transparent;
    color: #9B89CC;
    border: 2px solid #E0D4F7;
  }}

  .btn-back:hover {{ background: #F0E8FF; }}

  .btn-next {{
    background: #5B2D8E;
    color: #fff;
    flex: 1;
    max-width: 260px;
    margin-left: auto;
  }}

  .btn-next:hover {{ background: #4A2475; }}
  .btn-next:disabled {{
    background: #C4ABEE;
    cursor: not-allowed;
  }}

  /* Result */
  .result {{
    display: none;
    animation: fadeIn 0.4s ease;
  }}

  .result.active {{ display: block; }}

  .result-card {{
    background: #fff;
    border-radius: 16px;
    padding: 36px 32px;
    box-shadow: 0 4px 24px rgba(91,45,142,0.12);
    border: 1px solid rgba(91,45,142,0.1);
    text-align: center;
    margin-bottom: 24px;
  }}

  .result-badge {{
    display: inline-block;
    background: #EDE6FF;
    color: #5B2D8E;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 16px;
    border-radius: 20px;
    margin-bottom: 16px;
  }}

  .result-name {{
    font-size: 24px;
    font-weight: 700;
    color: #2D1F4E;
    margin-bottom: 14px;
    line-height: 1.3;
  }}

  .result-desc {{
    font-size: 14px;
    font-weight: 300;
    color: #5A4B72;
    line-height: 1.7;
    margin-bottom: 20px;
  }}

  .result-why {{
    background: #F5F0FF;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 13px;
    font-weight: 400;
    color: #4A3A6A;
    line-height: 1.6;
    text-align: left;
    margin-bottom: 24px;
  }}

  .result-why strong {{
    color: #5B2D8E;
    font-weight: 600;
  }}

  .result-meta {{
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 28px;
  }}

  .result-meta .badge {{
    font-size: 13px;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 20px;
  }}

  .badge-price {{
    background: #5B2D8E;
    color: #fff;
  }}

  .badge-free {{
    background: #EDE6FF;
    color: #5B2D8E;
  }}

  .badge-duration {{
    background: #F0EBF9;
    color: #5B2D8E;
  }}

  .btn-order {{
    display: inline-block;
    padding: 16px 36px;
    background: #5B2D8E;
    color: #fff;
    border-radius: 12px;
    font-family: 'Montserrat', sans-serif;
    font-size: 15px;
    font-weight: 700;
    text-decoration: none;
    transition: background 0.2s;
  }}

  .btn-order:hover {{ background: #4A2475; }}

  .btn-clarify {{
    display: inline-block;
    margin-top: 12px;
    padding: 13px 28px;
    background: transparent;
    color: #5B2D8E;
    border: 2px solid #C4ABEE;
    border-radius: 12px;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.2s;
  }}

  .btn-clarify:hover {{
    background: #F0E8FF;
    border-color: #5B2D8E;
  }}

  .clarify-hint {{
    font-size: 12px;
    color: #9B89CC;
    margin-top: 10px;
    font-weight: 400;
  }}

  .result-actions {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }}

  .btn-retry {{
    display: block;
    margin: 20px auto 0;
    background: none;
    border: 2px solid #E0D4F7;
    color: #9B89CC;
    font-family: 'Montserrat', sans-serif;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 28px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
  }}

  .btn-retry:hover {{ background: #F0E8FF; color: #5B2D8E; }}

  .counter {{ color: #9B89CC; font-size: 14px; }}

  @media (max-width: 480px) {{
    .quiz-header h1 {{ font-size: 22px; }}
    .question-text {{ font-size: 17px; }}
    .option {{ padding: 14px 16px; font-size: 14px; }}
    .result-card {{ padding: 28px 20px; }}
    .result-name {{ font-size: 20px; }}
  }}
</style>
</head>
<body>
<div class="quiz-wrap">
  <header class="quiz-header">
    <p class="channel">AIстрология</p>
    <h1>Найди свою услугу</h1>
    <p>5 вопросов — и вы узнаете, какой астрологический разбор подходит именно вам.</p>
  </header>

  <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>

  <div id="quiz-body">
    <!-- Questions inserted by JS -->
  </div>

  <div class="result" id="result">
    <div class="result-card" id="result-card">
      <!-- filled by JS -->
    </div>
    <button class="btn-retry" onclick="restart()">Пройти тест заново</button>
  </div>
</div>

<script>
const SERVICES = {services_json};
const SCORING = {scoring_json};
const REASONS = {reasons_json};

const QUESTIONS = {questions_json};

let answers = {{}};
let current = 0;

function buildQuizHTML() {{
  const body = document.getElementById('quiz-body');
  body.innerHTML = QUESTIONS.map((q, i) => `
    <div class="question ${{i === 0 ? 'active' : ''}}" id="q-${{i}}">
      <div class="block-label">Блок ${{q.block}} — ${{q.block_title}}</div>
      <div class="question-text">${{q.text}}</div>
      <div class="options">
        ${{q.options.map(o => `
          <button class="option" data-key="${{o.key}}" onclick="selectOption(this, '${{q.id}}', '${{o.key}}')">
            <span class="option-dot"></span>
            ${{o.text}}
          </button>
        `).join('')}}
      </div>
      <div class="nav">
        ${{i > 0 ? `<button class="btn btn-back" onclick="goBack()">Назад</button>` : '<span></span>'}}
        <button class="btn btn-next" id="btn-next-${{i}}" disabled onclick="goNext()">
          ${{i < QUESTIONS.length - 1 ? 'Далее' : 'Узнать результат'}}
        </button>
      </div>
    </div>
  `).join('');
  updateProgress();
}}

function selectOption(el, questionId, key) {{
  // Deselect previous in same question
  el.closest('.options').querySelectorAll('.option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  answers[questionId] = key;
  document.getElementById(`btn-next-${{current}}`).disabled = false;
}}

function updateProgress() {{
  const pct = (current / QUESTIONS.length) * 100;
  document.getElementById('progress').style.width = pct + '%';
  // restore previous selection if navigating back
  const q = QUESTIONS[current];
  if (answers[q.id]) {{
    const saved = document.querySelector(`[data-key="${{answers[q.id]}}"]`);
    if (saved) {{
      saved.classList.add('selected');
      document.getElementById(`btn-next-${{current}}`).disabled = false;
    }}
  }}
}}

function goNext() {{
  const q = QUESTIONS[current];
  if (!answers[q.id]) return;
  if (current < QUESTIONS.length - 1) {{
    document.getElementById(`q-${{current}}`).classList.remove('active');
    current++;
    document.getElementById(`q-${{current}}`).classList.add('active');
    updateProgress();
  }} else {{
    showResult();
  }}
}}

function goBack() {{
  if (current > 0) {{
    document.getElementById(`q-${{current}}`).classList.remove('active');
    current--;
    document.getElementById(`q-${{current}}`).classList.add('active');
    updateProgress();
  }}
}}

function computeScores() {{
  const scores = {{}};
  SERVICES.forEach(s => {{ scores[s.id] = 0; }});
  Object.values(answers).forEach(key => {{
    const weights = SCORING[key] || {{}};
    Object.entries(weights).forEach(([id, w]) => {{
      if (id in scores) scores[id] = (scores[id] || 0) + w;
    }});
  }});
  return scores;
}}

function showResult() {{
  document.getElementById('quiz-body').style.display = 'none';
  document.getElementById('progress').style.width = '100%';

  const scores = computeScores();
  const topId = Object.entries(scores).sort((a, b) => b[1] - a[1])[0][0];
  const service = SERVICES.find(s => s.id === topId);
  const reason = REASONS[topId] || '';

  const priceHtml = service.price
    ? `<span class="badge badge-price">${{service.price.toLocaleString('ru-RU')}} ₽</span>`
    : `<span class="badge badge-free">цена по запросу</span>`;
  const durHtml = service.duration
    ? `<span class="badge badge-duration">${{service.duration}}</span>`
    : '';

  document.getElementById('result-card').innerHTML = `
    <div class="result-badge">Ваша услуга</div>
    <div class="result-name">${{service.name}}</div>
    <div class="result-desc">${{service.description}}</div>
    ${{reason ? `<div class="result-why"><strong>Почему именно это:</strong> ${{reason}}</div>` : ''}}
    <div class="result-meta">${{priceHtml}} ${{durHtml}}</div>
    <div class="result-actions">
      <a class="btn-order" href="https://t.me/tina_yuma" target="_blank">Записаться в Telegram</a>
      <a class="btn-clarify" href="${{`https://t.me/tina_yuma?text=${{encodeURIComponent('Хочу уточнить по услуге «' + service.name + '» перед заказом')}}`}}" target="_blank">Уточнить перед заказом</a>
      <p class="clarify-hint">Напишу, подходит ли вам именно эта услуга — без длинных переписок</p>
    </div>
  `;

  document.getElementById('result').classList.add('active');
}}

function restart() {{
  answers = {{}};
  current = 0;
  document.getElementById('result').classList.remove('active');
  document.getElementById('quiz-body').style.display = '';
  buildQuizHTML();
}}

buildQuizHTML();
</script>
</body>
</html>
"""


def main() -> None:
    if not SERVICES_FILE.exists():
        print(f"ERROR: {SERVICES_FILE} не найден. Сначала запусти parse.py.")
        sys.exit(1)

    with open(SERVICES_FILE, encoding="utf-8") as f:
        services = json.load(f)

    print(f"Загружено {len(services)} услуг из {SERVICES_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    html = HTML.format(
        services_json=json.dumps(services, ensure_ascii=False),
        scoring_json=json.dumps(SCORING, ensure_ascii=False),
        reasons_json=json.dumps(REASONS, ensure_ascii=False),
        questions_json=json.dumps(QUESTIONS, ensure_ascii=False),
    )

    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Quiz -> {OUTPUT_HTML}")
    print(f"Готово! Открой {OUTPUT_HTML} в браузере или задеплой на GitHub Pages.")


if __name__ == "__main__":
    main()
