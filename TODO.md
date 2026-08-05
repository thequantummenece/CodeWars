# CODE//WARS — TODO

Outstanding work in dependency order. See [README.md](README.md) for what already
works and where things live.

**Two things dominate everything else: the sandbox and the websocket layer.** The
restructuring in §0 was hours of work; those two are weeks. Don't let the first
feel like progress on the second.

---

## Progress

**Done since the last pass — the whole §0 restructure, essentially.**

The app split landed: `Questions` → `Learning` (practice UI), with `problembank`
extracted as the data owner. Tables were renamed in place rather than dropped, so
nothing was lost in the move. `judge/` and `mentor/` are still the only missing
pieces of the target layout.

```
Learning ─┐
          ├──→ problembank ──→ judge*, mentor*        (* not built yet)
Compete ──┘
```

The data model absorbed most of its outstanding fixes: `q_no` is unique (that was
a live 500), the oversized `CharField`s became `TextField`s, `expected_output`
arrived, `Submission` gained `code`/`lang`/verdict choices, and `TestCases` gained
`test_case_no` + `visiblity` — ordering and public/private, which the judge needs.

The problem bank is seeded with **10 problems (3 Easy / 4 Medium / 3 Hard) and 73
test cases**, expected outputs generated from reference solvers rather than
hand-typed, and spot-checked against 24 known answers.

Both problem pages now consume the real schema — description, input/output formats
with constraints, worked example, and difficulty pills colour-coded per the design
on both the list and the detail page.

**Still true: nothing executes code.** RUN, SUBMIT, and the guru remain simulated
in JavaScript. That's §1 and §2, and it's the whole ballgame.

---

## 0. Restructure

- [x] ~~Rename `Questions` app → **`Learning`**~~ — tables renamed in place, all
      rows preserved.
- [x] ~~Extract the data owner app~~ — landed as `problembank`.
- [x] ~~Rename the model `Questions` → `Problem`~~ — landed as `Problems`, still
      plural. Django convention is singular; low priority.
- [ ] Write `problembank/selectors.py` so `Learning` and `Compete` never reach into
      its ORM: `random_problem()`, `judge_cases_for(problem)`. **Not started** —
      `Learning/views.py` imports the models directly today.
- [ ] Namespace templates (`Learning/templates/Learning/…`). Still flat, so the
      first duplicate filename in another app silently wins.
- [x] ~~Seed command~~ — `problembank/management/commands/seed_problems.py`,
      idempotent, `--clear` supported.
- [ ] **Move to Postgres.** Still SQLite.
- [ ] App naming is inconsistent: `Home`, `Compete`, `Learning` are CapitalCase,
      `problembank` and `judge` are lowercase. Pick one.

### Model fixes

- [x] ~~`q_no` needs `unique=True`~~ — was a live 500 on duplicates.
- [x] ~~`q_content` → `TextField`~~ — now `q_description`.
- [x] ~~`TestCases.test_case` → `TextField`~~
- [x] ~~`TestCase.expected_output`~~
- [x] ~~`TestCase.is_sample`~~ — landed as `visiblity` (PUBLIC/PRIVATE), which is
      more expressive.
- [x] ~~`Submission.code` and `Submission.language`~~ — landed as `code` / `lang`.
- [x] ~~`Submission.verdict` → add `choices`~~
- [x] ~~Add `difficulty`~~ — with Easy/Medium/Hard choices matching the design.
- [ ] `date_published`: `DateField(default=datetime.now)` holds a `datetime` in
      memory and a `date` after reload. Use `date.today`. **Still open.**
- [ ] `__str__` on every model — admin still shows `Problems object (1)`, which is
      painful for hand-entering test cases.
- [ ] Rename the `q_id` FKs to `problem`. The column is `q_id_id`, and `tc.q_id`
      returns a model instance, not an id.
- [ ] Remaining fields: `acceptance`, `slug`, solved-by-user.
- [ ] Multiple tags per problem. `q_tag` is still one `CharField(30)`.

### New — found while seeding and wiring the pages

- [ ] **`visiblity` is missing an `i`.** Rename to `visibility` before more code
      references it; right now it's one field and one line in the seeder.
- [ ] **`Submission` can't represent an unjudged submission.** Async grading means
      the row exists before a verdict, but `default="WA"` makes every queued
      submission read as Wrong Answer, and `max_length=3` won't hold `"PENDING"`.
      Add a `PENDING`/`QUEUED` choice and widen the field.
- [ ] **`Submission` has nowhere for runtime and memory.** The verdict modal
      displays both plus tests-passed; without columns they can't survive a reload.
- [ ] `TestCases` has no `Meta.ordering`. `test_case_no` exists, but without a
      default ordering "case 3 failed" isn't stable between queries.
- [ ] `Problems.objects.all()` in `Learning.views.questions` has no `order_by`, so
      list order is whatever SQLite returns.
- [ ] The `# This will inclued Constrainsts` comment is on both `q_input_format`
      **and** `q_output_format` — copy-paste; constraints on an output format
      doesn't parse.
- [ ] `Learning/views.py` imports `JsonResponse`, `TestCases`, `Submission` and
      uses none of them.

---

## 1. Judge (`judge/`)

- [ ] **Decide what `judge/` is.** It's currently scaffolded as a Django app —
      `apps.py`, `models.py`, `migrations/`, `views.py`, `admin.py` — and is *not*
      in `INSTALLED_APPS`. The plan was a plain Python package with no models, so
      it stays testable without a database and can move to a queue worker or its
      own container later. Either delete the Django scaffolding or commit to it
      deliberately.
- [ ] **`judge/reference.py` is a verbatim copy of the seed command**, including its
      `BaseCommand` class and `problembank` imports. If the reference solvers are
      wanted as judge fixtures, extract just the solver functions; otherwise delete
      it. Two copies will drift.
- [ ] **Stub first.** `grade()` returning a hardcoded verdict, wired to a real POST
      handler, with the JS mocks deleted. This makes the whole request path real
      while only execution stays fake — and it decouples §2 from §3.
- [ ] `types.py`: `TestCase`, `CaseResult`, `Verdict`, `RunResult` as dataclasses.
- [ ] `grade(code, language, cases) -> Verdict` and `run_once(code, language, stdin)`.
- [ ] **Accept the POST.** The page already sends `action` (`submit`/`run`/`guru`),
      `code`, and `custom_input` to the current URL with a CSRF token. Nothing
      reads it.
- [ ] Return **JSON**, not page HTML.
- [ ] `SUBMIT`: full hidden suite → per-case pass/fail, runtime, memory, first
      failing case. `RUN`: one ad-hoc case, ungraded, real stdout/stderr/exit code.
- [ ] Grading is **async**. Poll or hold a websocket; don't block the request.
- [ ] Only mark solved / move stats on a genuine passing verdict.
- [ ] Delete `mockVerdict()` / `mockRunOutput()` / `mockGuruReply()` from
      `static/js/question_description.js`, plus the visible TEMPORARY note. All
      marked with `TODO(judge)`.
- [ ] Output comparison needs a normalization policy — trailing whitespace, final
      newline, line endings. The seeded fixtures have no trailing newline; decide
      before real submissions arrive.

### Sandbox — the dominant risk

- [ ] **Evaluate Judge0 or Piston before building this.** It's the one piece where
      not-invented-here costs weeks and a security incident.
- [ ] If building: `subprocess` + rlimits is a dev stopgap and *not* isolation.
      Docker-per-run is the realistic floor for anything public.
- [ ] Wall-clock timeout, CPU cap, memory cap, no network, non-root, read-only FS.
- [ ] Container lifecycle + cleanup on timeout.
- [ ] Queue (Celery/RQ) — you can't hold an HTTP request open for execution.

---

## 2. Mentor (`mentor/`)

- [ ] **The package doesn't exist yet.** Same shape as the judge: plain Python, no
      models, so `Compete` can't reach it by construction.
- [ ] `ask(problem, code, failing_case, history) -> reply`. Stateless.
- [ ] System prompt enforcing Socratic behaviour: ask questions, point at gaps,
      **never** emit working code.
- [ ] "ASK THE GURU" in the verdict modal must pass the **real** failing case and
      user code, not a canned string. Marked `TODO(mentor)`.
- [ ] Chat history per user + problem — a `GuruMessage` model in `Learning`.
- [ ] Two tone variants (encouraging vs. direct), per-account or A/B.
- [ ] `Compete` simply never imports `mentor`, so duels can't reach it.

---

## 3. Compete / duels

Currently `HttpResponse("This is Compete Page")`.

- [ ] Five states in one view: **idle → searching → matched → running → finished**.
- [ ] Idle: "NO HINTS. NO MENTOR. JUST THE CLOCK.", format, Elo, magenta FIND MATCH.
- [ ] Searching: pulsing ring, "SCANNING FOR OPPONENT_", rating range.
- [ ] Matched: opponent name/rating, brief loading pause.
- [ ] Running: 15:00 countdown, opponent progress bar (config-flagged), Problem +
      CodeSpace side by side, **no guru**.
- [ ] Finished: VICTORY / DEFEAT / TIME'S UP, Elo delta, FIND NEW MATCH + BACK TO HOME.
- [ ] Models: `Duel`, `DuelParticipant`, `EloHistory`. `DuelParticipant` points at
      `problembank.Submission` — never the reverse, so every arrow stays one-way.
- [ ] Channels setup: `ASGI_APPLICATION`, `CHANNEL_LAYERS` (Redis), `consumers.py`,
      `routing.py`, Daphne/Uvicorn in production.
- [ ] **The clock is server-authoritative.** A client-side countdown means every
      duel is winnable with devtools.
- [ ] Duel state in Redis with expiry; reconciliation when a player reconnects.
- [ ] Matchmaking that can't pair the same person twice under concurrency.
- [ ] Elo calculation + persistence. The nav badge is hardcoded `ELO 1450`.
- [ ] Match ends on an actual passing verdict, not on submit.

---

## 4. Profile

- [ ] Route `/profile`, reachable from a nav link **and** by clicking the Elo badge.
- [ ] Avatar initials, handle, rank tier, leaderboard position.
- [ ] 5-stat row: Elo, solved/total, win rate, duels played, streak.
- [ ] Difficulty breakdown with progress bars.
- [ ] Recent duels: opponent, problem, time ago, win/loss, Elo delta.

---

## 5. Problem pages — remaining UI

- [x] ~~Problem panel needs a worked example and constraints~~ — `q_sample_io`
      renders in a mono block; constraints ship inside `q_input_format`. Note the
      design asked for constraints as a *bullet list*; they're a mono block today.
- [x] ~~Restore the DIFFICULTY column~~ — outlined pill in the difficulty colour, on
      both the list and the detail header.
- [ ] **Pick one source of truth for the worked example.** `q_sample_io` is authored
      copy built from test case 1, and cases 1–2 are marked `PUBLIC` — so the
      `PUBLIC` flag currently has no consumer, and an authored example can silently
      disagree with the graded fixture. Either render public cases instead, or keep
      `q_sample_io` and show public cases from case 2 onward.
- [ ] ACCEPTANCE % and STATUS (SOLVED green / OPEN muted) columns — both need data
      the judge produces.
- [ ] TOGGLE LAYOUT: split (`1fr 1.3fr 0.9fr`) ⇄ stacked (`1.4fr 1fr`, currently
      hardcoded). Both rule sets already exist — it's a class swap, not new CSS.
- [ ] Seed the custom-input placeholder from the problem's sample input; it's
      hardcoded generic text.
- [ ] Persist editor contents per user + problem.
- [ ] Slug routes (`/problems/two-sum`) per the design, instead of `q_no`.
- [ ] `/questions/<non-numeric>/` returns **200** with plain-text "No Such Question
      Exist" — should be a real 404.

---

## 6. Auth

- [ ] `request.POST['key']` in `blogin` and `signin` raises `MultiValueDictKeyError`
      on a missing field. The `required` attributes are client-side only — curl or
      a devtools edit walks past them. Use `.get()` with a presence check.
- [ ] `AUTH_PASSWORD_VALIDATORS` is configured but bypassed: `create_user()` never
      consults it, so a 1-character password is accepted. Route signup through a
      form that calls `validate_password()`.
- [ ] Email isn't unique on Django's `User`. Matters once password reset exists.
- [ ] `GET /login/` returns a plain-text 200 ("Not a Valid Login") outside the design.

---

## 7. Site-wide

- [ ] **The contact form doesn't save.** `Home.models.Contact` exists and is
      migrated, but `contact()` only sets `sent=True` — nothing is written, and the
      form has no `phone` field the model requires.
- [ ] No mail backend, so nothing is sent either.
- [ ] About / Contact copy is placeholder text; replace it.
- [ ] **`README.md` still describes the app as `Questions`** and predates the
      `problembank` split — its structure section is out of date.
- [ ] **Rotate `SECRET_KEY` before the first deploy — it is in public git history.**
      `settings.py:23` holds the `django-insecure-` key `startproject` generated,
      and it was pushed in the initial commit. Harmless while this is a local dev
      project, but that key signs session cookies and password-reset tokens:
      deploy without replacing it and anyone reading the repo can forge either.
      Changing it later does not remove it from history, so the deployed value
      must simply be different. Move it to `.env` (gitignored) with a committed
      `.env.example`, alongside `DEBUG = False` and a populated `ALLOWED_HOSTS`.
- [ ] `collectstatic` + hashed filenames. Unversioned static is why a hard refresh
      is needed after every CSS change in development.
- [ ] No tests anywhere. The `judge` package is the natural place to start — pure
      functions, so its tests need no database. The seeded fixtures double as a
      grading corpus.
