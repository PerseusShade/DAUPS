import puppeteer from 'puppeteer';
import fs from 'fs/promises';
import fssync from 'fs';
import path from 'path';
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import { execSync } from 'child_process';

async function getLocale(lang) {
    const raw = await fs.readFile(path.resolve('docs/locales.json'), 'utf8');
    const locales = JSON.parse(raw);
    return locales[lang] ?? locales['en'];
}

async function getMdTitles(lang, locale) {
    const dir = path.resolve(`docs/${lang}`);
    const files = (await fs.readdir(dir)).filter(f => f.endsWith('.md'));
    return files.map(file => {
        const base = file.replace(/\.md$/, '');
        const [chap, ...words] = base.split('_');
        const name = words
            .map((w,i) => i===0
                ? w.charAt(0).toUpperCase()+w.slice(1).toLowerCase()
                : w.toLowerCase()
            ).join(' ');
        return { id: base, title: `${locale.chapter} ${chap} : ${name}` };
    });
}

async function genChapterPdfs(lang) {
    const logoDataURL = `data:image/png;base64,${fssync.readFileSync(path.resolve('docs/site/logo.png'),'base64')}`;
    const locale = await getLocale(lang);
    const mdTitles = await getMdTitles(lang, locale);
    const outDir = path.resolve(`docs/site/pdf/${lang}`);
    await fs.mkdir(outDir, { recursive: true });

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    const htmlUrl = `file://${path.resolve(`docs/site/${lang}.html`)}`;
    await page.goto(htmlUrl, { waitUntil:'load' });

    const ids = await page.evaluate(() => Array.from(document.querySelectorAll('main section')).map(s=>s.id));
    const chapters = ids.map(id => {
        const m = mdTitles.find(t=>t.id===id);
        return m ? m : { id, title:id };
    });

    for (const {id,title} of chapters) {
        await page.goto(htmlUrl, { waitUntil:'load' });
        await page.evaluate((sid, t)=> {
            const sec = document.getElementById(sid);
            const clone = sec.cloneNode(true);

            const h1 = document.createElement('h1');
            h1.textContent = t;
            h1.style.cssText = [
                'text-align:center',
                'font-size:2em',
                'font-weight:bold',
                'color:#224289',
                'margin:0',
                'margin-bottom:1em'
            ].join(';');

            Array.from(clone.querySelectorAll('a')).forEach(a => {
                a.setAttribute('target', '_blank');
            });

            document.body.innerHTML = '';
            document.body.appendChild(h1);
            document.body.appendChild(clone);
        }, id, title);

        await page.pdf({
            path: path.join(outDir, `${id}.pdf`),
            format: 'A4',
            printBackground: true,
            displayHeaderFooter: true,
            margin: { top:'1.1in', bottom:'1in', left:'1in', right:'1in' },
            headerTemplate: `
                <div style="
                    width:100%; font-size:12px; padding:0 1in;
                    display:flex; justify-content:space-between; align-items:center; color:#999;
                    margin-top:0.2in;">
                    <div style="display:flex;align-items:center;gap:10px">
                        <img src="${logoDataURL}" style="
                            height:24px; opacity:0.5;
                            filter:drop-shadow(0 0 1.5px rgba(0,0,0,0.6));"/>
                        <span style="font-weight:bold;font-size:14px;color:#666">DAUPS</span>
                    </div>
                    <span style="font-style:italic;opacity:0.6">${title}</span>
                </div>`,
            footerTemplate: `
                <div style="width:100%; font-size:12px; color:#999; padding:0 1in;
                                        display:flex; justify-content:space-between; align-items:center;">
                    <span style="opacity:0.5">PerseusShade</span>
                </div>`,
        });
        console.log(`✅ ${lang}/${id}.pdf`);
    }
    await browser.close();
    return chapters;
}

async function mergeAndBookmark(lang, chapters, locale) {
    const dir = path.resolve(`docs/site/pdf/${lang}`);
    const mergedPdf = await PDFDocument.create();

    const files = (await fs.readdir(dir)).filter(f=>f.endsWith('.pdf')).sort();
    const pageCounts = [];
    for (const f of files) {
        const bytes = await fs.readFile(path.join(dir,f));
        const donor = await PDFDocument.load(bytes);
        const pages = await mergedPdf.copyPages(donor, donor.getPageIndices());
        pages.forEach(p=>mergedPdf.addPage(p));
        pageCounts.push(pages.length);
    }

    const fontDoc = await mergedPdf.embedFont(StandardFonts.HelveticaBold);
    const fontDa    = await mergedPdf.embedFont(StandardFonts.HelveticaBold);
    const fontIt    = await mergedPdf.embedFont(StandardFonts.HelveticaOblique);

    const [model] = mergedPdf.getPages();
    const { width, height } = model.getSize();
    const cover = mergedPdf.insertPage(0, [width,height]);

    const startY = height / 2;

    const docText = locale.coverTop;
    const docSize = 32;
    const daupsText = 'DAUPS';
    const daupsSize = 40;
    const daupsWidth = fontDoc.widthOfTextAtSize(daupsText, daupsSize);
    const docWidth = fontDoc.widthOfTextAtSize(docText, docSize);
    cover.drawText(daupsText, {
        x: width/2 - daupsWidth/2,
        y: startY + 20,
        size: daupsSize,
        font: fontDoc,
        color: rgb(0.133,0.259,0.537),
    });
    cover.drawText(docText, {
        x: width/2 - docWidth/2,
        y: startY - 30,
        size: docSize,
        font: fontDoc,
        color: rgb(0.133,0.259,0.537),
    });

    cover.drawText(locale.madeBy, {
        x: 72, y:36, size:12,
        font: await mergedPdf.embedFont(StandardFonts.HelveticaOblique),
        color: rgb(0.6,0.6,0.6)
    });

    const tocPage = mergedPdf.insertPage(1, [width,height]);
    const fontH = await mergedPdf.embedFont(StandardFonts.HelveticaBold);
    tocPage.drawText(locale.toc, {
        x: width/2 - fontH.widthOfTextAtSize('Table des matières',20)/2,
        y: height - 72,
        size: 20,
        font: fontH,
        color: rgb(0.133,0.259,0.537),
        textAlign: 'center'
    });
    const font = await mergedPdf.embedFont(StandardFonts.Helvetica);
    let cursorY = height - 110;
    let cursorPage = 3;
    for (let i=0;i<chapters.length;i++){
        const t = chapters[i].title;
        tocPage.drawText(t, { x:72, y: cursorY, size:12, font, color:rgb(0,0,0) });
        tocPage.drawText(String(cursorPage), {
            x: width - 72 - font.widthOfTextAtSize(String(cursorPage),12),
            y: cursorY, size:12, font, color:rgb(0,0,0)
        });
        cursorY -= 20;
        cursorPage += pageCounts[i];
    }

    const end = mergedPdf.addPage([width,height]);
    const fontI = await mergedPdf.embedFont(StandardFonts.HelveticaOblique);
    const licPath = path.resolve(`docs/site/LICENCE/${lang}.md`);
    const lic = await fs.readFile(licPath, 'utf8');

    end.drawText(locale.madeBy, {
        x: width/2 - fontI.widthOfTextAtSize(locale.madeBy, 12)/2,
        y: height - 72,
        size: 12,
        font: fontI,
        color: rgb(0.6,0.6,0.6)
    });
    end.drawText(lic, {
        x: width/2 - (width-144)/2,
        y: height - 96,
        size: 8,
        font: fontI,
        color: rgb(0.4,0.4,0.4),
        maxWidth: width - 144,
        textAlign: 'justify',
        lineHeight: 12
    });

    const temp = path.join(dir, `${lang}_tmp.pdf`);
    await fs.writeFile(temp, await mergedPdf.save());
    let offset=1, info='';
    for(let i=0;i<chapters.length;i++){
        info+=[
            'BookmarkBegin',
            `BookmarkTitle: ${chapters[i].title}`,
            'BookmarkLevel: 1',
            `BookmarkPageNumber: ${2 + offset}`,
            ''
        ].join('\n');
        offset+=pageCounts[i];
    }
    const bm = path.join(dir,'bookmarks.txt');
    await fs.writeFile(bm, info, 'utf8');
    execSync(`pdftk "${temp}" update_info_utf8 "${bm}" output "${path.resolve(`docs/site/pdf/${lang}.pdf`)}"`);

    const finalBytes = await fs.readFile(path.resolve(`docs/site/pdf/${lang}.pdf`));
    const finalPdf = await PDFDocument.load(finalBytes);
    const allPages = finalPdf.getPages();
    const pf = await finalPdf.embedFont(StandardFonts.Helvetica);
    const tot = allPages.length;
    allPages.forEach((pg,i)=>{
        const { width } = pg.getSize();
        const txt = `${i+1}/${tot}`, tw=pf.widthOfTextAtSize(txt,9);
        pg.drawText(txt,{ x: width-72-tw, y:18, size:9, font:pf, color:rgb(0.4,0.4,0.4) });
    });
    await fs.writeFile(path.resolve(`docs/site/pdf/${lang}.pdf`), await finalPdf.save());

    await fs.rm(dir, {recursive:true, force:true});
    console.log(`✅ ${lang}.pdf généré`);
}

(async()=>{
    const langs = (await fs.readdir(path.resolve('docs'),{withFileTypes:true}))
        .filter(d=>d.isDirectory()&&d.name!=='site').map(d=>d.name);
    for(const lang of langs){
        const locale = await getLocale(lang);
        const chapters = await genChapterPdfs(lang);
        await mergeAndBookmark(lang, chapters, locale);
    }
    console.log('🏁 Terminé');
})();