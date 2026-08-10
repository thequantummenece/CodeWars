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
not a Django app. **Still true: nothing executes code.** RUN, SUBMIT, and the guru remain
simulated in JavaScript. That's §1 and §2, and it's the whole ballgame.

```
learning ─┐
          ├──→ problembank ──→ judge*, mentor*        (* not built yet)
compete ──┘
```

---

## 0. Restructure — remaining

- [ ] **`fetch_random_problem` still crashes on a difficulty with no problems.**
      The guard reads `if q_no is None`, but `q_no` is built with `list(...)`, so
      an empty result is `[]` — never `None`. The check never fires and
      `random.choice([])` raises a bare `IndexError`. Needs `if not q_no:`.
      Note the values are case-sensitive: `"easy"` matches nothing, `"Easy"` does.
- [ ] **Add the test-case selector** — `fetch_judge_cases(problem)` ordered by
      `test_case_no`, and a public-only variant. Deliberately deferred until the
      judge's `types.py` fixes what shape a case needs to be in; the judge is the
      consumer, so it should decide. `TestCases` is imported in `selectors.py` but
      unused until then.
- [ ] **Move to Postgres.** Still SQLite.
- [ ] Rename the model `Problems` → `Problem`. Django convention is singular;
      low priority.

### Model fixes

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
- [ ] `date_published`: `DateField(default=datetime.now)` holds a `datetime` in
      memory and a `date` after reload. Use `date.today`.
- [ ] `__str__` on every model — admin still shows `Problems object (1)`, which is
      painful for hand-entering test cases.
- [ ] Rename the `q_id` FKs to `problem`. The column is `q_id_id`, and `tc.q_id`
      returns a model instance, not an id.
- [ ] Remaining fields: `acceptance`, `slug`, solved-by-user.
- [ ] Multiple tags per problem. `q_tag` is still one `CharField(30)`.
- [ ] The `# This will inclued Constrainsts` comment is on both `q_input_format`
      **and** `q_output_format` — copy-paste; constraints on an output format
      doesn't parse.

---

## 1. Judge (`judge/`)

**Settled: `judge/` is a plain Python package, not a Django app.** The `apps.py`,
`models.py`, `migrations/`, `views.py`, `admin.py` scaffolding is deleted and it
stays out of `INSTALLED_APPS` — so it's testable without a database and can move
to a queue worker or its own container later. `core.py` exists but is empty.

- [ ] **`judge/reference.py` is a verbatim copy of the seed command**, including its
      `BaseCommand` class and `problembank` imports. That import is now a
      dependency pointing the wrong way — a plain package reaching into a Django
      app. If the reference solvers are wanted as judge fixtures, extract just the
      solver functions; otherwise delete it. Two copies will drift.
- [ ] **Stub first.** `grade()` returning a hardcoded verdict, wired to a real POST
      handler, with the JS mocks deleted. This makes the whole request path real
      while only execution stays fake — and it decouples §2 from §3. `core.py` is
      the natural home and is currently empty.
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

- [ ] **The repo root is still `C:\Comding\python\CodeWars`** — rename to
      `ByteBrawl`, and rename the GitHub remote (`thequantummenece/CodeWars`) to
      match. Can't be done from a shell or editor running inside the folder; close
      them first. Cosmetic — nothing in the code reads the path.
- [ ] **The contact form doesn't save.** `home.models.Contact` exists and is
      migrated, but `contact()` only sets `sent=True` — nothing is written, and the
      form has no `phone` field the model requires.
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
- [ ] No tests anywhere. The `judge` package is the natural place to start — pure
      functions, so its tests need no database. The seeded fixtures double as a
      grading corpus. `problembank/tests.py` is still an empty `startapp` stub;
      the selectors are the other obvious candidate, since they now carry the
      ordering and not-found rules.
- [ ] Branch names must be kebab-case per the naming standard —
      `feature/judge_implementation` should be `feature/judge-implementation`.
      No upstream is tracking it yet, so `git branch -m` is enough.
