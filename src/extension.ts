import * as vscode from 'vscode';
import * as path from 'path';

let userDefinedFunctions = new Set<string>();
let scopedVariables = new Map<string, Set<string>>();

const functionCallDecorationType = vscode.window.createTextEditorDecorationType({ color: '#DCDCAA' });
const variableDecorationType = vscode.window.createTextEditorDecorationType({ color: '#9CDCFE' });
const unusedVariableDecorationType = vscode.window.createTextEditorDecorationType({ opacity: '0.5', fontStyle: 'italic' });

export function activate(context: vscode.ExtensionContext) {
    context.subscriptions.push(
        vscode.commands.registerCommand('daups.runDaups', runDaups),
        vscode.languages.registerCompletionItemProvider('daups', { provideCompletionItems }, ' '),
        vscode.languages.registerHoverProvider('daups', { provideHover }),
        vscode.languages.registerDefinitionProvider('daups', { provideDefinition }),
        vscode.workspace.onDidChangeTextDocument(handleDocumentChange),
        vscode.workspace.onDidOpenTextDocument(handleDocumentOpen),
        vscode.window.onDidChangeActiveTextEditor(handleEditorChange)
    );

    const activeEditor = vscode.window.activeTextEditor;
    if (activeEditor?.document.languageId === 'daups') {
        refresh(activeEditor.document);
    }
}

export function deactivate() {}

function runDaups() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No file is open');
        return;
    }
    const extensionPath = vscode.extensions.getExtension('PerseusShade.daups')?.extensionPath;
    const pythonScriptPath = path.join(extensionPath!, 'interpreter', 'basic.py');
    const cmd = `python "${pythonScriptPath}" "${editor.document.uri.fsPath}"`;

    let terminal = vscode.window.terminals.find(t => t.name === 'DAUPS Runner');
    if (!terminal) {
        terminal = vscode.window.createTerminal('DAUPS Runner');
    }

    terminal.show();
    terminal.sendText(cmd);
}

function provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
    const lineText = document.lineAt(position).text;
    const hashIndex = lineText.indexOf('#');

    if (hashIndex !== -1 && position.character > hashIndex) {
        return [];
    }

    const completions: vscode.CompletionItem[] = [];

    const pushItems = (words: string[], kind: vscode.CompletionItemKind, insert?: (w: string) => vscode.SnippetString) =>
        words.forEach(w => {
            const item = new vscode.CompletionItem(w, kind);
            if (insert) {
                item.insertText = insert(w);
            }
            completions.push(item);
        });

    pushItems(['Algo', 'Begin', 'End', 'function', 'if', 'then', 'else', 'for', 'to', 'downto', 'while', 'return'], vscode.CompletionItemKind.Keyword);
    pushItems(['int', 'float', 'bool', 'str', 'array'], vscode.CompletionItemKind.TypeParameter);
    pushItems(['print', 'get', 'run'], vscode.CompletionItemKind.Function, fn => new vscode.SnippetString(`${fn} $0`));
    pushItems(['create_array', 'SQRT', 'nombreAleatoire', 'size'], vscode.CompletionItemKind.Function, fn => new vscode.SnippetString(`${fn}($0)`));
    pushItems([...userDefinedFunctions], vscode.CompletionItemKind.Function, fn => new vscode.SnippetString(`${fn}($0)`));

    const varsInScope = scopedVariables.get(getScopeAtPosition(document, position)) ?? new Set();
    varsInScope.forEach(v => completions.push(new vscode.CompletionItem(v, vscode.CompletionItemKind.Variable)));

    const snippetMap = {
        'Algo': new vscode.SnippetString("Algo\n    $0\nBegin\n    \nEnd"),
        'Begin': new vscode.SnippetString("Begin\n    $0\nEnd"),
        'End': 'End',
        'function': new vscode.SnippetString("function $1\n    Begin\n        $0\n    End")
    };

    for (const [label, insertText] of Object.entries(snippetMap)) {
        const existing = completions.find(c => c.label === label);
        if (existing) {
            existing.insertText = insertText;
            existing.kind = vscode.CompletionItemKind.Snippet;
            existing.detail = 'Snippet';
        } else {
            const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
            item.insertText = insertText;
            item.detail = 'Snippet';
            completions.push(item);
        }
    }

    return completions;
}

function handleDocumentChange(event: vscode.TextDocumentChangeEvent) {
    if (event.document.languageId === 'daups') {
        refresh(event.document);
    }
}

function handleDocumentOpen(doc: vscode.TextDocument) {
    if (doc.languageId === 'daups') {
        refresh(doc);
    }
}

function handleEditorChange(editor: vscode.TextEditor | undefined) {
    if (editor?.document.languageId === 'daups') {
        refresh(editor.document);
    }
}

function refresh(document: vscode.TextDocument) {
    updateFunctionList(document);
    updateVariableScopes(document);
    updateDecorations(document);
}

function provideHover(document: vscode.TextDocument, position: vscode.Position) {
    const wordRange = document.getWordRangeAtPosition(position);
    const word = document.getText(wordRange);

    for (const [scope, vars] of scopedVariables.entries()) {
        if (vars.has(word)) {
            return new vscode.Hover(`Variable **${word}**\n\n\`\`\`daups-hover\n${word} : ${getVariableType(document, word)}\n\`\`\``);
        }
    }

    if (userDefinedFunctions.has(word)) {
        const { signature, doc } = getFunctionInfo(document, word);
        return new vscode.Hover(`\`${signature}\`\n\n${doc}`);
    }

    if (builtinDocs.has(word)) {
        const doc = builtinDocs.get(word);
        return new vscode.Hover(`\`\`\`daups-hover\nBuiltInFunction ${word}\n\`\`\`\n\n${doc}`);
    }

    return undefined;
}

function provideDefinition(document: vscode.TextDocument, position: vscode.Position) {
    const wordRange = document.getWordRangeAtPosition(position);
    const word = document.getText(wordRange);
    const lines = document.getText().split(/\r?\n/);

    for (let i = 0; i < lines.length; i++) {
        if (lines[i].match(new RegExp(`^\\s*function\\s+${word}\\s*\\(`))) {
            const start = new vscode.Position(i, lines[i].indexOf('function'));
            const end = new vscode.Position(i, lines[i].length);
            return new vscode.Location(document.uri, new vscode.Range(start, end));
        }
    }
    return undefined;
}

function getVariableType(doc: vscode.TextDocument, varName: string): string {
    for (const line of doc.getText().split(/\r?\n/)) {
        const match = line.match(new RegExp(`\\b${varName}\\b.*:\\s*(int|float|bool|str|array)`));
        if (match) {
            return match[1];
        }
    }
    return 'inconnu';
}

function getFunctionInfo(doc: vscode.TextDocument, fnName: string): { signature: string, doc: string } {
    for (const line of doc.getText().split(/\r?\n/)) {
        const match = line.trim().match(new RegExp(`^function\\s+(${fnName})\\s*\\(([^)]*)\\)\\s*(?::\\s*(\\w+))?\\s*(#.*)?$`));
        if (match) {
            const [_, name, args, returnType, comment] = match;
            const formattedArgs = args.split(',').map(arg => `    ${arg.trim()}`).join('\n');
            const returnText = returnType ? `: ${returnType}` : '  # La fonction ne retourne rien';
            return {
                signature: `\`\`\`daups-hover\nfunction ${name} (\n${formattedArgs}\n)${returnText}\n\`\`\``,
                doc: comment?.replace('#', '').trim() ?? ''
            };
        }
    }
    return { signature: '', doc: '_Fonction non trouvée._' };
}

const builtinDocs = new Map<string, string>([
    ["print", "Accepts any number of arguments.\n\nDisplays the provided arguments on the screen."],
    ["get", "Accepts one argument — a variable.\n\nAssigns the value entered by the user to the specified variable."],
    ["SQRT", "Accepts one argument — a number.\n\nReturns the square root of the provided number."],
    ["create_array", "Accepts multiple arguments — integers.\n\nCreates an array with the specified length, initializing it with the given values."],
    ["size", "Accepts one argument — a variable.\n\nReturns the size (length) of the specified variable."],
    ["nombreAleatoire", "Accepts two arguments — integers.\n\nReturns a random integer between the specified range (inclusive)."]
]);

function updateFunctionList(doc: vscode.TextDocument) {
    userDefinedFunctions.clear();
    const regex = /\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;
    for (const match of doc.getText().matchAll(regex)) {
        userDefinedFunctions.add(match[1]);
    }
}

function updateVariableScopes(doc: vscode.TextDocument) {
    scopedVariables.clear();
    let currentScope = 'global';
    const lines = doc.getText().split(/\r?\n/);

    for (const line of lines) {
        const trimmed = line.trim();
        const fnMatch = trimmed.match(/^function\s+(\w+)\s*\(([^)]*)\)/);
        if (fnMatch) {
            currentScope = fnMatch[1];
            const paramVars = Array.from(fnMatch[2].matchAll(/\b([a-zA-Z_][a-zA-Z0-9_]*)\s*:/g)).map(m => m[1]);
            scopedVariables.set(currentScope, new Set(paramVars));
            continue;
        }
        if (trimmed === 'End') {
            currentScope = 'global';
        }

        const declMatch = trimmed.match(/^([a-zA-Z0-9_,\s]+):\s*(int|float|bool|str|array)/);
        if (declMatch) {
            const vars = declMatch[1].split(',').map(v => v.trim());
            if (!scopedVariables.has(currentScope)) {
                scopedVariables.set(currentScope, new Set());
            }
            vars.forEach(v => scopedVariables.get(currentScope)!.add(v));
        }
    }
}

function getScopeAtPosition(doc: vscode.TextDocument, position: vscode.Position): string {
    const lines = doc.getText().split(/\r?\n/);
    let currentScope = 'global';

    for (let i = 0; i <= position.line; i++) {
        const line = lines[i].trim();
        const match = line.match(/^function\s+(\w+)/);
        if (match) {
            currentScope = match[1];
        }
        else if (line === 'End') {
            currentScope = 'global';
        }
    }
    return currentScope;
}

function updateDecorations(doc: vscode.TextDocument) {
    const editor = vscode.window.visibleTextEditors.find(e => e.document === doc);
    if (!editor) {
        return;
    }

    const text = doc.getText();
    const commentMatches = Array.from(text.matchAll(/"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|#.*$/gm));
    const isInCommentOrString = (idx: number) => commentMatches.some(({ index, 0: match }) => idx >= index! && idx < index! + match.length);

    const findAllMatches = (term: string) =>
        Array.from(text.matchAll(new RegExp(`\\b${term}\\b`, 'g')))
            .filter(m => !isInCommentOrString(m.index!));

    const functionRanges = [...userDefinedFunctions].flatMap(fn =>
        findAllMatches(fn).map(m => ({
            range: new vscode.Range(doc.positionAt(m.index!), doc.positionAt(m.index! + fn.length))
        }))
    );

    const variableRanges: vscode.DecorationOptions[] = [];
    const unusedRanges: vscode.DecorationOptions[] = [];

    scopedVariables.forEach((vars, scope) => {
        vars.forEach(v => {
            const matches = findAllMatches(v);
            const relevant = matches.filter(m => getScopeAtPosition(doc, doc.positionAt(m.index!)) === scope);
            if (relevant.length > 0) {
                variableRanges.push(...relevant.map(m => ({
                    range: new vscode.Range(doc.positionAt(m.index!), doc.positionAt(m.index! + v.length))
                })));
            }
            if (matches.length <= 1 && matches[0]) {
                const start = doc.positionAt(matches[0].index!);
                const end = doc.positionAt(matches[0].index! + v.length);
                unusedRanges.push({ range: new vscode.Range(start, end) });
            }
        });
    });

    editor.setDecorations(functionCallDecorationType, functionRanges);
    editor.setDecorations(variableDecorationType, variableRanges);
    editor.setDecorations(unusedVariableDecorationType, unusedRanges);
}