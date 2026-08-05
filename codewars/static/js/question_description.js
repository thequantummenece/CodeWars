/* ==========================================================================
   Question detail — RUN / SUBMIT / AI Guru
   ==========================================================================

   Everything below POSTs to the current URL and then renders a SIMULATED
   result. No view reads these posts yet.

   TODO(judge): the judge is going into its own package, shared by Questions
   and Compete. When it lands:
     - have the POST target return JSON instead of the page HTML
     - `await response.json()` at each marked spot below
     - delete mockVerdict() / mockRunOutput() / mockGuruReply() entirely
     - render the real verdict, per-case results, stdout/stderr, exit code
     - grading is async (queued execution), so SUBMIT should poll or open a
       websocket for the result rather than assume it arrives in the response
   ========================================================================== */

(function () {
    'use strict';

    var codeForm = document.getElementById('codeForm');
    if (!codeForm) {
        return;
    }

    var codeEditor = document.getElementById('codeEditor');
    var customInput = document.getElementById('customInput');
    var runBtn = document.getElementById('runBtn');
    var guruForm = document.getElementById('guruForm');
    var guruInput = document.getElementById('guruInput');
    var guruThread = document.getElementById('guruThread');

    var verdictModal = document.getElementById('verdictModal');
    var verdictBox = document.getElementById('verdictBox');
    var verdictTitle = document.getElementById('verdictTitle');
    var verdictFail = document.getElementById('verdictFail');
    var caseList = document.getElementById('caseList');
    var askGuruBtn = document.getElementById('askGuruBtn');

    var runModal = document.getElementById('runModal');
    var termBody = document.getElementById('termBody');

    var TOTAL_CASES = 8;
    var lastVerdict = null;

    function csrfToken() {
        var field = codeForm.querySelector('[name=csrfmiddlewaretoken]');
        return field ? field.value : '';
    }

    /* ----------------------------------------------------------- transport */

    // Sends the payload to the current URL. The response is deliberately
    // ignored for now — see TODO(judge) at the top of this file.
    function post(payload) {
        var body = new FormData();
        body.append('csrfmiddlewaretoken', csrfToken());
        Object.keys(payload).forEach(function (key) {
            body.append(key, payload[key]);
        });

        return fetch(window.location.pathname, {
            method: 'POST',
            body: body,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).catch(function () {
            /* Network failure is non-fatal while results are simulated. */
        });
    }

    /* --------------------------------------------------------------- modal */

    function openModal(modal) {
        modal.hidden = false;
        document.body.classList.add('modal-open');
    }

    function closeModal(modal) {
        modal.hidden = true;
        document.body.classList.remove('modal-open');
    }

    document.addEventListener('click', function (event) {
        if (!event.target.closest('[data-close]')) {
            return;
        }
        var modal = event.target.closest('.modal');
        if (modal) {
            closeModal(modal);
        }
    });

    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') {
            return;
        }
        [verdictModal, runModal].forEach(function (modal) {
            if (modal && !modal.hidden) {
                closeModal(modal);
            }
        });
    });

    /* ---------------------------------------------------------- SIMULATION */
    /* Delete this whole block once the judge returns real results. */

    function mockVerdict() {
        var passed = Math.random() < 0.5
            ? TOTAL_CASES
            : Math.floor(Math.random() * TOTAL_CASES);

        return {
            accepted: passed === TOTAL_CASES,
            passed: passed,
            total: TOTAL_CASES,
            runtime: (20 + Math.floor(Math.random() * 90)) + ' ms',
            memory: (12 + Math.random() * 6).toFixed(1) + ' MB'
        };
    }

    function mockRunOutput(code, input) {
        var shown = input || '(example input)';
        var failed = Math.random() < 0.25;

        var lines = [
            '$ python solution.py --input ' + shown,
            'compiling...',
            'executing solve()...',
            ''
        ];

        if (failed) {
            lines.push('Traceback (most recent call last):');
            lines.push('  File "solution.py", line 2, in solve');
            lines.push('NameError: name \'result\' is not defined');
            lines.push('');
            lines.push('[process exited with code 1 in 0.08s]');
        } else {
            lines.push('[2, 7, 11, 15]');
            lines.push('');
            lines.push('[process exited with code 0 in 0.04s]');
        }

        return { lines: lines, failed: failed };
    }

    function mockGuruReply(verdict) {
        if (verdict && verdict.accepted) {
            return 'That passes. Now tell me the time complexity of what you wrote, ' +
                'and whether the nested loop is doing work you could avoid.';
        }
        if (verdict) {
            return 'Case ' + (verdict.passed + 1) + ' is the first one failing. ' +
                'Walk me through what your code returns for it, and where that ' +
                'diverges from what the problem asks for.';
        }
        return 'What have you tried so far, and what specifically is not behaving ' +
            'the way you expect?';
    }

    /* -------------------------------------------------------------- render */

    function renderVerdict(verdict) {
        var accepted = verdict.accepted;

        verdictBox.classList.toggle('panel--green', accepted);
        verdictBox.classList.toggle('panel--red', !accepted);
        verdictTitle.textContent = accepted ? 'ACCEPTED' : 'WRONG ANSWER';
        verdictTitle.className = 'verdict-title ' +
            (accepted ? 'verdict-title--pass' : 'verdict-title--fail');

        document.getElementById('vsTests').textContent = verdict.passed + '/' + verdict.total;
        document.getElementById('vsRuntime').textContent = verdict.runtime;
        document.getElementById('vsMemory').textContent = verdict.memory;

        caseList.innerHTML = '';
        for (var i = 0; i < verdict.total; i++) {
            var pass = i < verdict.passed;
            var item = document.createElement('li');
            item.className = 'case-row ' + (pass ? 'case-row--pass' : 'case-row--fail');
            item.innerHTML = '<span>CASE ' + (i + 1) + '</span><span>' +
                (pass ? 'PASS' : 'FAIL') + '</span>';
            caseList.appendChild(item);
        }

        if (accepted) {
            verdictFail.hidden = true;
        } else {
            verdictFail.hidden = false;
            verdictFail.textContent = 'First failure on case ' + (verdict.passed + 1) + '.';
        }
    }

    function renderTerminal(result) {
        termBody.innerHTML = '';
        result.lines.forEach(function (line) {
            var row = document.createElement('span');
            row.className = 'term-line';
            if (/^Traceback|^ {2}File|Error:/.test(line)) {
                row.classList.add('term-line--err');
            } else if (/exited with code 0/.test(line)) {
                row.classList.add('term-line--ok');
            } else if (/exited with code [1-9]/.test(line)) {
                row.classList.add('term-line--err');
            }
            row.textContent = line;
            termBody.appendChild(row);
        });

        var cursor = document.createElement('span');
        cursor.className = 'term-cursor';
        cursor.textContent = '$ ';
        termBody.appendChild(cursor);
    }

    function pushGuruMessage(text, who) {
        var bubble = document.createElement('p');
        bubble.className = 'guru-msg guru-msg--' + who;
        bubble.textContent = text;
        guruThread.appendChild(bubble);
        guruThread.scrollTop = guruThread.scrollHeight;
    }

    /* ------------------------------------------------------------- actions */

    codeForm.addEventListener('submit', function (event) {
        event.preventDefault();

        post({
            action: 'submit',
            code: codeEditor.value,
            custom_input: customInput.value
        });
        // TODO(judge): const verdict = await response.json();
        lastVerdict = mockVerdict();

        renderVerdict(lastVerdict);
        openModal(verdictModal);
    });

    runBtn.addEventListener('click', function () {
        post({
            action: 'run',
            code: codeEditor.value,
            custom_input: customInput.value
        });
        // TODO(judge): stream real stdout/stderr/exit code into the terminal.
        renderTerminal(mockRunOutput(codeEditor.value, customInput.value));
        openModal(runModal);
    });

    askGuruBtn.addEventListener('click', function () {
        closeModal(verdictModal);

        post({ action: 'guru', message: '[submission follow-up]' });
        // TODO(mentor): send the failing case + user code as context so the
        // reply is grounded in the real failure instead of a canned string.
        pushGuruMessage(mockGuruReply(lastVerdict), 'bot');
        guruInput.focus();
    });

    guruForm.addEventListener('submit', function (event) {
        event.preventDefault();

        var message = guruInput.value.trim();
        if (!message) {
            return;
        }

        pushGuruMessage(message, 'user');
        guruInput.value = '';

        post({ action: 'guru', message: message });
        // TODO(mentor): render the LLM's reply here instead of the canned hint.
        pushGuruMessage(mockGuruReply(null), 'bot');
    });
}());
