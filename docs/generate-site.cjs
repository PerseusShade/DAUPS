const fs = require('fs/promises');
const path = require('path');
const { getHighlighter } = require('shiki');
const MarkdownIt = require('markdown-it');

(async () => {
    const daupsTheme = JSON.parse(
        await fs.readFile(path.join(__dirname, '..', 'themes', 'daups-color-theme.json'), 'utf8')
    );
    const daupsGrammar = JSON.parse(
        await fs.readFile(path.join(__dirname, '..', 'syntaxes', 'daups-docs.tmLanguage.json'), 'utf8')
    );

    const highlighter = await getHighlighter({
        theme: daupsTheme,
        langs: [
            {
                id: 'daups-docs',
                scopeName: 'source.daups-docs',
                grammar: daupsGrammar,
            },
        ],
    });

    const md = new MarkdownIt({
        highlight(code, lang) {
            if (lang === 'daups-docs') {
                return highlighter.codeToHtml(code, { lang: 'daups-docs' });
            }
            return `<pre><code>${md.utils.escapeHtml(code)}</code></pre>`;
        },
    });

    const docsPath = __dirname;
    const outputBase = path.join(docsPath, 'site');
    await fs.mkdir(outputBase, { recursive: true });

    const entries = await fs.readdir(docsPath, { withFileTypes: true });
    const languageDirs = entries.filter(
        (dirent) => dirent.isDirectory() && dirent.name !== 'site'
    );

    for (const langDir of languageDirs) {
        const langName = langDir.name;
        const inputPath = path.join(docsPath, langName);
        const files = (await fs.readdir(inputPath))
            .filter((f) => f.endsWith('.md'))
            .sort();

        let sidebarLinks = '';
        let mainContent = '';

        for (const file of files) {
            const fullPath = path.join(inputPath, file);
            const raw = await fs.readFile(fullPath, 'utf8');
            const baseName = path.basename(file, '.md');
            const cleanTitle = baseName.replace(/^\d+_?/, '').replace(/_/g, ' ');
            const titleCapitalized = cleanTitle.charAt(0).toUpperCase() + cleanTitle.slice(1);

            sidebarLinks += `<div class="sidebar-link"><a href="#${baseName}">${titleCapitalized}</a></div>`;
            mainContent += `<section id="${baseName}">
                ${md.render(raw)}</section>
                <div class="separator"></div>`;
        }

        const downloadMenuHTML = languageDirs.map(ld => {
            const lang = ld.name;
            return `<div><a href="#" class="pdf-link" data-lang="${lang}">PDF (<i>${lang.toUpperCase()}</i>)</a></div>`;
        }).join('');

        const finalHtml = `<!DOCTYPE html>
<html lang="${langName}">
<head>
    <meta charset="UTF-8" />
    <title>Documentation DAUPS (${langName})</title>
    <link rel="icon" href="logo.png" type="image/svg+xml">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="logo-wrapper">
            <img src="logo.png" alt="Logo DAUPS" class="logo-img">
            <span class="logo-text">DAUPS Documentation</span>
        </div>
        <div class="controls">
            <!-- A faire plus tard, onlineshell
            <a href="https://todoonlineshell.com" target="_blank" class="play-button">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24" class="bi bi-play-circle"><circle cx="12" cy="12" r="10"/><path d="m10 8 6 4-6 4z"/></svg>
            </a>
            -->
            <a href="https://github.com/PerseusShade/DAUPS-docs" target="_blank" class="github-button" aria-label="GitHub">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-github" viewBox="0 0 16 16">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38
                    0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
                    -.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2
                    -3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21
                    2.2.82a7.65 7.65 0 0 1 2-.27c.68 0 1.36.09 2 .27 1.53-1.04
                    2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82
                    2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48
                    0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013
                    0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
            </a>

            <button id="download-btn" title="Télécharger">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4m4-5 5 5 5-5m-5 5V3"/></svg>
            </button>

            <label class="theme-switch">
                <input type="checkbox" id="theme-toggle" />
                <span class="slider"></span>
            </label>

            <select id="lang-select" class="lang-select" onchange="location.href=this.value + '.html'">
                ${languageDirs.map(ld => `<option value="${ld.name}" ${ld.name === langName ? 'selected' : ''}>${ld.name}</option>`).join('')}
            </select>
        </div>
    </header>

    <div class="page-wrapper">
        <button class="menu-toggle" id="menuToggle">
            <span></span>
            <span></span>
            <span></span>
        </button>

        <div class="menu-mask"></div>

        <div class="container">
            <aside class="sidebar">
                <div>
                    ${sidebarLinks}
                </div>
            </aside>
            <main>
                ${mainContent}
            </main>
        </div>
    </div>

    <script>
        // Restaurer le thème au chargement
        const savedTheme = localStorage.getItem('theme');
        const isDark = savedTheme === 'dark';
        document.documentElement.classList.toggle('dark', isDark);
        const themeToggleInput = document.getElementById('theme-toggle');
        if (themeToggleInput) themeToggleInput.checked = isDark;

        // Changement thème
        const themeToggle = document.getElementById('theme-toggle');
        themeToggle.addEventListener('change', () => {
            const dark = themeToggle.checked;
            document.documentElement.classList.toggle('dark', dark);
            localStorage.setItem('theme', dark ? 'dark' : 'light');
        });

        // Menu téléchargement
        const downloadBtn    = document.getElementById('download-btn');
        const downloadMenu = document.createElement('div');
        const downloadMenuHTML = ${JSON.stringify(
            '<div><a href="https://myextension.github.com" target="_blank">Extension</a></div>\n' + downloadMenuHTML
        )};
        downloadMenu.classList.add('download-menu');
        document.body.appendChild(downloadMenu);
        downloadMenu.innerHTML = downloadMenuHTML;
        downloadBtn.addEventListener('click', () => {
            const rect = downloadBtn.getBoundingClientRect();
            downloadMenu.style.display = 'block';
            const menuWidth = downloadMenu.offsetWidth;
            downloadMenu.style.left = (rect.right + window.scrollX - menuWidth) + 'px';
            downloadMenu.style.top    = (rect.bottom + window.scrollY) + 'px';
        });
        document.addEventListener('click', e => {
            if (!downloadBtn.contains(e.target) && !downloadMenu.contains(e.target))
                downloadMenu.style.display = 'none';
        });

        document.querySelectorAll('.pdf-link').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const lang = link.dataset.lang;
                try {
                    const response = await fetch(\`pdf/\${lang}.pdf\`);
                    if (!response.ok) throw new Error('Fichier introuvable');
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);

                    const a = document.createElement('a');
                    a.href = url;
                    a.download = \`\${lang}.pdf\`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } catch (e) {
                    console.error('Erreur lors du téléchargement du PDF:', e);
                    alert("Le fichier PDF n'a pas pu être téléchargé.");
                }
            });
        });

        // Sidebar & toggle
        const sidebar        = document.querySelector(".sidebar");
        const main             = document.querySelector("main");
        const menuToggle = document.getElementById("menuToggle");

        function collapseSidebar() {
            if (sidebar.classList.contains("collapsed")) return;
            menuToggle.classList.add("active");
            sidebar.classList.add("collapsed");
            void sidebar.offsetWidth;
            main.style.transition    = "margin-left 0.3s ease-in-out";
            main.style.marginLeft    = "0";
            setTimeout(() => main.style.transition = "", 300);
        }

        function openSidebar() {
            if (!sidebar.classList.contains("collapsed")) return;
            sidebar.classList.remove("collapsed");
            void sidebar.offsetWidth;
            main.style.transition    = "margin-left 0.3s ease-in-out";
            main.style.marginLeft    = "240px";
            menuToggle.classList.remove("active");
            setTimeout(() => main.style.transition = "", 300);
        }

        menuToggle.addEventListener("click", () => {
            if (sidebar.classList.contains("collapsed")) openSidebar();
            else                                                         collapseSidebar();
        });

        // IntersectionObserver
        const links     = document.querySelectorAll('.sidebar a');
        const sections = Array.from(document.querySelectorAll('main section'));
        const observer = new IntersectionObserver((entries) => {
            let vis = null;
            entries.forEach(e => { if (e.isIntersecting) vis = e.target; });
            if (vis) {
                const id = vis.id;
                links.forEach(l => l.classList.toggle('active', l.getAttribute('href') === \`#\${id}\`));
            }
        }, { root:null, rootMargin:'0px', threshold:0.6 });
        sections.forEach(s => observer.observe(s));

        document.addEventListener("DOMContentLoaded", () => {
            const opts = { root:null, rootMargin:'0px 0px -80% 0px', threshold:0 };
            const io = new IntersectionObserver((ents) => {
                ents.forEach(e => {
                    if (e.isIntersecting) {
                        const id = e.target.id;
                        document.querySelectorAll('.sidebar a')
                            .forEach(l => l.classList.toggle('active', l.getAttribute('href') === \`#\${id}\`));
                    }
                });
            }, opts);
            document.querySelectorAll('section').forEach(s => io.observe(s));
        });

        // Sur petits écrans, on ferme au clic sur un lien
        if (window.innerWidth <= 600) {
            document.querySelectorAll(".sidebar a").forEach(link =>
                link.addEventListener("click", collapseSidebar)
            );
        }
    </script>
</body>
</html>
`;

        await fs.writeFile(path.join(outputBase, `${langName}.html`), finalHtml, 'utf8');
    }

    console.log('✅ Conversion terminée dans le dossier docs/site');
})();
