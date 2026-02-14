---
title: "Динамика команды"
created: 2026-01-18
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
target-role: [em, director, tech-lead]
teaches:
  - tuckman stages
  - psychological safety
  - conflict resolution
sources: [google-aristotle, five-dysfunctions, tuckman]
tags:
  - topic/leadership
  - type/deep-dive
  - level/intermediate
related:
  - "[[building-engineering-team]]"
  - "[[team-culture]]"
  - "[[motivation]]"
prerequisites:
  - "[[building-engineering-team]]"
  - "[[team-culture]]"
reading_time: 9
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Динамика команды

> **TL;DR:** Команда — не статичная структура, а динамическая система. Google's Project Aristotle: #1 фактор эффективности — psychological safety. Conflict — normal и necessary, но нужно конструктивно. Tuckman: forming → storming → norming → performing. Каждая стадия требует разного leadership.

---

## Psychological Safety (Google Aristotle)

```
ОПРЕДЕЛЕНИЕ:
"Уверенность что можно рисковать без
наказания или унижения."

5 ФАКТОРОВ ЭФФЕКТИВНЫХ КОМАНД:
#1 Psychological Safety (самый важный)
#2 Dependability
#3 Structure & Clarity
#4 Meaning
#5 Impact

КАК СТРОИТЬ:
□ Leader показывает уязвимость первым
□ Благодарить за вопросы и идеи
□ Ошибки обсуждать без blame
□ "Я не знаю" — нормально
□ Приветствовать несогласие
```

## Tuckman Stages

```
FORMING → STORMING → NORMING → PERFORMING

FORMING (вежливость):
• Знакомство, осторожность
• Leader: дай направление, познакомь

STORMING (конфликт):
• Роли оспариваются, friction
• Leader: фасилитируй конфликт, не избегай

NORMING (нормы):
• Процессы устаканиваются
• Leader: закрепляй хорошее

PERFORMING (продуктивность):
• Высокая эффективность
• Leader: убирай препятствия

⚠️ Любое изменение (new member, reorg)
возвращает команду к FORMING.
```

## Five Dysfunctions (Lencioni)

```
ПИРАМИДА ДИСФУНКЦИЙ:

        ╱ INATTENTION TO RESULTS ╲
       ╱   Личные цели > командных   ╲
      ╱  AVOIDANCE OF ACCOUNTABILITY  ╲
     ╱   Избегание ответственности     ╲
    ╱    LACK OF COMMITMENT             ╲
   ╱     Нет buy-in в решения            ╲
  ╱      FEAR OF CONFLICT                 ╲
 ╱       Избегание конструктивного спора   ╲
╱        ABSENCE OF TRUST                   ╲
         Нет уязвимости друг перед другом

РЕШЕНИЕ: работай снизу вверх.
Сначала trust, потом всё остальное.
```

## Healthy vs Unhealthy Conflict

```
HEALTHY:                        UNHEALTHY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Про идеи                      • Про людей
• "Я думаю X лучше"             • "Ты не прав"
• Фокус на outcome              • Фокус на победу
• Слушают друг друга            • Перебивают
• Ищут общее решение            • Защищают позицию
• После meeting — OK            • После meeting — обида

КАК ФАСИЛИТИРОВАТЬ:
1. Установи ground rules
2. Слушай всех
3. Рефрейми personal → ideas
4. Найди underlying interests
5. Закрой: decision + commitment
```

## Team Health Signals

```
ЗДОРОВАЯ КОМАНДА:
✓ Люди говорят на meetings
✓ Смеются вместе
✓ Помогают друг другу
✓ Спорят конструктивно
✓ Признают ошибки
✓ Празднуют победы

ПРОБЛЕМНАЯ КОМАНДА:
✗ Тишина на meetings
✗ Группировки/клики
✗ Blame culture
✗ Избегают друг друга
✗ Passive-aggressive
✗ High turnover
```

---

## Связанные темы

- [[building-engineering-team]] — построение команды
- [[team-culture]] — культура
- [[motivation]] — мотивация

## Источники

| Источник | Тип |
|----------|-----|
| [Google Project Aristotle](https://rework.withgoogle.com/) | Research |
| [Five Dysfunctions of a Team](https://www.amazon.com/Five-Dysfunctions-Team-Leadership-Fable/dp/0787960756) | Book |
| [Tuckman's Stages](https://en.wikipedia.org/wiki/Tuckman%27s_stages_of_group_development) | Model |

---

## Связь с другими темами

**[[building-engineering-team]]** — Team dynamics — это поведенческое измерение team building. Если building-engineering-team фокусируется на структуре (кого нанимать, как компоновать), то team-dynamics раскрывает, что происходит после: как люди взаимодействуют, проходят через стадии Tuckman (forming → storming → norming → performing) и формируют рабочие паттерны. Менеджер, понимающий динамику, может предвидеть и направлять конфликты вместо их тушения.

**[[team-culture]]** — Культура и динамика — два лица одной медали. Culture определяет expected behaviors ("как мы здесь делаем вещи"), а dynamics показывает actual behaviors в реальном времени. Gap между declared culture и observed dynamics — важнейший diagnostic signal для менеджера. Если culture говорит "мы ценим feedback", а dynamics показывает, что люди избегают conflict — это проблема.

**[[motivation]]** — Мотивация тесно связана с team dynamics: psychological safety (#1 фактор из Google Aristotle) напрямую влияет на intrinsic motivation. В команде с healthy dynamics люди чувствуют себя safe для risk-taking, creative thinking и honest communication, что усиливает мотивацию через autonomy и purpose. Toxic dynamics, наоборот, разрушают даже самую сильную intrinsic motivation.

## Источники и дальнейшее чтение

- **Patrick Lencioni, "The Five Dysfunctions of a Team" (2002)** — Центральная книга для понимания team dynamics. Модель пяти дисфункций (absence of trust, fear of conflict, lack of commitment, avoidance of accountability, inattention to results) — это diagnostic framework, который помогает менеджеру идентифицировать корневые причины проблем в team dynamics.
- **Camille Fournier, "The Manager's Path" (2017)** — Описывает, как менеджер на разных уровнях влияет на team dynamics: от первого EM, строящего trust через 1-on-1, до Director, управляющего dynamics между несколькими командами.
- **Ed Catmull, "Creativity Inc." (2014)** — Pixar's Braintrust — пример управляемой team dynamics, где honest, direct feedback является нормой, а не источником conflict. Catmull показывает, как создать среду, где productive conflict (storming) ведёт к creative breakthroughs.


## Проверь себя

> [!question]- Storming — это нормально
> Новый менеджер видит конфликт в команде после прихода двух новых сотрудников. Он хочет 'решить проблему', убрав conflict. Используя модель Tuckman, объясните почему этот конфликт нормален и как менеджер должен действовать на стадии storming вместо подавления конфликта.

> [!question]- Five Dysfunctions и диагностика
> Команда показывает следующие симптомы: люди не спорят на meetings, все кивают, но потом делают по-своему. Используя пирамиду Lencioni, определите на каком уровне находится дисфункция и какой фундамент нужно построить в первую очередь.

> [!question]- Healthy vs Unhealthy conflict
> На code review два senior инженера начинают спорить. Один говорит 'ты всегда пишешь плохой код', другой отвечает атакой. Как рефреймить эту ситуацию от personal attack к idea-based discussion? Какие ground rules установить?

## Ключевые карточки

Назови 4 стадии команды по Tuckman.
?
Forming (вежливость, знакомство) -> Storming (конфликт, friction) -> Norming (нормы, процессы) -> Performing (высокая эффективность). Любое изменение (new member, reorg) возвращает к Forming.

Назови 5 факторов эффективных команд по Google Aristotle (в порядке важности).
?
#1 Psychological Safety, #2 Dependability, #3 Structure & Clarity, #4 Meaning, #5 Impact.

Назови 5 дисфункций команды по Lencioni (снизу вверх).
?
Absence of Trust -> Fear of Conflict -> Lack of Commitment -> Avoidance of Accountability -> Inattention to Results. Решение: работай снизу вверх, начни с trust.

Чем healthy conflict отличается от unhealthy?
?
Healthy: про идеи, фокус на outcome, слушают друг друга, ищут общее решение. Unhealthy: про людей, фокус на победу, перебивают, защищают позицию.

## Куда дальше

| Тип | Ссылка | Описание |
|-----|--------|----------|
| Следующий шаг | [[motivation]] | Мотивация и её связь с psychological safety |
| Углубиться | [[conflict-resolution]] | Детальные техники разрешения конфликтов |
| Смежная тема | [[cognitive-biases]] | Когнитивные искажения в командной динамике |
| Обзор | [[leadership-overview]] | Карта раздела лидерства |

---

*Последнее обновление: 2026-02-13*
