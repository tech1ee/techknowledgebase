---
title: "Portfolio Strategy 2026: GitHub как proof of work"
created: 2025-12-26
modified: 2026-02-13
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - type/guide
  - level/advanced
related:
  - "[[resume-strategy]]"
  - "[[linkedin-optimization]]"
  - "[[personal-brand]]"
  - "[[standing-out]]"
prerequisites:
  - "[[resume-strategy]]"
  - "[[linkedin-optimization]]"
reading_time: 24
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Portfolio Strategy 2026: доказательство экспертизы

**Статистика 2026:**
- Recruiters проверяют GitHub до чтения резюме
- 75% hiring managers смотрят на code quality
- AI-проекты в portfolio — сильный дифференциатор
- Open source contributions → +15% к вероятности оффера

Portfolio — не только для juniors. Для Senior это демонстрация architecture decisions, code quality, и способности завершать проекты. **Quality > Quantity.** 3-5 excellent projects > 20 abandoned repos.

---

## Теоретические основы

> **Portfolio** (в карьерном контексте) — курированная коллекция артефактов, демонстрирующих профессиональную компетенцию. В отличие от резюме (claims), portfolio предоставляет **proof of work** — верифицируемые доказательства навыков.

Теоретический фундамент portfolio-стратегии опирается на несколько дисциплин:

| Концепция | Источник | Суть | Применение к GitHub |
|-----------|----------|------|---------------------|
| Signaling Theory | Spence (1973) | Артефакты снижают информационную асимметрию между кандидатом и работодателем | Качественный код = сигнал компетенции |
| Portfolio Theory | Markowitz (1952) | Диверсификация снижает риск | Разнообразие проектов покрывает разные навыки |
| Show Your Work | Austin Kleon (2014) | Процесс важнее результата; делись работой на каждом этапе | README, commit history, architecture docs |
| Proof of Work | — (криптография) | Верифицируемое доказательство затраченных усилий | Working code > claims in resume |

**Пирамида доказательства экспертизы (от слабого к сильному):**

```
Level 5: Open Source Impact — contributions в known projects
Level 4: Architecture Decisions — ADRs, design docs, trade-off analysis
Level 3: Working Code — finished projects с тестами и CI
Level 2: Learning Projects — tutorials, experiments (слабый сигнал для Senior)
Level 1: Claims — "proficient in Kotlin" без доказательств
```

Исследования показывают, что hiring managers тратят 2-5 минут на GitHub-профиль кандидата (Stack Overflow Developer Survey, 2024). За это время они оценивают: **code quality** (40%), **architecture thinking** (25%), **completion rate** (15%), **communication** (10%), **modern stack** (10%).

> **Принцип Quality > Quantity:** 3-5 polished проектов с comprehensive README, тестами и CI эффективнее 20 abandoned repos. Каждый незавершённый проект — негативный сигнал о способности доводить работу до конца.

→ Связано: [[resume-strategy]], [[personal-brand]], [[standing-out]]

---

## Что изменилось в 2026

```
2024 → 2026:
├── AI tools: необязательно → покажи использование
├── AI projects: бонус → ожидание для tech
├── GitHub Copilot: новинка → стандарт разработки
├── Profile README: nice-to-have → must-have
├── GitHub Pages: опция → рекомендуется
├── Contribution graph: косметика → hiring managers смотрят
└── Open source: опционально → сильный сигнал
```

### 2026 Portfolio Requirements

| Элемент | Важность | Что делать |
|---------|----------|------------|
| **Profile README** | Critical | Обязательно с bio и projects |
| **Pinned repos** | High | 4-6 лучших проектов |
| **AI integration** | High | Покажи AI tools в проектах |
| **Modern stack** | High | Compose, KMP, современные паттерны |
| **Documentation** | Critical | README в каждом проекте |
| **Activity** | Medium | Зелёный contribution graph |

---

## Зачем portfolio Senior Developer

```
МИФ: "Portfolio нужен только juniors без опыта"

РЕАЛЬНОСТЬ 2026:
• Recruiters гуглят тебя перед первым контактом
• GitHub profile = first technical impression
• Shows HOW you think, not just WHAT you've done
• Differentiator когда experience похож
• Proof что можешь писать современный код

ЧТО ПОКАЗЫВАЕТ PORTFOLIO:
• Code quality и architecture decisions
• Ability to finish projects
• Communication через documentation
• Technical depth и breadth
• Initiative beyond day job
• AI tools proficiency (2026)
```

---

## GitHub Profile Structure

### Profile README (must-have 2026)

Файл: `username/username/README.md`

```markdown
# Hi, I'm [Name] 👋

Senior Android Developer with 7+ years shipping apps for millions.
Currently exploring Kotlin Multiplatform and AI integration.

## 🔧 Tech Stack

**Android:** Kotlin, Jetpack Compose, Coroutines, Flow, Hilt
**Architecture:** Clean Architecture, MVVM, MVI, Multi-module
**Cross-platform:** Kotlin Multiplatform, Compose Multiplatform
**AI Tools:** GitHub Copilot, Claude API integration

## 🌟 Featured Projects

| Project | Description | Tech |
|---------|-------------|------|
| [Project A](link) | Offline-first app with 50K+ users | Kotlin, Compose |
| [Project B](link) | KMP shared library | KMP, SQLDelight |
| [Project C](link) | AI-powered feature | Claude API |

## 📊 GitHub Stats

![Your GitHub stats](https://github-readme-stats.vercel.app/api?username=yourusername&show_icons=true&theme=dark)

## 📫 Connect

- LinkedIn: [Your Profile](link)
- Email: your@email.com
- Blog: [yourblog.dev](link)

---

*Open to remote Senior/Staff Android roles*
```

### Pinned Repositories (4-6)

```
SELECTION CRITERIA:
1. Best code quality
2. Most complete/polished
3. Demonstrates modern skills
4. Variety of technologies
5. Recent activity (not abandoned 3+ years)

IDEAL MIX для Android Senior:
├── 1 Full app (end-to-end, modern stack)
├── 1 Library/SDK (shows API design)
├── 1 Architecture template (shows thinking)
├── 1 KMP/Cross-platform project (2026 skill)
├── 1 AI integration project (2026 differentiator)
└── 1 Experimental/Learning (shows curiosity)
```

---

## What Projects to Include

### For Android Senior/Staff 2026

```
HIGH VALUE PROJECTS:

1. PRODUCTION-QUALITY APP:
   ├── Full app using modern stack
   ├── Jetpack Compose UI
   ├── Clean Architecture / MVVM / MVI
   ├── Coroutines + Flow
   ├── Tests (unit + UI)
   ├── CI/CD setup
   └── Polished README with screenshots

2. ARCHITECTURE TEMPLATE:
   ├── Multi-module project structure
   ├── Clean boundaries between layers
   ├── Gradle Convention Plugins
   ├── README explaining decisions
   ├── Easy to clone and use
   └── GitHub template repository

3. OPEN SOURCE LIBRARY:
   ├── Solves real problem
   ├── Good API design
   ├── Comprehensive documentation
   ├── Published to Maven Central
   ├── Semantic versioning
   └── CHANGELOG maintained

4. KMP PROJECT (2026 must):
   ├── Shared Kotlin code
   ├── Platform-specific UI
   ├── SQLDelight или Room
   ├── Ktor для networking
   └── Shows cross-platform thinking

5. AI INTEGRATION (2026 differentiator):
   ├── Claude/OpenAI API integration
   ├── On-device ML (TensorFlow Lite)
   ├── AI-powered feature
   └── Clear documentation how AI is used
```

### Avoid These

```
❌ Tutorial follow-alongs (копипаст с курса)
❌ Incomplete projects (no README, broken build)
❌ Outdated tech (AsyncTask, Java-only)
❌ Projects без README
❌ Forked repos без своих изменений
❌ Abandoned 3+ years (если не legacy on purpose)
❌ Sensitive data (API keys, credentials)
```

---

## Project Quality Checklist

### README Template

```markdown
# Project Name

> Brief description in 1-2 sentences.

![Demo GIF](path/to/demo.gif)

## Features

- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **UI** | Jetpack Compose, Material 3 |
| **Architecture** | Clean Architecture, MVI |
| **DI** | Hilt |
| **Networking** | Retrofit, OkHttp |
| **Database** | Room |
| **Testing** | JUnit5, Mockk, Turbine |
| **CI/CD** | GitHub Actions |

## Architecture

```
app/
├── data/
│   ├── remote/
│   └── local/
├── domain/
│   ├── model/
│   ├── repository/
│   └── usecase/
└── presentation/
    ├── ui/
    └── viewmodel/
```

## Why This Architecture?

Brief explanation of architectural decisions and trade-offs.
Link to ADR documents if available.

## Getting Started

### Prerequisites
- Android Studio Hedgehog+
- JDK 17

### Installation
```bash
git clone https://github.com/you/project.git
cd project
./gradlew build
```

### Configuration
```
1. Get API key from [service]
2. Add to local.properties: API_KEY=your_key
3. Build and run
```

## Screenshots

| Home | Detail | Settings |
|------|--------|----------|
| ![](screenshots/home.png) | ![](screenshots/detail.png) | ![](screenshots/settings.png) |

## Testing

```bash
# Unit tests
./gradlew test

# UI tests
./gradlew connectedAndroidTest

# All tests with coverage
./gradlew testDebugUnitTestCoverage
```

## Roadmap

- [ ] Feature X
- [ ] Improvement Y
- [x] Completed feature

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE)

## Author

**Your Name** - [@yourgithub](https://github.com/yourgithub)
```

### Code Quality Checklist

```
README:
□ What the project does (1-2 sentences)
□ Why it exists (problem it solves)
□ Screenshots/GIFs
□ Tech stack table
□ How to build/run
□ Architecture overview
□ Future improvements

CODE:
□ Consistent coding style
□ Meaningful comments (when needed)
□ No hardcoded secrets
□ Clean git history
□ Proper .gitignore
□ No IDE-specific files committed

EXTRAS:
□ Unit tests
□ CI/CD (GitHub Actions)
□ License file
□ Semantic versioning / releases
□ CHANGELOG.md
```

---

## AI Integration in Portfolio (2026)

### Показать AI Proficiency

```
2026 EXPECTATION:
Hiring managers ожидают, что Senior dev использует AI tools.

КАК ПОКАЗАТЬ:

1. AI-ASSISTED DEVELOPMENT:
   ├── Mention в README: "Developed with GitHub Copilot"
   ├── .github/copilot-usage.md с примерами
   └── Thoughtful commit messages (not AI-generated garbage)

2. AI-POWERED FEATURES:
   ├── Claude/OpenAI API integration
   ├── On-device ML (TensorFlow Lite, ML Kit)
   ├── Vector search, embeddings
   └── AI-generated content

3. AI TOOLING:
   └── Custom AI scripts для разработки
```

### Example AI Project

```markdown
# AI Chat Feature

Android chat feature powered by Claude API with streaming responses.

## Features
- Real-time streaming responses
- Conversation history
- Offline queue for poor connectivity

## AI Integration
Using Claude 3.5 Sonnet via Anthropic API:
- Streaming with Ktor
- Retry logic with exponential backoff
- Token counting for context management

## Why Claude?
Decision: Claude vs GPT-4 vs Local LLM
- Chose Claude for: better reasoning, longer context
- Trade-off: API cost vs quality
- See [ADR-001](docs/adr/001-llm-choice.md)
```

---

## Beyond GitHub

### Play Store Apps

```
BENEFITS:
• Proof you can ship to production
• Real users = real feedback
• Link from resume/LinkedIn
• Reviews visible (social proof)

REQUIREMENTS 2026:
• App must be polished
• Material 3 design
• No obvious bugs
• Regular updates (at least quarterly)

ALTERNATIVE если не в Store:
• APK download link
• Video demo (YouTube/Loom)
• Screenshots с описанием
```

### Technical Blog

```
COMPLEMENTS CODE:
• Explains WHY, not just WHAT
• Shows thought process
• SEO brings traffic to your name
• Content для LinkedIn sharing

PLATFORMS 2026:
├── Personal site (best for SEO)
├── Medium (good reach)
├── Dev.to (developer community)
├── Hashnode (custom domain free)
└── Substack (if building newsletter)

ARTICLE IDEAS:
• "How I built [Project X]"
• "Architecture decisions in [Project]"
• "Performance optimization case study"
• "Lessons learned from [Challenge]"
• "Comparing [Technology A] vs [Technology B]"

FREQUENCY:
• 1 article/month minimum
• Quality > Quantity
```

### Conference Talks

```
HIGH SIGNAL:
• Shows communication skills
• Public validation of expertise
• Reusable content (slides, video)
• Networking opportunity

GETTING STARTED:
1. Local meetups first (low stakes)
2. Lightning talks (5-10 min)
3. Company internal talks
4. Regional conferences
5. Major conferences (Droidcon, KotlinConf)

TRACK IN PORTFOLIO:
• YouTube/Vimeo links в Featured
• Speaker deck links
• Conference badges/logos
```

---

## Open Source Contributions

### Why It Matters 2026

```
SIGNALS TO EMPLOYERS:
• Collaboration skills
• Reading others' code
• Following contribution guidelines
• Community recognition
• Often asked about in interviews

STATS:
• 15% higher offer probability
• Networking with maintainers
• Real-world complex codebases
```

### How to Contribute

```
GETTING STARTED:
1. Fix documentation (low barrier)
2. Add tests
3. Small bug fixes
4. Improve error messages
5. Translate UI

GOOD TARGETS:
├── Libraries you use daily
├── Kotlin/Android ecosystem
├── "good first issue" labels
├── "help wanted" labels
└── Projects by companies you target

EXAMPLES для Android:
• compose-samples (Google)
• kotlinx.coroutines (JetBrains)
• coil (coil-kt)
• Accompanist (Google)
• Cash App libraries
```

### Track Contributions

```
В Profile README:
"## Open Source Contributions
- [kotlinx.coroutines](link) — Fixed flow cancellation bug (#1234)
- [compose-samples](link) — Added accessibility support (#567)
- [library](link) — Documentation improvements"

В Resume:
"Contributed to kotlinx.coroutines, fixing critical flow
cancellation issue used by 50K+ projects"
```

---

## What Hiring Managers Look For

### During GitHub Review

```
1. CODE QUALITY (40%):
   ├── Readable, maintainable code
   ├── Proper naming conventions
   ├── Not over-engineered
   ├── Appropriate abstractions
   └── Error handling

2. ARCHITECTURE THINKING (25%):
   ├── Separation of concerns
   ├── Testable design
   ├── Appropriate patterns
   ├── Clean module boundaries
   └── Dependency management

3. COMPLETION (15%):
   ├── Projects that are finished
   ├── Working builds
   ├── Documentation
   └── No abandoned-looking repos

4. COMMUNICATION (10%):
   ├── Clear READMEs
   ├── Good commit messages
   ├── Issue/PR discussions
   └── Code comments where needed

5. MODERN SKILLS (10%):
   ├── Current tech stack
   ├── AI tools usage
   ├── Best practices
   └── Growth mindset
```

### Red Flags

```
❌ Copied code without attribution
❌ No documentation anywhere
❌ Years of inactivity
❌ Only tutorial projects
❌ Everything incomplete
❌ Commit messages: "fix", "update", "asdf"
❌ API keys in code
❌ No tests anywhere
❌ Java-only in 2026 (for Android)
```

---

## Portfolio Review Checklist

### Before Job Search

```
PROFILE:
□ Profile README updated
□ Bio filled (160 chars)
□ Location (or "Remote")
□ Company/affiliation
□ Website link
□ Professional avatar

PINNED REPOS (4-6):
□ Best projects pinned
□ Variety of technologies
□ Each has good README
□ Each has working build
□ Each has screenshots/demo
□ Recent activity or marked "complete"

EACH REPO:
□ Clear README
□ No sensitive data
□ Consistent coding style
□ License file
□ .gitignore proper

CONTRIBUTION GRAPH:
□ Activity in last 6 months
□ No long gaps (или explanation)
```

### Ongoing Maintenance

```
WEEKLY:
□ Commit to at least one repo

MONTHLY:
□ Review and update one README
□ Add new screenshot/demo если улучшил
□ Update dependencies in main projects

QUARTERLY:
□ Add new project или major update
□ Review all pinned repos
□ Update Profile README
□ Check for broken links

BEFORE INTERVIEW:
□ Check company-relevant projects visible
□ No controversial content
□ Latest activity visible
□ Links работают
```

---

## Quick Wins

### If You Have 2 Hours

```
HOUR 1:
□ Create/update profile README
□ Pin 4-6 best repositories
□ Add bio and links

HOUR 2:
□ Update README of top pinned repo
□ Add screenshots/GIF
□ Check все links работают
```

### If You Have a Weekend

```
SATURDAY:
□ Build one polished small project
   ├── Simple but complete
   ├── Modern stack (Compose, Coroutines)
   ├── Good README
   └── Working CI/CD

SUNDAY:
□ Complete documentation
□ Add architecture diagram
□ Write blog post о проекте
□ Share on LinkedIn
```

### Project Ideas для Quick Portfolio

```
EASY (1-2 days):
• Todo app с modern architecture
• Weather app с API integration
• Notes app с Room
• Calculator с Compose

MEDIUM (1 week):
• News reader с offline support
• Expense tracker с charts
• Recipe app с search
• Habit tracker

ADVANCED (2+ weeks):
• KMP shared module
• AI-powered feature
• Open source library
• Architecture template
```

---

## GitHub Features to Use

### GitHub Actions CI/CD

```yaml
# .github/workflows/android.yml
name: Android CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'
    - name: Build
      run: ./gradlew build
    - name: Run tests
      run: ./gradlew test
```

### GitHub Pages

```
USE FOR:
• Project documentation
• Portfolio website
• API documentation
• Interactive demos

SETUP:
1. Settings → Pages
2. Source: main branch / docs folder
3. Custom domain (optional)
```

### Template Repository

```
MAKE YOUR ARCHITECTURE TEMPLATE:
1. Create clean project
2. Settings → Template repository ✓
3. Others can "Use this template"
4. Shows architectural thinking
```

---

## Полный Action Plan

### Week 1: Foundation

```
DAY 1-2: Profile
□ Create profile README
□ Update bio, links
□ Pin best repos

DAY 3-4: Top Project
□ Pick best project
□ Write comprehensive README
□ Add screenshots/demo
□ Setup CI/CD

DAY 5-7: Second Project
□ Same for second project
□ Different technology focus
```

### Week 2: Content

```
DAY 1-3: Third Project
□ Either existing or new small project
□ Focus on modern stack

DAY 4-5: Open Source
□ Find 2-3 repos to contribute
□ Make first contribution (docs/tests)

DAY 6-7: Blog Post
□ Write about one project
□ Share on LinkedIn
```

### Ongoing

```
WEEKLY:
□ 2-3 commits minimum
□ 1 open source interaction

MONTHLY:
□ 1 project improvement
□ 1 blog post or significant README update
```

---

## Куда дальше

→ [[resume-strategy]] — как упоминать portfolio в резюме
→ [[linkedin-optimization]] — showcase в Featured section
→ [[personal-brand]] — долгосрочная стратегия
→ [[standing-out]] — использование portfolio для differentiation

---

## Связь с другими темами

- [[resume-strategy]] — Резюме и portfolio дополняют друг друга: резюме рассказывает о твоём опыте словами и метриками, а portfolio показывает его в коде. В резюме упоминай ссылки на GitHub-проекты, а в portfolio README ссылайся на результаты из резюме. Hiring manager читает резюме за 7 секунд, потом открывает GitHub — оба должны быть согласованы.

- [[linkedin-optimization]] — LinkedIn Featured section — идеальное место для showcase portfolio-проектов. Pinned repos с GitHub, blog-посты о проектах и demo-видео размещаются в Featured и привлекают внимание рекрутеров. LinkedIn даёт visibility, GitHub — proof of work.

- [[personal-brand]] — Portfolio — это техническая основа личного бренда. Без качественных проектов на GitHub бренд остаётся пустыми словами. Portfolio показывает code quality, architecture thinking и ability to finish projects — именно эти сигналы формируют репутацию эксперта.

- [[standing-out]] — В 2026 году portfolio с AI-интеграцией и KMP-проектами — один из сильнейших дифференциаторов. Когда 50 кандидатов присылают одинаковые резюме, тот, у кого есть polished GitHub с modern stack, автоматически попадает в top-5. Portfolio превращает "I can do this" в "Here's proof".

## Источники

### Теоретические основы

- Spence M. (1973). *Job Market Signaling*. — Теория сигналов: portfolio как costly signal компетенции, который некомпетентный кандидат не сможет имитировать.

- Markowitz H. (1952). *Portfolio Selection*. Journal of Finance. — Теория диверсификации, применимая к набору проектов: разнообразие технологий снижает карьерный риск.

- Kleon A. (2014). *Show Your Work!*. — Философия открытости процесса: делись работой на каждом этапе, не только результатом.

- Larson W. (2022). *Staff Engineer*. — Какие артефакты работы ценятся на Senior/Staff+ уровне: RFCs, architecture templates, open source.

- Xu A. (2020). *System Design Interview*. — System design знания для architecture template repository.

### Практические руководства

- [Zencoder: Software Engineer Portfolio 2026](https://zencoder.ai/blog/how-to-create-software-engineer-portfolio)
- [Fonzi AI: AI Engineer Portfolio Guide](https://fonzi.ai/blog/ai-engineer-portfolio)
- [AI Jobs UK: Portfolio Projects That Get Hired](https://artificialintelligencejobs.co.uk/career-advice/portfolio-projects-that-get-you-hired-for-ai-jobs-with-real-github-examples-)
- [GitHub Blog: Becoming an AI Developer](https://github.blog/ai-and-ml/vibe-coding-your-roadmap-to-becoming-an-ai-developer/)
- [Dev.to: Creative Developer Portfolio 2026](https://dev.to/nk2552003/the-anthology-of-a-creative-developer-a-2026-portfolio-56jp)

---

## Проверь себя

> [!question]- Почему tutorial follow-along проекты на GitHub вредят, а не помогают Senior-кандидату?
> Tutorial проекты сигнализируют hiring manager: кандидат копирует, а не думает самостоятельно. Для Senior ожидаются собственные architecture decisions, trade-off analysis, и оригинальные решения. Один polished project с документированными решениями ценнее 10 tutorial repos.

> [!question]- Ты готовишь portfolio для подачи в fintech-компанию. Какие 4-6 pinned repos ты выберешь и почему?
> Ideal mix: 1) Full app с финансовой тематикой (security, encryption). 2) Architecture template с multi-module Clean Architecture. 3) KMP shared module для cross-platform. 4) AI integration project (показать proficiency). 5) Open source contribution в финансовую библиотеку. Каждый repo демонстрирует разный аспект: code quality, architecture, modern skills, domain knowledge.

> [!question]- Как AI Integration в portfolio 2026 отличается от простого "я использую Copilot"?
> Три уровня: 1) AI-assisted development -- упоминание Copilot в README (базовый). 2) AI-powered features -- Claude/OpenAI API integration, on-device ML (средний). 3) AI tooling -- custom AI scripts для разработки, ADR документирующий выбор LLM (продвинутый). Hiring managers ищут не "использую AI", а "понимаю trade-offs и интегрирую осознанно".

> [!question]- На что hiring managers тратят больше всего внимания при ревью GitHub -- и какие red flags приводят к немедленному отказу?
> Приоритеты: Code Quality (40%), Architecture Thinking (25%), Completion (15%), Communication (10%), Modern Skills (10%). Немедленные red flags: API keys в коде, commit messages "fix"/"asdf", всё incomplete, Java-only в 2026. Главное: "shows HOW you think, not just WHAT you've done".

---

## Ключевые карточки

Portfolio 2026 -- обязательные элементы?
?
Profile README (critical), Pinned repos 4-6 (high), AI integration (high), Modern stack -- Compose/KMP (high), Documentation в каждом проекте (critical), Activity graph (medium).

Ideal Pinned Repos mix для Android Senior?
?
6 repos: 1) Full app (modern stack, end-to-end). 2) Library/SDK (API design). 3) Architecture template (shows thinking). 4) KMP project (2026 skill). 5) AI integration (differentiator). 6) Experimental/Learning (curiosity).

README Template -- обязательные секции?
?
Brief description, Features, Tech Stack table, Architecture overview, Getting Started (prerequisites + install), Screenshots, Testing commands, Roadmap, License. Каждый pinned repo должен иметь comprehensive README.

Hiring Manager Review -- распределение внимания?
?
Code Quality 40% (readable, maintainable, proper naming). Architecture Thinking 25% (SoC, testable design, patterns). Completion 15% (finished, working builds, docs). Communication 10% (READMEs, commits, PR discussions). Modern Skills 10% (current stack, AI tools).

Open Source Contributions -- почему +15% к вероятности оффера?
?
Signals: collaboration skills, reading others' code, following contribution guidelines, community recognition. Начинать с: документация, тесты, small bug fixes. Targets: библиотеки которые используешь, "good first issue", проекты целевых компаний.

---

## Куда дальше

| Направление | Тема | Ссылка |
|------------|------|--------|
| Следующий шаг | Как упомянуть portfolio в резюме | [[resume-strategy]] |
| Углубиться | Долгосрочная стратегия personal brand | [[personal-brand]] |
| Смежная тема | Git workflows для open source | [[git-workflows]] |
| Обзор | Как выделиться среди кандидатов | [[standing-out]] |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
