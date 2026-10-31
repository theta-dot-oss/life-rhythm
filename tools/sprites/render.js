const { chromium } = require('playwright'); const fs=require('fs'); const path=require('path');
(async()=>{ const out=process.argv[2]; const man=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
 const b=await chromium.launch(); const pg=await b.newPage({viewport:{width:320,height:320}});
 for(const m of man){ for(let k=0;k<m.frames;k++){ const svg=fs.readFileSync(path.join(out,'svg',`${m.name}-${k}.svg`),'utf8');
   await pg.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
   await pg.screenshot({path:path.join(out,'svg',`${m.name}-${k}.png`),omitBackground:true,clip:{x:0,y:0,width:320,height:320}}); } }
 await b.close(); console.log('rendered'); })();
