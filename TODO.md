# BYTE//BRAWL — TODO

Outstanding work in dependency order. See [README.md](README.md) for what already
works and where things live.

**Two things dominate everything else: the sandbox and the websocket layer.**
Everything in §0 is cleanup measured in hours; those two are weeks. Don't let
progress on the first feel like progress on the second.

Status: the §0 restructure landed (`learning` + `problembank` split, tables
renamed in place, 10 problems / 73 test cases seeded), the project is
**BYTE//BRAWL** everywhere, and `problembank` is now a real data owner —
`selectors.py` is in place and `learning/views.py` goes through it instead of the
ORM. Templates are namespaced per app (`learning/questions.html`), so no bare
name is shadowable. `judge/` has been committed to as a **plain Python package**,
not a Django app. RUN has been removed from the frontend entirely (`325683f`).
**Still true: nothing executes code.** SUBMIT and the guru remain simulated in
JavaScript. That's §1 and §2, and it's the whole ballgame.

```
learning ─┐
          ├──→ problembank ──→ judge*, mentor*        (* not built yet)
compete ──┘
```

---

## 0. Restructure — remaining

- [x] **`fetch_random_problem` still crashes on a difficulty with no problems.**
      The guard reads `if q_no is None`, but `q_no` is built with `list(...)`, so
      an empty result is `[]` — never `None`. The check never fires and
      `random.choice([])` raises a bare `IndexError`. Needs `if not q_no:`.
      Note the values are case-sensitive: `"easy"` matches nothing, `"Easy"` does.
- [x] **Add the test-case selector** — `fetch_judge_cases(problem)` ordered by
      `test_case_no`, and a public-only variant. Deliberately deferred until the
      judge's `types.py` fixes what shape a case needs to be in; the judge is the
      consumer, so it should decide. `TestCases` is imported in `selectors.py` but
      unused until then. *Done: `fetch_judge_cases(problem)` and
      `fetch_public_judge_cases(problem)` return `judge.types.TestCase` lists.*
- [ ] **Move to Postgres.** Still SQLite.
- [ ] Rename the model `Problems` → `Problem`. Django convention is singular;
      low priority.

### Model fixes

- [x] **`visiblity` is missing an `i`.** Rename to `visibility` before more code
      references it; right now it's one field and one line in the seeder.
- [x] **`Submission.verdict` has `default="WA"`, so any row missing a verdict
      reads as Wrong Answer.** Settled (see §1): rows are written only *after*
      grading finishes, so there is no unjudged row to represent — drop the
      default outright rather than adding a `PENDING` choice or a `status`
      column. With no default, code that forgets to set a verdict raises instead
      of silently recording a wrong answer. `max_length=3` is correct as-is;
      every verdict code fits. *Done (`0004`). Correction: dropping the default
      alone does **not** raise — Django gives a `CharField` an implicit `""`
      default, so a forgotten verdict would save as `""`. A `CheckConstraint`
      (`submission_verdict_valid`) now makes it raise `IntegrityError`.*
- [x] **`Submission` has nowhere for runtime and memory.** The verdict modal
      displays both plus tests-passed; without columns they can't survive a reload.
      *Done (`0004`): nullable `runtime_ms` and `memory_kb`. Tests-passed has no
      column yet.*
- [x] `TestCases` has no `Meta.ordering`. `test_case_no` exists, but without a
      default ordering "case 3 failed" isn't stable between queries.
- [x] `date_published`: `DateField(default=datetime.now)` holds a `datetime` in
      memory and a `date` after reload. Use `date.today`.
- [x] `__str__` on every model — admin still shows `Problems object (1)`, which is
      painful for hand-entering test cases.
- [x] Rename the `q_id` FKs to `problem`. The column is `q_id_id`, and `tc.q_id`
      returns a model instance, not an id. *Done (`0003`): only `TestCases.q_id`
      was an FK — `Submission` already used `problem`. `Problems.q_id` is the
      PK, not an FK, and keeps its name.*
- [ ] Remaining fields: `acceptance`, `slug`, solved-by-user.
- [ ] Multiple tags per problem. `q_tag` is still one `CharField(30)`.
- [x] The `# This will inclued Constrainsts` comment is on both `q_input_format`
      **and** `q_output_format` — copy-paste; constraints on an output format
      doesn't parse.

---

## 1. Judge (`judge/`)

**Settled: `judge/` is a plain Python package, not a Django app.** The `apps.py`,
`models.py`, `migrations/`, `views.py`, `admin.py` scaffolding is deleted and it
stays out of `INSTALLED_APPS` — so it's testable without a database and can move
to a queue worker or its own container later. `core.py` holds the `grade()` stub.

**Settled: the submission lifecycle.** SUBMIT hands the code to a task scheduler
(Celery) and returns immediately. While the task is in flight the browser shows a
**pending** state driven by the task's own status. When the worker finishes, the
verdict is written to `Submission` and the result is rendered. A `Submission` row
therefore only ever exists *with* a real verdict — in-flight state belongs to the
scheduler, not the database, which is why §0 drops the verdict default instead of
adding `PENDING`.

**Settled: RUN is gone from the frontend** (`325683f`) — removed, not stubbed.
It needs arbitrary stdin, and nothing in the schema describes what valid stdin
for a problem is (`q_input_format` is prose with constraints inlined). It comes
back once the sandbox exists and there's a machine-readable input spec to check
against; at that point it's the easier of the two paths — one execution, no
comparison, no verdict, no `Submission` row.

- [x] **`judge/reference.py` is a verbatim copy of the seed command**, including its
      `BaseCommand` class and `problembank` imports. That import is now a
      dependency pointing the wrong way — a plain package reaching into a Django
      app. If the reference solvers are wanted as judge fixtures, extract just the
      solver functions; otherwise delete it. Two copies will drift.
      *Done: `judge/reference.py` now holds only the solver functions; the seed
      command imports them from there (problembank → judge, arrow points down).*
- [ ] **Stub first.** `grade()` returning a hardcoded verdict, wired to a real POST
      handler, with the JS mocks deleted. This makes the whole request path real
      while only execution stays fake — and it decouples §2 from §3. `core.py` is
      the natural home and is currently empty.
      *Partial: `core.grade()` exists as a stub (always `WA`, never executes
      code, so it cannot mark anything solved). POST wiring and deleting the JS
      mocks are still open.*
- [x] `types.py`: `TestCase`, `CaseResult`, `Verdict` as dataclasses. `RunResult`
      waits for RUN to come back.
- [ ] `grade(code, language, cases) -> Verdict`. `run_once()` is deferred with RUN.
      *Signature and stub in `core.py`; real execution waits on the sandbox.*
- [ ] **Accept the POST.** The page sends `action` and `code` to the current URL
      with a CSRF token. Nothing reads it.
- [ ] **Switch the request body to JSON.** It's `multipart/form-data` today, so
      every value arrives as a string. With JSON the CSRF token moves from a form
      field to the `X-CSRFToken` header — `csrfToken()` already reads it out of
      the DOM, so the helper is unchanged.
- [ ] **Decide where problem identity comes from.** The URL already carries it
      (`<int:question_id>` → `q_no`) and the view can trust that. Recommend *not*
      accepting `q_no`/`q_id` in the body: two sources of truth for one fact, one
      of them client-controlled, means a POST to `/questions/1/` carrying
      `q_no: 9` has to be adjudicated — and getting it wrong credits an easy
      problem's fixtures against a hard problem. Note `q_id` (PK) and `q_no`
      (unique int, the routing key) are different fields; sending both invites
      them to disagree.
- [ ] Allowlist `action` server-side — reject anything but `submit` with a 400,
      which is where RUN actually gets closed off. Allowlist `language` the same
      way rather than passing it through to the sandbox.
- [ ] Return **JSON**, not page HTML.
- [ ] `SUBMIT`: full hidden suite → per-case pass/fail, runtime, memory, first
      failing case.
- [ ] Grading is **async** via Celery. Poll or hold a websocket; don't block the
      request.
- [ ] **The verdict modal needs a third state.** It has green ACCEPTED and red
      WRONG ANSWER; pending needs a neutral in-flight look. The guru panel already
      has the vocabulary — `pulse-dot` plus a `STANDBY`-style label — so it's
      existing CSS, not new design.
- [ ] **In-flight state lives in Celery, not the database** — the direct
      consequence of writing `Submission` only on completion. Two things follow,
      neither solved: a user who reloads mid-grade can't find their running
      submission (the task id was only ever in JS memory), and attempts that die
      in a crashed worker are never recorded, so the `acceptance` denominator in
      §0 undercounts. Decide whether a lost in-flight submission is an annoyance
      or data loss before this ships.
- [ ] Only mark solved / move stats on a genuine passing verdict.
- [ ] Delete `mockVerdict()` / `mockGuruReply()` from
      `static/js/question_description.js`, plus the visible TEMPORARY note. Both
      marked with `TODO(judge)`. (`mockRunOutput()` went with RUN.)
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
- [ ] **Celery** — settled as the scheduler; you can't hold an HTTP request open
      for execution. Needs a broker (Redis) and a worker process alongside the
      web server.

---

## 2. Mentor (`mentor/`)

- [ ] **The package doesn't exist yet.** Same shape as the judge: plain Python, no
      models, so `compete` can't reach it by construction.
- [ ] `ask(problem, code, failing_case, history) -> reply`. Stateless.
- [ ] System prompt enforcing Socratic behaviour: ask questions, point at gaps,
      **never** emit working code.
- [ ] "ASK THE GURU" in the verdict modal must pass the **real** failing case and
      user code, not a canned string. Marked `TODO(mentor)`.
- [ ] Chat history per user + problem — a `GuruMessage` model in `learning`.
- [ ] Two tone variants (encouraging vs. direct), per-account or A/B.
- [ ] `compete` simply never imports `mentor`, so duels can't reach it.

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

- [ ] **Pick one source of truth for the worked example.** `q_sample_io` is authored
      copy built from test case 1, and cases 1–2 are marked `PUBLIC` — so the
      `PUBLIC` flag currently has no consumer, and an authored example can silently
      disagree with the graded fixture. Either render public cases instead, or keep
      `q_sample_io` and show public cases from case 2 onward.
- [ ] Constraints ship inside `q_input_format` as a mono block; the design asked
      for a *bullet list*.
- [ ] ACCEPTANCE % and STATUS (SOLVED green / OPEN muted) columns — both need data
      the judge produces.
- [ ] TOGGLE LAYOUT: split (`1fr 1.3fr 0.9fr`) ⇄ stacked (`1.4fr 1fr`, currently
      hardcoded). Both rule sets already exist — it's a class swap, not new CSS.
- [ ] Persist editor contents per user + problem.
- [ ] Slug routes (`/problems/two-sum`) per the design, instead of `q_no`.
- [x] `/questions/<non-numeric>/` returns **200** with plain-text "No Such Question
      Exist" — should be a real 404. *Done: the route is now `<int:question_id>`,
      so non-numeric ids 404 in the resolver; unknown ids already 404 via
      `get_object_or_404`.*

---

## 6. Auth

- [x] `request.POST['key']` in `blogin` and `signin` raises `MultiValueDictKeyError`
      on a missing field. The `required` attributes are client-side only — curl or
      a devtools edit walks past them. Use `.get()` with a presence check.
      *Done: missing fields redirect home with an error message.*
- [x] `AUTH_PASSWORD_VALIDATORS` is configured but bypassed: `create_user()` never
      consults it, so a 1-character password is accepted. Route signup through a
      form that calls `validate_password()`.
      *Done without a form: `signin` calls `validate_password()` directly before
      `create_user()` and shows the errors as a message, like the other errors.*
- [ ] Email isn't unique on Django's `User`. Matters once password reset exists.
- [ ] `GET /login/` returns a plain-text 200 ("Not a Valid Login") outside the design.

---

## 7. Site-wide

- [ ] **The repo root is still `C:\Comding\python\CodeWars`** — rename to
      `ByteBrawl`, and rename the GitHub remote (`thequantummenece/CodeWars`) to
      match. Can't be done from a shell or editor running inside the folder; close
      them first. Cosmetic — nothing in the code reads the path.
- [x] **The contact form doesn't save.** `home.models.Contact` exists and is
      migrated, but `contact()` only sets `sent=True` — nothing is written, and the
      form has no `phone` field the model requires.
      *Done: `contact()` saves a `Contact` (subject is prepended to `content`,
      the model has no subject column); `phone` is now `blank=True`
      (`home` `0002`). Missing name/email/message shows an error, saves nothing.*
- [ ] No mail backend, so nothing is sent either.
- [ ] About / Contact copy is placeholder text; replace it.
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
- [ ] **Orphaned CSS from the RUN removal.** `.term*` (`style.css:1228-1305`) and
      `.custom-input` (`:960-978`) have no markup referencing them. Left in place
      deliberately — authored design work RUN will need again — but it's dead
      until then.
- [ ] No tests anywhere. The `judge` package is the natural place to start — pure
      functions, so its tests need no database. The seeded fixtures double as a
      grading corpus. `problembank/tests.py` is still an empty `startapp` stub;
      the selectors are the other obvious candidate, since they now carry the
      ordering and not-found rules.
- [ ] Branch names must be kebab-case per the naming standard —
      `feature/judge_implementation` should be `feature/judge-implementation`.
      No upstream is tracking it yet, so `git branch -m` is enough.
