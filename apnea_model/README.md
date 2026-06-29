# apnea_model

Сюда кладётся модель определения апноэ. Бэкенд импортирует ее как top-level пакет `apnea_model`.

## Ожидаемый интерфейс

В `apnea_model/__init__.py` (или модуле, доступном как `apnea_model.predict`) должна быть функция:

```python
def predict(audio_path: str) -> tuple[bool, float]:
    ...
```

- вход: путь к временному аудиофайлу (wav/mp3), который бэкенд сохраняет из multipart-запроса
- выход: кортеж `(has_apnea: bool, confidence: float)`, где confidence в диапазоне `[0, 1]`

## Куда положить

Файлы модели — в эту папку. При запуске через `uvicorn backend.main:app` с корня репозитория пакет `apnea_model` уже на `PYTHONPATH`. В Docker папка копируется в `/app/apnea_model`, `PYTHONPATH=/app`.

## Если модель ещё не загружена

`backend/services/apnea.py` ловит ошибку импорта и возвращает детерминированную заглушку (по хэшу файла), помечая ответ `used_model: false`. Это позволяет демонстрировать сквозной сценарий до загрузки реальной модели. После загрузки `used_model` станет `true` без изменений в коде.

## Проверка

```bash
python -c "from apnea_model import predict; print(predict('test.wav'))"
```
