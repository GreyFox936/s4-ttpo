# F-Bank testing task

Учебный проект по ручному и автоматизированному тестированию ненастоящего банковского сервиса F-Bank.

## Состав проекта

```text
.
├── index.html
├── assets/
│   ├── index-BUH56GOL.js
│   └── index-Dy9zO9yl.css
├── docs/
├── tests/
├── .github/workflows/selenium.yml
├── pytest.ini
└── requirements.txt
```

## Запуск приложения локально

По инструкции к заданию сервис запускается из папки с `index.html` и директорией `assets`.

```bash
python3 -m http.server 8000
```

После запуска открыть:

```text
http://localhost:8000/?balance=30000&reserved=20001
```

Параметры `balance` и `reserved` задают сумму и зарезервированную часть суммы.

## Запуск Selenium-тестов

Нужен установленный Google Chrome and/or Chromium:


```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell

pip install -r requirements.txt
pytest -v
```

## GitHub Actions

По условию задания тоговая сборка должна быть красной из-за непроходящих тестов.

Падающие тесты фиксирующие дефекты:

- `DEF-001` - отрицательная сумма перевода принимается как валидная
- `DEF-002` -  перевод блокируется при равенстве суммы с комиссией доступному остатку
- `DEF-003` - поле номера карты принимает 17 цифр вместо 16
- `DEF-004` - валютные счета доступны в интерфейсе, но проверка доступности перевода использует рублёвый баланс из URL


Красная сборка означает, что дефекты воспроизводятся автотестами. Ожидаемый результат
