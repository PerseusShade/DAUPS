const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js";

let pyodide = null;
let inputQueue = [];
let inputWaiters = [];
let runInProgress = false;
let stopRequested = false;
let terminalLastEndedWithNewline = true;

let autoScrollWhileTyping = false;
let userScrolled = false;
let lastUserScrollTime = 0;

const DOM = {
    terminal: null,
    output: null,
    runBtn: null,
    stopBtn: null,
    status: null,
    inputLine: null,
    cmdLine: null,
    blockCaret: null,
    cmdPrefix: null,
    editor: null,
    themeToggle: null,
    langSelect: null,
    downloadPaneBtn: null,
    paneFileInput: null,
    termBtn: null
};

const $ = sel => document.querySelector(sel);

let terminalLineCount = 0;

function appendOutput(s) {
    if (!DOM.output) return;
    const text = String(s);
    if (text.length === 0) {
        if (DOM.terminal) DOM.terminal.scrollTop = DOM.terminal.scrollHeight;
        return;
    }

    const pushNewLine = (txt) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'terminal-line';
        const num = document.createElement('div');
        num.className = 'line-num';
        terminalLineCount += 1;
        num.textContent = terminalLineCount;
        const content = document.createElement('div');
        content.className = 'line-content';
        content.appendChild(document.createTextNode(txt));
        wrapper.appendChild(num);
        wrapper.appendChild(content);
        DOM.output.appendChild(wrapper);
        terminalLastEndedWithNewline = (txt === "");
        return content;
    };

    const getLastContent = () => {
        const last = DOM.output.lastElementChild;
        return last ? last.querySelector('.line-content') : null;
    };

    let pos = 0;
    const N = text.length;
    while (pos < N) {
        const nlIdx = text.indexOf('\n', pos);
        if (nlIdx === -1) {
            let chunk = text.slice(pos);
            if (chunk.endsWith('\r')) chunk = chunk.slice(0, -1);
            if (chunk.length > 0) {
                const lastContent = getLastContent();
                if (terminalLastEndedWithNewline || !lastContent) {
                    pushNewLine(chunk);
                } else {
                    lastContent.appendChild(document.createTextNode(chunk));
                    terminalLastEndedWithNewline = false;
                }
            }
            break;
        } else {
            let chunk = text.slice(pos, nlIdx);
            if (chunk.endsWith('\r')) chunk = chunk.slice(0, -1);
            if (chunk.length > 0) {
                const lastContent = getLastContent();
                if (terminalLastEndedWithNewline || !lastContent) {
                    pushNewLine(chunk);
                } else {
                    lastContent.appendChild(document.createTextNode(chunk));
                    terminalLastEndedWithNewline = false;
                }
            }

            const nextIdx = nlIdx + 1;
            if (nextIdx < N && text[nextIdx] === '\n') {
                pushNewLine("");
                pos = nlIdx + 1;
            } else {
                terminalLastEndedWithNewline = true;
                pos = nlIdx + 1;
            }
        }
    }

    if (DOM.terminal) {
        DOM.terminal.getBoundingClientRect();
        DOM.terminal.scrollTop = DOM.terminal.scrollHeight;
    }
}

function clearTerminal() {
    if (!DOM.output) return;
    DOM.output.innerHTML = '';
    terminalLineCount = 0;
}

function renderTerminalFromString(fullText) {
    clearTerminal();
    const lines = String(fullText).split(/\r?\n/);
    lines.forEach(ln => {
        const wrapper = document.createElement('div');
        wrapper.className = 'terminal-line';
        const num = document.createElement('div');
        num.className = 'line-num';
        terminalLineCount += 1;
        num.textContent = terminalLineCount;
        const content = document.createElement('div');
        content.className = 'line-content';
        content.textContent = ln;
        wrapper.appendChild(num);
        wrapper.appendChild(content);
        DOM.output.appendChild(wrapper);
    });
    if (DOM.terminal) DOM.terminal.scrollTop = DOM.terminal.scrollHeight;
}

function updateEditorLineNumbers() {
    const editor = DOM.editor;
    const gutter = document.getElementById('editor-gutter');
    if (!editor || !gutter) return;
    const lines = (editor.value || '').split(/\r?\n/);
    let html = '';
    for (let i = 0; i < lines.length; i++) {
        html += `<div class="gutter-line">${i + 1}</div>`;
    }
    gutter.innerHTML = html;
}

function syncEditorScroll() {
    const editor = DOM.editor;
    const gutter = document.getElementById('editor-gutter');
    if (!editor || !gutter) return;
    gutter.scrollTop = editor.scrollTop;
}

function wireEditorLineNumbers() {
    if (!DOM.editor) return;
    updateEditorLineNumbers();
    DOM.editor.addEventListener('input', () => {
        updateEditorLineNumbers();
    });
    DOM.editor.addEventListener('scroll', () => {
        syncEditorScroll();
    });
}

function placeCaretAtEndContentEditable(el) {
    try {
        if (!el) return;
        el.focus();
        if (typeof window.getSelection !== "undefined" && typeof document.createRange !== "undefined") {
            const range = document.createRange();
            range.selectNodeContents(el);
            range.collapse(false);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
        }
    } catch (e) {}
}

let lastSelectionUpdate = 0;

function updateBlockCaret() {
    try {
        const block = DOM.blockCaret;
        const cmd = DOM.cmdLine;
        const term = DOM.terminal;
        const inputLine = DOM.inputLine;
        if (!block || !cmd || !term || !inputLine) return;

        if (inputLine.classList.contains("hidden")) {
            block.style.display = "none";
            return;
        }

        block.style.display = "inline-block";

        const sel = window.getSelection();
        if (!sel || sel.rangeCount === 0) placeCaretAtEndContentEditable(cmd);
        let range = sel && sel.rangeCount ? sel.getRangeAt(0).cloneRange() : null;
        if (!range) {
            range = document.createRange();
            range.selectNodeContents(cmd);
            range.collapse(false);
        }
        if (!range.collapsed) range.collapse(false);

        const marker = document.createElement("span");
        marker.textContent = "\u200b";
        try {
            range.insertNode(marker);
        } catch (e) {
            try { cmd.appendChild(marker); } catch (e2) {}
        }

        const markerRect = marker.getBoundingClientRect();
        const termRect = term.getBoundingClientRect();

        const markerOffsetLeft = markerRect.left - termRect.left + term.scrollLeft;
        const markerOffsetTop  = markerRect.top  - termRect.top  + term.scrollTop;

        if (autoScrollWhileTyping && !userScrolled) {
            const paddingRight = 12;
            const paddingLeft = 8;
            const viewLeft = term.scrollLeft;
            const viewRight = term.scrollLeft + term.clientWidth;

            if (markerOffsetLeft > viewRight - paddingRight) {
                term.scrollLeft = Math.max(0, markerOffsetLeft - term.clientWidth + paddingRight);
            } else if (markerOffsetLeft < viewLeft + paddingLeft) {
                term.scrollLeft = Math.max(0, markerOffsetLeft - paddingLeft);
            }
        }

        block.style.left = `${Math.max(0, Math.round(markerOffsetLeft))}px`;
        block.style.top  = `${Math.max(0, Math.round(markerOffsetTop))}px`;

        try { marker.remove(); } catch (e) {}

        placeCaretAtEndContentEditable(cmd);
        lastSelectionUpdate = performance.now();
    } catch (err) {
        console.warn("updateBlockCaret failed:", err);
        try { if (DOM.blockCaret) DOM.blockCaret.style.display = "none"; } catch(e) {}
    }
}

function showInputLine(promptText = "") {
    try {
        const out = DOM.output;
        if (!out || !DOM.inputLine || !DOM.cmdLine || !DOM.cmdPrefix || !DOM.blockCaret) {
            if (DOM.inputLine) DOM.inputLine.classList.remove("hidden");
            return;
        }

        autoScrollWhileTyping = true;
        userScrolled = false;

        DOM.cmdPrefix.textContent = promptText;
        const cmd = DOM.cmdLine;
        cmd.textContent = "";

        const lastWrapper = out.lastElementChild;
        const shouldInline = lastWrapper &&
            lastWrapper.classList &&
            lastWrapper.classList.contains('terminal-line') &&
            (() => {
                const c = lastWrapper.querySelector ? lastWrapper.querySelector('.line-content') : null;
                return c && String(c.textContent).length > 0;
            })();

        if (shouldInline) {
            const lastContent = lastWrapper.querySelector('.line-content');
            if (lastContent && DOM.inputLine.parentElement !== lastContent) {
                try { DOM.inputLine.remove(); } catch (e) {}

                (function trimTrailingTextNodeWhitespace(node) {
                    if (!node) return;
                    for (let i = node.childNodes.length - 1; i >= 0; i--) {
                        const child = node.childNodes[i];
                        if (child.nodeType === Node.TEXT_NODE) {
                            child.nodeValue = child.nodeValue.replace(/[\s\u00A0\u200B]+$/u, '');
                            return;
                        } else if (child.nodeType === Node.ELEMENT_NODE) {
                            trimTrailingTextNodeWhitespace(child);
                            const last = child.childNodes[child.childNodes.length - 1];
                            if (last && last.nodeType === Node.TEXT_NODE) return;
                        }
                    }
                })(lastContent);

                try { lastContent.appendChild(DOM.cmdPrefix); } catch(e) {}
                try { lastContent.appendChild(DOM.cmdLine); } catch(e) {}
                try { lastContent.appendChild(DOM.blockCaret); } catch(e) {}

                DOM.inputLine.dataset.inlined = "1";
                DOM.inputLine.style.display = "none";

                DOM.cmdPrefix.style.display = "inline";
                DOM.cmdLine.style.display = "inline";
                DOM.blockCaret.style.display = "inline-block";
            }
        } else {
            if (DOM.inputLine.parentElement !== DOM.terminal) {
                try { DOM.inputLine.remove(); } catch (e) {}
                try { DOM.terminal.appendChild(DOM.inputLine); } catch (e) {}
                delete DOM.inputLine.dataset.inlined;
                DOM.inputLine.style.display = "inline-block";
            }
        }

        DOM.inputLine.classList.remove("hidden");
        if (DOM.terminal) DOM.terminal.setAttribute('aria-disabled', 'false');
        if (DOM.blockCaret) DOM.blockCaret.style.display = "inline-block";

        if (DOM.terminal) {
            DOM.terminal.scrollLeft = Math.max(0, DOM.terminal.scrollWidth - DOM.terminal.clientWidth);
            DOM.terminal.scrollTop = DOM.terminal.scrollHeight;
        }

        placeCaretAtEndContentEditable(cmd);
        requestAnimationFrame(updateBlockCaret);

        if (!showInputLine._listenersAdded) {
            document.addEventListener("selectionchange", () => {
                if (DOM.inputLine && !DOM.inputLine.classList.contains("hidden")) updateBlockCaret();
            });
            try {
                DOM.cmdLine.addEventListener("input", () => {
                    autoScrollWhileTyping = true;
                    updateBlockCaret();
                });
                DOM.cmdLine.addEventListener("keydown", ev => {
                    if (ev.key.length === 1 && !ev.ctrlKey && !ev.metaKey) {
                        autoScrollWhileTyping = true;
                        userScrolled = false;
                    }
                    if (ev.key === "Enter") {
                        ev.preventDefault();
                        const val = DOM.cmdLine.textContent;
                        pushInput(val);

                        if (DOM.inputLine && DOM.inputLine.dataset && DOM.inputLine.dataset.inlined) {
                            try {
                                const parentContent = DOM.cmdLine.parentElement;
                                if (parentContent) {
                                    try { DOM.cmdPrefix.remove(); } catch(e) {}
                                    try { DOM.blockCaret.remove(); } catch(e) {}
                                    try { DOM.cmdLine.remove(); } catch(e) {}
                                    const textNode = document.createTextNode(val);
                                    parentContent.appendChild(textNode);

                                    if (DOM.terminal && autoScrollWhileTyping && !userScrolled) {
                                        DOM.terminal.scrollLeft = Math.max(0, DOM.terminal.scrollWidth - DOM.terminal.clientWidth);
                                    }

                                    appendOutput('\n');
                                } else {
                                    appendOutput(val + '\n');
                                }
                            } catch (e) {
                                appendOutput(val + '\n');
                            }
                        } else {
                            appendOutput(val + '\n');
                        }

                        try {
                            autoScrollWhileTyping = false;
                            userScrolled = false;
                            if (DOM.terminal) DOM.terminal.scrollLeft = 0;
                        } catch (e) {}

                        try { updateBlockCaret(); } catch (e) {}
                        hideInputLine();
                    } else if (ev.key === "Tab") {
                        ev.preventDefault();
                        document.execCommand('insertText', false, '    ');
                        updateBlockCaret();
                    } else {
                        setTimeout(updateBlockCaret, 0);
                    }
                });
            } catch (e) {
                console.warn("failed to attach cmd listeners:", e);
            }
            showInputLine._listenersAdded = true;
        }
    } catch (err) {
        console.error("showInputLine error:", err);
        try { if (DOM.inputLine) { DOM.inputLine.classList.remove("hidden"); DOM.inputLine.style.display = "inline-block"; } } catch(e) {}
    }
}

function hideInputLine() {
    try {
        if (DOM.inputLine && DOM.inputLine.dataset && DOM.inputLine.dataset.inlined) {
            try {
                try { DOM.cmdPrefix.remove(); } catch(e) {}
                try { DOM.cmdLine.remove(); } catch(e) {}
                try { DOM.blockCaret.remove(); } catch(e) {}

                DOM.inputLine.appendChild(DOM.cmdPrefix);
                DOM.inputLine.appendChild(DOM.cmdLine);
                DOM.inputLine.appendChild(DOM.blockCaret);

                if (DOM.inputLine.parentElement !== DOM.terminal) {
                    try { DOM.inputLine.remove(); } catch (e) {}
                    try { DOM.terminal.appendChild(DOM.inputLine); } catch (e) {}
                }

                delete DOM.inputLine.dataset.inlined;
                DOM.inputLine.style.display = "inline-block";
                DOM.cmdPrefix.style.display = "";
                DOM.cmdLine.style.display = "";
                DOM.blockCaret.style.display = "none";
            } catch (e) {
                try { DOM.inputLine.remove(); } catch(e) {}
                if (DOM.terminal) DOM.terminal.appendChild(DOM.inputLine);
                delete DOM.inputLine.dataset.inlined;
                DOM.inputLine.style.display = "inline-block";
            }
        }

        DOM.inputLine.classList.add("hidden");
        DOM.cmdPrefix.textContent = "";
        DOM.cmdLine.textContent = "";

        if (DOM.blockCaret) DOM.blockCaret.style.display = "none";

        if (DOM.terminal) {
            DOM.terminal.setAttribute('aria-disabled', 'true');
            try { DOM.terminal.blur(); } catch (e) {}
        }
    } catch (err) {
        console.error("hideInputLine error:", err);
        try { if (DOM.inputLine) DOM.inputLine.classList.add("hidden"); } catch(e) {}
    }
}

function pushInput(value) {
    if (inputWaiters.length > 0) {
        const waiter = inputWaiters.shift();
        try {
            waiter.resolve(value);
        } catch (e) {
            inputQueue.push(value);
        }
    } else {
        inputQueue.push(value);
    }
}

function rejectAllInputWaitersWithKeyboardInterrupt() {
    while (inputWaiters.length) {
        const waiter = inputWaiters.shift();
        try {
            if (waiter && typeof waiter.reject === 'function') {
                waiter.reject(new Error('KeyboardInterrupt'));
            } else if (typeof waiter === 'function') {
                waiter(Promise.reject(new Error('KeyboardInterrupt')));
            }
        } catch (e) {}
    }
    try { hideInputLine(); } catch(e) {}
}

function wireTerminalTyping() {
    const term = DOM.terminal;
    if (!term) return;

    term.addEventListener('scroll', () => {
        lastUserScrollTime = Date.now();
        setTimeout(() => {
            const age = Date.now() - lastUserScrollTime;
            if (age >= 30) {
                userScrolled = true;
                autoScrollWhileTyping = false;
            }
        }, 40);
    });

    term.addEventListener("keydown", ev => {
        const line = DOM.inputLine;
        const cmd = DOM.cmdLine;

        if (!line || line.classList.contains("hidden")) {
            if (ev.ctrlKey && ev.key.toLowerCase() === "c") {
                ev.preventDefault();
                ev.stopPropagation();
                if (runInProgress) {
                    appendOutput("^C\n");
                    try { hideInputLine(); } catch(e) {}
                    requestStop();
                }
            }
            return;
        }

        if (ev.key === "Backspace") {
            ev.preventDefault();
            const s = cmd.textContent;
            cmd.textContent = s.slice(0, -1);
            autoScrollWhileTyping = true;
            userScrolled = false;
            setTimeout(updateBlockCaret, 0);
        } else if (ev.key === "Enter") {
            ev.preventDefault();
            const val = cmd.textContent;
            pushInput(val);

            if (DOM.inputLine && DOM.inputLine.dataset && DOM.inputLine.dataset.inlined) {
                try {
                    const parentContent = DOM.inputLine.parentElement.closest('.terminal-line')?.querySelector('.line-content');
                    if (parentContent) {
                        parentContent.textContent = parentContent.textContent + val;

                        if (DOM.terminal && autoScrollWhileTyping && !userScrolled) {
                            DOM.terminal.scrollLeft = Math.max(0, DOM.terminal.scrollWidth - DOM.terminal.clientWidth);
                        }

                        appendOutput('\n');
                    } else {
                        appendOutput(val + '\n');
                    }
                } catch (e) {
                    appendOutput(val + '\n');
                }
            } else {
                appendOutput(val + '\n');
            }

            try {
                autoScrollWhileTyping = false;
                userScrolled = false;
                if (DOM.terminal) DOM.terminal.scrollLeft = 0;
            } catch (e) {}

            try { updateBlockCaret(); } catch (e) {}
            hideInputLine();
        } else if (ev.key === "Tab") {
            ev.preventDefault();
            document.execCommand('insertText', false, '    ');
            autoScrollWhileTyping = true;
            userScrolled = false;
            updateBlockCaret();
        } else if (ev.key.length === 1 && !ev.ctrlKey && !ev.metaKey) {
            ev.preventDefault();
            cmd.textContent += ev.key;
            autoScrollWhileTyping = true;
            userScrolled = false;
            setTimeout(updateBlockCaret, 0);
        } else if (ev.ctrlKey && ev.key.toLowerCase() === "c") {
            ev.preventDefault();
            ev.stopPropagation();
            if (runInProgress) {
                appendOutput("^C\n");
                try { hideInputLine(); } catch(e) {}
                requestStop();
            }
        } else {
            setTimeout(updateBlockCaret, 0);
        }
    });

    term.addEventListener("click", () => {
        if (DOM.inputLine && !DOM.inputLine.classList.contains("hidden")) {
            term.focus();
        }
    });
}

function requestStop() {
    stopRequested = true;

    try { hideInputLine(); } catch (e) {}

    try {
        const ib = window.__pyodide_interruptBuffer;
        if (ib && ib.length > 0) {
            ib[0] = 2;
            if (pyodide && typeof pyodide.checkInterrupt === 'function') {
                try { pyodide.checkInterrupt(); } catch(e) {}
            }
        }
    } catch(e){ console.warn("interrupt buffer write failed", e); }

    try {
        if (pyodide && pyodide.globals) pyodide.globals.set("__stop_requested", true);
    } catch(e){}

    try {
        if (pyodide) pyodide.runPythonAsync("__stop_requested = True").catch(()=>{});
    } catch(e){}

    try {
        rejectAllInputWaitersWithKeyboardInterrupt();
    } catch (e) {}
}

function clearStopRequest() {
    stopRequested = false;
    try {
        if (pyodide && pyodide.globals) pyodide.globals.set("__stop_requested", false);
    } catch (e) {}
}

const setStatus = s => { if (DOM.status) DOM.status.textContent = s; };

async function loadPyodideAndPackages() {
    setStatus("Loading Pyodide...");
    try {
        if (!window.loadPyodide) await import(PYODIDE_URL);
        pyodide = await window.loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/" });
    } catch (e) {
        console.error("Failed to load pyodide:", e);
        setStatus("Pyodide load failed");
        return;
    }
    let interruptBuffer = null;
    if (typeof SharedArrayBuffer !== "undefined") {
        try {
            interruptBuffer = new Int32Array(new SharedArrayBuffer(4));
            pyodide.setInterruptBuffer(interruptBuffer);
            console.log("Interrupt buffer set");
        } catch (e) {
            console.warn("SharedArrayBuffer / setInterruptBuffer not available", e);
            interruptBuffer = null;
        }
    } else {
        console.warn("SharedArrayBuffer not available in this environment");
    }

    window.__pyodide_interruptBuffer = interruptBuffer;
    setStatus("Pyodide loaded, loading interpreter...");
    try {
        const resp = await fetch("../basic.py");
        const basicSrc = await resp.text();
        function js_write(s) {
            setTimeout(() => appendOutput(String(s)), 0);
        }
        async function js_await_input(prompt = "") {
            try { showInputLine(prompt); } catch (e) {}
            try {
                if (pyodide && typeof pyodide.checkInterrupt === "function") {
                    pyodide.checkInterrupt();
                }
            } catch (e) {
                try { hideInputLine(); } catch (e2) {}
                throw e;
            }
            if (inputQueue.length > 0) {
                const v = inputQueue.shift();
                try { hideInputLine(); } catch (e) {}
                return v;
            }
            return await new Promise((resolve, reject) => {
                 inputWaiters.push({ resolve, reject });
            }).then(value => {
                try { hideInputLine(); } catch (e) {}
                return value;
            });
        }
        pyodide.globals.set("__js_write", js_write);
        pyodide.globals.set("__js_await_input", js_await_input);
        try { pyodide.globals.set("__stop_requested", false); } catch (e) {}
        await pyodide.runPythonAsync(basicSrc);
        setStatus("Interpreter ready");
        if (DOM.runBtn) DOM.runBtn.disabled = false;
        if (DOM.stopBtn) DOM.stopBtn.disabled = true;
    } catch (e) {
        console.error("Failed to initialize interpreter:", e);
        setStatus("Interpreter init failed");
    }
}

async function handleRun() {
    if (!pyodide || runInProgress) return;
    runInProgress = true;
    DOM.runBtn.disabled = true;
    if (DOM.stopBtn) DOM.stopBtn.disabled = false;
    setStatus("Running...");
    clearTerminal();
    hideInputLine();
    const code = DOM.editor.value;
    try {
        inputQueue = [];
        inputWaiters = [];
        clearStopRequest();
        try { if (pyodide && pyodide.globals) pyodide.globals.set("__stop_requested", false); } catch (e) {}
        const pyCode = `
result, error = await run_async('<web>', ${JSON.stringify(code)})
if error:
    try:
            __js_write(error.as_string())
    except Exception:
            print(error.as_string())
`;
        await pyodide.runPythonAsync(pyCode);
    } catch (err) {
        appendOutput(`JS Error: ${err}\n`);
    } finally {
        runInProgress = false;
        DOM.runBtn.disabled = false;
        if (DOM.stopBtn) DOM.stopBtn.disabled = true;
        setStatus("Ready");
        try { if (pyodide && pyodide.globals) pyodide.globals.set("__stop_requested", false); } catch (e) {}
    }
}

function handleStop() {
    if (!runInProgress) return;
    setStatus("Stop requested...");
    appendOutput("\n");
    requestStop();
    if (DOM.stopBtn) DOM.stopBtn.disabled = true;
    try {
        if (pyodide && pyodide.globals && pyodide.globals.has && pyodide.globals.has("on_stop_requested")) {
            pyodide.runPythonAsync("on_stop_requested()").catch(()=>{});
        }
    } catch (e) {}
}

function wireUI() {
    if (DOM.runBtn) DOM.runBtn.addEventListener('click', handleRun);
    if (DOM.stopBtn) DOM.stopBtn.addEventListener('click', handleStop);
    wireTerminalTyping();
    document.addEventListener("keydown", e => {
        if (e.ctrlKey && e.key.toLowerCase() === "i") showInputLine();
    });
    if (DOM.terminal) {
        DOM.terminal.addEventListener("dblclick", (e) => {
            if (DOM.inputLine && !DOM.inputLine.classList.contains('hidden')) {
                DOM.terminal.focus();
            } else {
                e.preventDefault();
            }
        });
    }
    if (DOM.editor) {
        DOM.editor.addEventListener("keydown", e => {
            if (e.key === "Enter" && e.shiftKey) {
                e.preventDefault();
                handleRun();
            } else if (e.key === "Tab") {
                e.preventDefault();
                const textarea = DOM.editor;
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const value = textarea.value;

                const lineStart = value.lastIndexOf('\n', Math.max(0, start - 1)) + 1;
                const beforeLine = value.slice(0, lineStart);
                const selectedFromLineStart = value.slice(lineStart, end);
                const after = value.slice(end);

                const spacesToNextMultipleOf4 = (n) => (Math.floor(n / 4) + 1) * 4 - n;
                const spacesToPrevMultipleOf4 = (n) => {
                    const target = Math.max(0, Math.floor((n - 1) / 4) * 4);
                    return n - target;
                };

                if (e.shiftKey) {
                    if (selectedFromLineStart.includes("\n")) {
                        const lines = selectedFromLineStart.split(/\r?\n/);
                        const removes = [];

                        for (let i = 0; i < lines.length; i++) {
                            const m = lines[i].match(/^ */);
                            const n = m ? m[0].length : 0;
                            const rem = spacesToPrevMultipleOf4(n);
                            removes.push(rem);
                            lines[i] = lines[i].slice(rem);
                        }

                        const newSelected = lines.join("\n");
                        textarea.value = beforeLine + newSelected + after;

                        const totalRemoved = removes.reduce((a, b) => a + b, 0);
                        const removedBeforeStart = removes[0];
                        textarea.selectionStart = Math.max(0, start - removedBeforeStart);
                        textarea.selectionEnd = Math.max(textarea.selectionStart, end - totalRemoved);
                    } else {
                        const lineRest = value.slice(lineStart, start);
                        const mTrailing = lineRest.match(/ *$/);
                        const trailingSpaces = mTrailing ? mTrailing[0].length : 0;
                        const rem = Math.min(4, trailingSpaces);
                        if (rem > 0) {
                            const newBefore = value.slice(0, start - rem);
                            const newAfter = value.slice(start);
                            textarea.value = newBefore + newAfter;
                            textarea.selectionStart = textarea.selectionEnd = start - rem;
                        } else {
                            textarea.selectionStart = textarea.selectionEnd = start;
                        }
                    }
                } else {
                    if (selectedFromLineStart.includes("\n")) {
                        const lines = selectedFromLineStart.split(/\r?\n/);
                        const adds = [];

                        for (let i = 0; i < lines.length; i++) {
                            const m = lines[i].match(/^ */);
                            const n = m ? m[0].length : 0;
                            const add = spacesToNextMultipleOf4(n);
                            adds.push(add);
                            lines[i] = " ".repeat(add) + lines[i];
                        }

                        const newSelected = lines.join("\n");
                        textarea.value = beforeLine + newSelected + after;

                        const totalInserted = adds.reduce((a, b) => a + b, 0);
                        textarea.selectionStart = start + adds[0];
                        textarea.selectionEnd = end + totalInserted;
                    } else {
                        const insert = "    ";
                        textarea.value = value.slice(0, start) + insert + value.slice(end);
                        textarea.selectionStart = textarea.selectionEnd = start + insert.length;
                    }
                }
                updateEditorLineNumbers();
            }
        });
    }
}

function wireHeaderAndPaneControls() {
    const editorEl = DOM.editor;
    if (editorEl) {
        const suggestions = {
            en: "Write your code here...",
            fr: "Écrivez votre code ici..."
        };

        const pageLang = (document.documentElement.lang || "").toLowerCase();
        const chosen = pageLang.startsWith("fr") ? suggestions.fr
                    : pageLang.startsWith("en") ? suggestions.en
                    : Math.random() < 0.5 ? suggestions.en : suggestions.fr;

        const current = editorEl.value || "";
        if (Object.values(suggestions).some(s => current.trim() === s)) {
            editorEl.value = "";
        }

        editorEl.setAttribute("placeholder", chosen);
    }
    const applyTheme = mode => {
        if (mode === 'dark') {
            document.documentElement.classList.add('dark');
            if (DOM.themeToggle) DOM.themeToggle.checked = true;
        } else {
            document.documentElement.classList.remove('dark');
            if (DOM.themeToggle) DOM.themeToggle.checked = false;
        }
    };
    try {
        const saved = localStorage.getItem('daups_theme');
        if (saved) applyTheme(saved);
        else applyTheme(document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    } catch (e) {}
    if (DOM.themeToggle) {
        DOM.themeToggle.addEventListener('change', ev => {
            const mode = ev.target.checked ? 'dark' : 'light';
            applyTheme(mode);
            try { localStorage.setItem('daups_theme', mode); } catch (e) {}
        });
    }
    if (DOM.langSelect) {
        DOM.langSelect.addEventListener('change', ev => {
            const lang = ev.target.value;
            const baseUrl = window.location.origin + window.location.pathname.replace(/\/(fr|en)\/$/, '/');
            window.location.href = baseUrl + lang + '/';
        });
    }
    function saveAsFile(content, filename = 'code.daups') {
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
    }
    if (DOM.downloadPaneBtn) {
        DOM.downloadPaneBtn.addEventListener('click', () => {
            if (!editorEl) return;
            const content = editorEl.value || "";
            const firstLine = (content.split(/\r?\n/).find(l => l.trim().length > 0) || '').trim();
            const safeName = firstLine ? firstLine.replace(/[^a-z0-9_\-]/ig, '_').slice(0, 40) : '';
            const filename = (safeName ? safeName + '.daups' : 'code.daups');
            saveAsFile(content, filename);
        });
    }
    if (DOM.paneFileInput) {
        DOM.paneFileInput.addEventListener('change', ev => {
            const file = ev.target.files && ev.target.files[0];
            if (!file) return;
            const name = file.name.toLowerCase();
            if (!(name.endsWith('.daups') || name.endsWith('.txt'))) {
                alert('Format non supporté — choisissez un fichier .daups ou .txt');
                DOM.paneFileInput.value = '';
                return;
            }
            const reader = new FileReader();
            reader.onload = e => {
                const text = e.target.result || "";
                if (editorEl) {
                    editorEl.value = text;
                    editorEl.focus();
                    setStatus(`Fichier chargé : ${file.name}`);
                    updateEditorLineNumbers();
                }
                DOM.paneFileInput.value = '';
            };
            reader.onerror = () => {
                alert('Erreur de lecture du fichier');
                DOM.paneFileInput.value = '';
            };
            reader.readAsText(file, 'utf-8');
        });
    }
    if (DOM.termBtn) {
        DOM.termBtn.addEventListener('click', () => {
            clearTerminal();
            setStatus('Terminal vidé');
        });
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    DOM.terminal = $("#terminal");
    DOM.output = $("#output");
    DOM.runBtn = $("#runBtn");
    DOM.stopBtn = $("#stopBtn");
    DOM.status = $("#status");
    DOM.inputLine = $("#input-line");
    DOM.cmdLine = $("#cmd-line");
    DOM.blockCaret = $("#block-caret");
    DOM.cmdPrefix = $("#cmd-prefix");
    DOM.editor = document.getElementById("editor");
    DOM.themeToggle = document.getElementById('theme-toggle');
    DOM.langSelect = document.getElementById('lang-select');
    DOM.downloadPaneBtn = document.querySelector('.download-pane');
    DOM.paneFileInput = document.querySelector('.pane-file-input');
    DOM.termBtn = document.querySelector('.terminal-action');

    wireUI();
    wireHeaderAndPaneControls();
    wireEditorLineNumbers();

    setStatus("Preparing...");
    await loadPyodideAndPackages();
    setStatus("Ready");
});
