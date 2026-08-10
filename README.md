# BYTE//BRAWL

A gamified coding practice platform. Solve problems with an AI mentor that gives
hints rather than answers, then drop the mentor and duel other developers on a
15-minute clock with Elo-matched opponents.

Django 5.2 · SQLite (Postgres planned) · server-rendered templates · vanilla JS

Status as of **2026-08-10**: the front end is built against the design handoff and
runs on real data. **Neither the judge nor the mentor exists** — code submission,
test results, and guru replies are simulated client-side. See [TODO.md](TODO.md).

---

## What works

| Area | State |
|---|---|
| **Home** | Hero, about grid, access terminal, contact band. Real. |
| **Auth** | Signup / login / logout. Session-backed, messages rendered site-wide. |
| **About / Contact** | Render with the shared sidebar layout. Copy is placeholder. |
| **Problem list** | 10 seeded problems (3 Easy / 4 Medium / 3 Hard) with difficulty pills. |
| **Problem detail** | Description, I/O formats, worked example, CodeSpace, AI Guru. |
| **Design system** | Full token set — colours, type, spacing, components. |

## What doesn't

| Area | State |
|---|---|
| **Judge** | Does not exist. `RUN` / `SUBMIT` POST successfully, then JS renders a **simulated** verdict. |
| **AI Guru** | Does not exist. Replies are canned strings. |
| **Compete** | `HttpResponse("This is Compete Page")` — plain text, outside the design. |
| **Profile** | Not built. Elo is hardcoded `1450` in the nav. |
| **Contact form** | Posts and acknowledges, but never writes to the `Contact` model. |

The simulated results carry a visible "TEMPORARY" notice in the verdict modal so
a passing verdict can't be mistaken for a real one.

---

## Running it

```bash
cd bytebrawl
python manage.py migrate
python manage.py createsuperuser     # to seed problems via /admin
python manage.py runserver
```

| Route | What |
|---|---|
| `/` | Home — hero, about, auth, contact |
| `/about/`, `/contact/` | Static pages |
| `/login/`, `/logout/`, `/signup/` | Auth endpoints (POST, except logout) |
| `/questions/` | Problem list |
| `/questions/<q_no>/` | Problem detail — description, editor, guru |
| `/compete/` | Placeholder |
| `/admin/` | Problem seeding |

Problems are entered through the Django admin. All three models are registered.

> **Static files are unversioned in development.** After editing CSS or JS,
> hard-refresh (`Ctrl+F5`) — the dev server has no cache busting.

---

## Naming conventions

**Project standard. Applies to everything from here on.**

| Thing | Rule | Examples |
|---|---|---|
| **Packages** (apps, Python packages) | lowercase, **no underscore** | `home`, `problembank`, `judge`, `learning` |
| **Modules** (`.py` files) | lowercase, underscore allowed | `views.py`, `authentication.py`, `seed_problems.py` |
| **Classes** | CapWords / CamelCase | `TestCases`, `Submission`, `LearningConfig` |
| **Functions & methods** | lowercase snake_case | `question_description()`, `solve_two_sum()` |
| **Variables** | lowercase snake_case | `sample_input`, `test_case_no` |
| **Constants** | UPPERCASE_WITH_UNDERSCORES | `PUBLIC_CASES`, `VERDICT_CHOICES` |

Packages take no underscore, so a two-word app is `problembank`, not
`problem_bank`. Modules do take one, so `seed_problems.py` is correct.

**Exempt — framework-mandated names.** Django requires these exact spellings and
they are module-level *variables*, not constants: `urlpatterns`, `application`,
`app_name`, `register`, `default_auto_field`. Leave them lowercase.

Run `/nomenclature-check` to audit the codebase against this table.

### Branches

**Every feature goes on a `feature/` branch.** Never commit a feature straight to
`main`.

| Prefix | For | Example |
|---|---|---|
| `feature/` | new functionality | `feature/judge-sandbox` |
| `fix/` | bug fixes | `fix/signup-missing-fields` |
| `chore/` | tooling, deps, config | `chore/postgres-migration` |
| `docs/` | documentation only | `docs/api-reference` |

After the prefix, use **lowercase kebab-case** — hyphens, not underscores, and no
CapitalCase. `feature/judge-sandbox`, not `feature/Judge_Sandbox`.

Name the branch after the outcome, not the file you happen to be editing:
`feature/elo-ratings` beats `feature/update-models`.

One branch per logical change. If a branch needs "and" to describe it, it's two
branches.

---

## Structure

```
ByteBrawl/
├── README.md
├── TODO.md
├── .claude/
│   ├── DEsign/README.md           design handoff — source of truth for UI
│   └── skills/nomenclature-check/ naming audit skill
└── bytebrawl/
    ├── manage.py
    ├── bytebrawl/                 project config (settings, urls, wsgi, asgi)
    │
    ├── home/                      home, about, contact, and all auth
    │   ├── authentication.py      blogin / blogout / signin
    │   ├── models.py              Contact
    │   └── templates/             home.html, about.html, contact.html
    │
    ├── problembank/               DATA OWNER — no views
    │   ├── models.py              Problems, TestCases, Submission
    │   └── management/commands/seed_problems.py
    │
    ├── learning/                  practice UI
    │   ├── views.py               problem list + detail
    │   └── templates/             questions.html, question_description.html
    │
    ├── compete/                   placeholder only
    ├── judge/                     scaffolded, empty — see TODO §1
    │
    ├── templates/                 project-level shared
    │   ├── base.html              blocks: title, page_class, sidebar,
    │   │                          content, extra_css, extra_js
    │   └── partials/              navbar, footer, sidebar
    │
    └── static/
        ├── css/style.css          the entire design system
        └── js/question_description.js   RUN / SUBMIT / guru, all simulated
```

### Dependency direction

```
learning ─┐
          ├──→ problembank ──→ judge*, mentor*      (* not built yet)
compete ──┘
```

- **`problembank`** — data owner. `Problems`, `TestCases`, `Submission`. No views.
  Will expose `selectors.py` so callers never touch its ORM directly.
- **`learning`** — practice UI. Will own guru chat history.
- **`compete`** — duels, matchmaking, Elo. Websocket consumers.
- **`judge`** — should be a plain Python package with no models, so it stays
  testable without a database and can move to a queue worker or its own container.
  `grade(code, language, cases) -> Verdict`.
- **`mentor`** — same shape. `ask(problem, code, failing_case, history) -> reply`.

`Submission` lives in `problembank`, not `learning`, because both features create
submissions — if it sat in `learning`, `compete` would import a sibling feature.
It carries no duel field; `compete.DuelParticipant` points *at* a submission
instead, keeping every arrow one-way.

Nothing points back up the graph. `judge` and `mentor` import nothing project-local.

---

## Design system

Everything derives from `.Claude/DEsign/README.md`. Tokens live as CSS custom
properties at the top of `static/css/style.css`.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0a0118` | Page background |
| `--panel` | `rgba(18,10,36,.6)` | Panel fill |
| `--border` | `#241a3d` | Panel border |
| `--cyan` | `#00f0ff` | Primary, problem panel, CTAs |
| `--magenta` | `#ff2bd6` | Compete, code panel, secondary CTAs |
| `--green` | `#39ff88` | Success, solved, guru |

Type: **Orbitron** (display) · **Rajdhani** (body/UI) · **JetBrains Mono** (code,
eyebrows, tags, timers).

Two rules the design is strict about:

1. **No `border-radius` anywhere.** Sharp corners throughout. The single exception
   in the codebase is the terminal window's traffic-light dots.
2. **Panels carry a 2px accent top border** that colour-codes purpose — cyan for
   problem, magenta for code, green for guru/success, red for failure.

### Adding a page

Extend `base.html` and fill the blocks:

```django
{% extends "base.html" %}
{% block title %}Thing | BYTE//BRAWL{% endblock %}
{% block page_class %}page--sidebar{% endblock %}   {# optional #}
{% block sidebar %}{% include "partials/sidebar.html" %}{% endblock %}
{% block content %}...{% endblock %}
{% block extra_js %}...{% endblock %}
```

Nav, footer, and the messages banner come from `base.html` automatically.
