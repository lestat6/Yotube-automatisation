# 🎬 YouTube Automation Pipeline

Естетично впорядкований, стабільний пайплайн для підготовки відео-проєктів з `sc.txt`.

## ✨ Що вже відкалібровано

- **Єдиний contract маркерів** в `markers.py`.
- **Preflight валідація** (`validate_scenario.py`) перед будь-якими змінами файлів.
- **Комбайн обробки** (`run_all.py`):
  - виділення HOOK/CORE/LIGHT,
  - експорт текстів в `AudioVoice/*.txt`,
  - генерація stub `*.mp3`,
  - перенос футажів за `[FOLDER]` в `MEDIA/<SECTION>/N.mp4`.
- **Балансування тривалості** (`balance_media.py`) з підтримкою `pydub` + `opencv`.
- **Оркестратор** (`run_pipeline.py`) зі статусами етапів `OK/FAIL`.
- **Спеціалізований парсер** (`03_parse_footages.py`) на базі `VALID_STRUCTURE`.

## 🧭 Рекомендований порядок запуску

```bash
python run_pipeline.py \
  --scenario /path/to/sc.txt \
  --project-dir /path/to/project \
  --media-root /path/to/library \
  --dry-run
```

Після dry-run прибираєте `--dry-run` і запускаєте реальний перенос.

## 🧱 Структура

```text
.
├── markers.py
├── validate_scenario.py
├── run_all.py
├── 03_parse_footages.py
├── balance_media.py
├── run_pipeline.py
└── README.md
```

## ✅ Production-нотатка

Для бойового режиму рекомендується:
1. замінити TTS-stub у `run_all.py` на реальний `edge-tts`;  
2. додати rollback-скрипт по `global_transfer_log.txt`;  
3. зафіксувати `requirements.txt` для `pydub/opencv`.
