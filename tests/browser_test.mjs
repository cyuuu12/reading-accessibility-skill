#!/usr/bin/env node
/* V2.3.2 真实浏览器验收：Node 内置 WebSocket + Chrome DevTools Protocol，零第三方依赖。 */
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath, pathToFileURL} from 'node:url';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(HERE,'..');
const OUT=path.join(HERE,'browser_artifacts');
fs.mkdirSync(OUT,{recursive:true});
const demo=path.join(HERE,'demo_reader_v232.html');
if(!fs.existsSync(demo))throw new Error('请先生成 tests/demo_reader_v232.html');
const candidates=[process.env.CHROME_PATH,'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'].filter(Boolean);
const chrome=candidates.find(p=>fs.existsSync(p));
if(!chrome)throw new Error('未找到 Chrome/Edge，可通过 CHROME_PATH 指定');
const port=9400+(process.pid%300);
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'reader-v232-'));
const proc=spawn(chrome,[`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'--headless=new','--disable-gpu','--no-sandbox','--no-first-run','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ws,seq=0;const pending=new Map(),errors=[];
async function connect(){
  for(let i=0;i<80;i++){
    try{const pages=await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();const page=pages.find(p=>p.type==='page');if(page){ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true})});return}}catch{}
    await sleep(100);
  }
  throw new Error('无法连接 Chrome DevTools');
}
function send(method,params={}){
  return new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.text+' '+(r.exceptionDetails.exception?.description||''));return r.result.value}
async function navigate(file){await send('Page.navigate',{url:pathToFileURL(file).href});for(let i=0;i<60;i++){if(await evaluate('document.readyState')==='complete'&&await evaluate('!!document.querySelector("#root")')){await sleep(120);return}await sleep(50)}throw new Error('页面加载超时')}
async function click(selector,index=0){
  const rect=await evaluate(`(()=>{const e=document.querySelectorAll(${JSON.stringify(selector)})[${index}];if(!e)return null;e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2,visible:r.width>0&&r.height>0}})()`);
  if(!rect||!rect.visible)throw new Error('不可点击: '+selector);
  await send('Input.dispatchMouseEvent',{type:'mousePressed',x:rect.x,y:rect.y,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:rect.x,y:rect.y,button:'left',clickCount:1});await sleep(280);
}
async function key(key,code=key,virtualKey=0){await send('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode:virtualKey});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode:virtualKey});await sleep(100)}
async function select(id,value){await evaluate(`(()=>{const e=document.getElementById(${JSON.stringify(id)});e.value=${JSON.stringify(value)};e.dispatchEvent(new Event('change',{bubbles:true}))})()`);await sleep(280)}
async function screenshot(name){const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(OUT,name),Buffer.from(r.data,'base64'))}
const results=[];function test(name,ok,detail=''){results.push({name,status:ok?'通过':'失败',detail});console.log(`[${ok?'通过':'失败'}] ${name}${ok?'':' '+JSON.stringify(detail)}`)}
function rgb(s){const m=String(s).match(/[\d.]+/g);return m?m.slice(0,3).map(Number):[0,0,0]}
function lum(c){return c.map(v=>{v/=255;return v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4)}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0)}
function contrast(a,b){const x=lum(rgb(a)),y=lum(rgb(b));return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)}

try{
  await connect();
  ws.addEventListener('message',ev=>{const m=JSON.parse(ev.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(new Error(m.error.message)):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails)});
  await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
  await navigate(demo);
  test('浏览器无脚本异常',errors.length===0,errors);
  const initial=await evaluate(`(()=>{const f=document.querySelector('.block[data-pri="精读"]'),s=document.querySelector('.block[data-pri="速览"]'),r=f.closest('.region'),d=document.querySelector('.skip-fold');return {focusBg:getComputedStyle(f).backgroundColor,focusBorder:getComputedStyle(r).borderLeftWidth,focusColor:getComputedStyle(f).color,strong:[...f.querySelectorAll('strong')].map(x=>({weight:getComputedStyle(x).fontWeight,color:getComputedStyle(x).color,text:x.textContent})),skimColor:getComputedStyle(s).color,skimWeight:getComputedStyle(s).fontWeight,skimBg:getComputedStyle(s).backgroundColor,skimText:s.textContent,skimExpected:DATA.segments.flatMap(x=>x.blocks).find(x=>x.priority==='速览').text,bodyColor:getComputedStyle(document.body).color,folds:document.querySelectorAll('.skip-fold').length,skipOpen:d.open,preview:d.querySelector('.skip-preview').textContent,previewVisible:d.querySelector('.skip-preview').getClientRects().length>0,regions:document.querySelectorAll('.region').length,blocks:document.querySelectorAll('.block').length,perSegmentButtons:document.querySelectorAll('.segfoot').length,originalButtons:document.querySelectorAll('#origAll').length}})()`);
  test('精读暖底/3-4px边框计算样式生效',initial.focusBg==='rgb(255, 242, 233)'&&initial.focusBorder==='3px',initial);
  test('精读仅局部strong加粗且深色强调',initial.strong.length===2&&initial.strong.every(x=>x.weight==='700'&&x.color==='rgb(168, 67, 31)'),initial.strong);
  test('速览为清晰基准态且不丢字',initial.skimColor===initial.bodyColor&&initial.skimWeight==='400'&&initial.skimBg==='rgba(0, 0, 0, 0)'&&initial.skimText===initial.skimExpected,initial);
  test('速览正文对比度≥4.5:1',contrast(initial.skimColor,'rgb(255,255,255)')>=4.5,contrast(initial.skimColor,'rgb(255,255,255)'));
  test('相邻同类合并区域且跳读跨段合并',initial.regions<initial.blocks&&initial.folds===1,{regions:initial.regions,blocks:initial.blocks,folds:initial.folds});
  test('跳读预览关闭时可见',!initial.skipOpen&&initial.previewVisible&&initial.preview.length>0,initial.preview);
  const previewScope=await evaluate(`DATA.segments.flatMap(s=>s.blocks).filter(b=>b.priority==='跳读').map(b=>({preview:b.preview,text:b.text}))`);
  test('跳读预览只描述区域范围',JSON.stringify(previewScope.map(x=>x.preview))===JSON.stringify(['《红楼梦》第117回原文引文','霍克思英译原文'])&&previewScope.every(x=>x.preview.length<=20&&x.preview!==x.text),previewScope);
  const regionStart=await evaluate(`(()=>{const r=document.querySelector('.region');const s=getComputedStyle(r);return {gap:s.marginTop,shadow:s.boxShadow,border:s.borderLeftWidth}})()`);
  test('区域起点有10px间隙且无卡片阴影',regionStart.gap==='10px'&&regionStart.shadow==='none',regionStart);
  const blockIntegrity=await evaluate(`({texts:entries.every(e=>e.block.text===DATA.segments.find(s=>s.seg_no===e.segNo).blocks.find(b=>b.text===e.block.text).text&&(!visible(document.querySelector('[data-block-id="'+e.id+'"]'))||document.querySelector('[data-block-id="'+e.id+'"]').textContent===e.block.text)),paragraphs:DATA.original_text.split(/\\n\\s*\\n/).length,segments:DATA.segments.length})`);
  test('辅助正文逐字一致且段落数量不变',blockIntegrity.texts&&blockIntegrity.paragraphs===blockIntegrity.segments,blockIntegrity);
  test('无逐段原文按钮，仅全局切换',initial.perSegmentButtons===0&&initial.originalButtons===1);
  await screenshot('01-light-initial.png');

  await click('.skip-fold summary');
  test('点击跳读可展开完整原文',await evaluate(`document.querySelector('.skip-fold').open&&document.querySelector('.skip-fold').textContent.includes('karma')`));
  await click('.skip-fold summary');
  await click('#expandAll');
  test('全部展开与按钮状态一致',await evaluate(`[...document.querySelectorAll('.skip-fold')].every(x=>x.open)&&document.getElementById('expandAll').textContent==='恢复折叠'`));
  await click('#expandAll');
  test('恢复折叠与按钮状态一致',await evaluate(`[...document.querySelectorAll('.skip-fold')].every(x=>!x.open)&&document.getElementById('expandAll').textContent==='全部展开'`));

  await click('#hlBtn');await click('.sent',0);
  const focusLight=await evaluate(`(()=>{const a=document.querySelector('.sent.active'),cur=a.closest('.block'),dim=document.querySelector('.block.dimmed');return {activeBg:getComputedStyle(a).backgroundColor,currentBg:getComputedStyle(cur).backgroundColor,dimColor:getComputedStyle(dim).color,dimmed:document.querySelectorAll('.block.dimmed').length,cur:state.cur}})()`);
  test('点句聚焦且静态块填充让位',focusLight.activeBg==='rgb(255, 243, 205)'&&focusLight.currentBg==='rgba(0, 0, 0, 0)',focusLight);
  test('其他语义块明显减淡',focusLight.dimmed>0&&focusLight.dimColor==='rgb(95, 95, 95)',focusLight);
  test('浅色减淡对比度≥4.5:1',contrast(focusLight.dimColor,'rgb(255,255,255)')>=4.5,contrast(focusLight.dimColor,'rgb(255,255,255)'));
  await send('Input.dispatchMouseEvent',{type:'mousePressed',x:3,y:500,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:3,y:500,button:'left',clickCount:1});await sleep(60);
  test('点击空白不改变焦点',await evaluate('state.cur')===focusLight.cur);
  await click('.skip-fold summary');
  test('点击跳读预览只展开不进入聚焦',await evaluate('state.cur')===focusLight.cur&&await evaluate(`document.querySelector('.skip-fold').open`));
  await click('.skip-fold summary');
  await select('th','dark');
  const dark=await evaluate(`(()=>{const a=document.querySelector('.sent.active'),d=document.querySelector('.block.dimmed');return {bg:getComputedStyle(document.body).backgroundColor,fg:getComputedStyle(document.body).color,hl:getComputedStyle(a).backgroundColor,dim:getComputedStyle(d).color}})()`);
  test('深色高亮与页面背景有可测亮度差',dark.hl==='rgb(90, 71, 24)'&&Math.abs(lum(rgb(dark.hl))-lum(rgb(dark.bg)))>.01,dark);
  test('深色高亮文字对比度≥4.5:1',contrast(dark.fg,dark.hl)>=4.5,contrast(dark.fg,dark.hl));
  test('深色减淡文字对比度≥4.5:1',contrast(dark.dim,dark.bg)>=4.5,contrast(dark.dim,dark.bg));
  await screenshot('02-dark-focus.png');
  await click('#hlBtn');
  test('关闭高亮恢复填充并清除减淡',await evaluate(`document.querySelectorAll('.sent.active,.block.dimmed').length===0&&getComputedStyle(document.querySelector('.block[data-pri="精读"]')).backgroundColor!=='rgba(0, 0, 0, 0)'`));

  // 关闭跳读后，从它之前的可见句用真实键盘向右导航。
  await click('#hlBtn');
  const beforeSkip=await evaluate(`(()=>{const i=sents.findIndex((x,i)=>visible(x.el)&&sents.slice(i+1).some(y=>!visible(y.el)));return i})()`);
  if(beforeSkip>=0){await evaluate(`sents[${beforeSkip}].el.scrollIntoView({block:'center'})`);await click('.sent',beforeSkip);await key('ArrowRight','ArrowRight',39);test('键盘导航不进入折叠内容',await evaluate(`state.cur<0||visible(sents[state.cur].el)`))}else test('键盘导航不进入折叠内容',false,'未找到折叠前句子');
  const readingBeforeOriginal=await evaluate('capturePosition()');
  await click('#origAll');
  test('切换原文定位当前阅读块而非页首',await evaluate('capturePosition().id')===readingBeforeOriginal.id,readingBeforeOriginal);
  const original=await evaluate(`(()=>{const o=document.getElementById('original-full'),all=[o,...o.querySelectorAll('*')];return {same:o.textContent===DATA.original_text,strong:o.querySelectorAll('strong').length,folds:document.querySelectorAll('.skip-fold').length,assisted:document.querySelectorAll('.block,.region').length,buttons:[...document.querySelectorAll('button')].filter(x=>x.textContent==='查看原文').length,noResidue:all.every(e=>{const s=getComputedStyle(e);return s.backgroundColor==='rgba(0, 0, 0, 0)'&&s.borderLeftWidth==='0px'&&s.boxShadow==='none'&&s.fontWeight==='400'})}})()`);
  test('全局原文与输入逐字一致且包含折叠内容',original.same,original);
  test('原文模式无任何辅助标记或视觉残留',original.strong===0&&original.folds===0&&original.assisted===0&&original.noResidue,original);
  await click('#origAll');
  test('返回辅助版无重复渲染',await evaluate(`document.querySelectorAll('#original-full').length===0&&document.querySelectorAll('.skip-fold').length===1`));
  await click('#hlBtn');

  // 模式：快速浏览速览仍清晰；完整阅读所有跳读直接可见。
  const readingBeforeMode=await evaluate('capturePosition()');
  await click('#modeBtn');
  test('模式切换保留当前阅读位置',await evaluate('capturePosition().id')===readingBeforeMode.id,readingBeforeMode);
  test('快速浏览速览不默认减淡',await evaluate(`state.mode==='快速浏览'&&document.querySelectorAll('.block[data-pri="速览"].dimmed').length===0`));
  await click('#modeBtn');
  test('完整阅读一次展示全部原文',await evaluate(`state.mode==='完整阅读'&&document.querySelectorAll('.skip-fold').length===0&&document.querySelectorAll('.block[data-pri="跳读"]').length===2`));
  await click('#modeBtn');
  test('返回聚焦阅读跳读恢复可逆折叠',await evaluate(`state.mode==='聚焦阅读'&&document.querySelectorAll('.skip-fold').length===1`));

  // 长区域 fixture：统一填充、起点间隙、结构边界与边框不重复。
  const fixture={title:'连续区域测试',mode:'聚焦阅读',segments:[],original_text:'',conservative:false};
  let n=0;const add=(priority,count,role='论证')=>{for(let i=0;i<count;i++){const text=`${priority}区域第${++n}句，用于验证连续呈现。`;fixture.segments.push({seg_no:n,original:text,sentences:[text],blocks:[{text,role,priority,sentences:[text],preview:priority==='跳读'?'补充例证预览':null}]});fixture.original_text+=(fixture.original_text?'\n\n':'')+text}};
  add('精读',5);add('精读',1,'列表');add('速览',3);add('跳读',2,'引文');add('跳读',1,'背景');
  const fixtureFile=path.join(OUT,'region_fixture.html');fs.writeFileSync(fixtureFile,fs.readFileSync(path.join(ROOT,'assets','reader_template.html'),'utf8').replace('__READER_DATA__',JSON.stringify(fixture)));
  await navigate(fixtureFile);await select('th','light');
  const regions=await evaluate(`(()=>{const blocks=[...document.querySelectorAll('.region[data-pri="精读"] .block')];return {bg:blocks.map(x=>getComputedStyle(x).backgroundColor),borders:blocks.map(x=>getComputedStyle(x).borderLeftWidth),regionBorders:blocks.map(x=>getComputedStyle(x.closest('.region')).borderLeftWidth),focusRegions:document.querySelectorAll('.region[data-pri="精读"]').length,folds:document.querySelectorAll('.skip-fold').length}})()`);
  test('长精读区域背景统一且不衰减',new Set(regions.bg).size===1&&regions.bg[0]==='rgb(255, 242, 233)',{bg:regions.bg});
  test('列表结构边界强制断区',regions.focusRegions===2,{focusRegions:regions.focusRegions});
  test('连续块无重复边框且区域边框始终保留',regions.borders.every(x=>x==='0px')&&regions.regionBorders.every(x=>x==='3px'),regions);
  test('同主题跳读合并、跨主题不合并',regions.folds===2,{folds:regions.folds});

  await navigate(demo);
  const themeFills={};
  for(const theme of ['light','dark','sepia']){await select('th',theme);themeFills[theme]=await evaluate(`(()=>{const f=document.querySelector('.block[data-pri="精读"]');return {fill:getComputedStyle(f).backgroundColor,page:getComputedStyle(document.body).backgroundColor,border:getComputedStyle(f.closest('.region')).borderLeftWidth}})()`)}
  test('三主题精读均有可辨填充而非只剩边框',Object.values(themeFills).every(x=>x.fill!=='rgba(0, 0, 0, 0)'&&x.fill!==x.page&&contrast(x.fill,x.page)>1.03&&x.border==='3px'),themeFills);
  await select('fs','20');await select('th','sepia');
  const sepia=await evaluate(`(()=>{const b=document.querySelector('.block[data-pri="速览"]');return {size:getComputedStyle(b).fontSize,fg:getComputedStyle(b).color,bg:getComputedStyle(document.body).backgroundColor}})()`);
  test('护眼主题字号统一且对比度≥4.5:1',sepia.size==='20px'&&contrast(sepia.fg,sepia.bg)>=4.5,{...sepia,contrast:contrast(sepia.fg,sepia.bg)});
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await sleep(100);
  const mobile=await evaluate(`({overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,minButton:Math.min(...[...document.querySelectorAll('.tbtn')].map(x=>x.getBoundingClientRect().height)),width:document.documentElement.clientWidth})`);
  test('移动端无横向溢出且触摸目标≥44px',!mobile.overflow&&mobile.minButton>=44,mobile);
  await screenshot('03-mobile-sepia.png');
  test('全程无浏览器脚本异常',errors.length===0,errors);
}catch(e){test('浏览器测试执行',false,{message:e.message,stack:e.stack});process.exitCode=1}
finally{
  const report={browser:'Chrome headless (CDP)',timestamp:new Date().toISOString(),passed:results.filter(x=>x.status==='通过').length,failed:results.filter(x=>x.status==='失败').length,results};
  fs.writeFileSync(path.join(OUT,'browser_results.json'),JSON.stringify(report,null,2));
  console.log(`真实浏览器测试：通过 ${report.passed} / 失败 ${report.failed} / 共 ${results.length}`);
  try{await send('Browser.close')}catch{}try{ws?.close()}catch{}proc.kill();await sleep(250);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}
  if(report.failed)process.exitCode=1;
}
