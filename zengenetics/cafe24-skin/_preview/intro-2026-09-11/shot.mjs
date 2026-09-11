import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const file = process.argv[2], tag = process.argv[3];
const b = await chromium.launch();
const p = await b.newPage({ viewport:{width:390,height:844}, deviceScaleFactor:2 });
const errs=[]; p.on('pageerror',e=>errs.push(String(e).slice(0,180)));
await p.goto('file://'+file,{waitUntil:'load',timeout:90000});
await p.waitForTimeout(3500);
const g = await p.evaluate(()=>{
  const t=document.getElementById('track'), s=document.getElementById('stage');
  return {top:t.getBoundingClientRect().top+scrollY, span:t.offsetHeight-s.offsetHeight,
          docH:document.documentElement.scrollHeight, load:document.getElementById('load').textContent};
});
console.log(tag, JSON.stringify(g), 'err', errs.slice(0,3));
const marks=[0.04,0.20,0.36,0.52,0.68,0.84,0.97];
for(let i=0;i<marks.length;i++){
  await p.evaluate(y=>scrollTo(0,y), Math.round(g.top+g.span*marks[i]));
  await p.waitForTimeout(700);
  await p.screenshot({path:`/tmp/claude-0/seq/${tag}_${i}.png`});
}
await p.evaluate(y=>scrollTo(0,y), Math.round(g.top+g.span*0.20));
await p.waitForTimeout(600);
console.log('rewind', await p.evaluate(()=>document.getElementById('pn').textContent));
await b.close();
