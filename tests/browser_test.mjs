#!/usr/bin/env node
/* V3.2.4 真实浏览器验收：Node 内置 WebSocket + Chrome DevTools Protocol，零第三方依赖。 */
import {spawn} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath, pathToFileURL} from 'node:url';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const ROOT=path.resolve(HERE,'..');
// 测试数据仅在执行时生成到系统临时目录；不写入 Git 仓库。
const OUT=fs.mkdtempSync(path.join(os.tmpdir(),'reader-browser-test-'));
const template=fs.readFileSync(path.join(ROOT,'assets','reader_template.html'),'utf8');
function makeFixture(file,data){const p=path.join(OUT,file);fs.writeFileSync(p,template.replace('__READER_DATA__',JSON.stringify(data)));return p}
const demoData={"title":"阅读辅助","mode":"聚焦阅读","high_risk":false,"modules":[{"title":"理论定义","content":"根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。从理论上讲，语义翻译倾向于保留原文文化的表达，…"},{"title":"方法论","content":"基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法…"},{"title":"概念定义","content":"借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。"},{"title":"例证","content":"例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"："},{"title":"引文","content":"他何尝是真要银子呢，也只当化个善缘就是了。（第117回）"},{"title":"局限","content":"这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。"}],"segments":[{"seg_no":1,"priority":"精读","role":"理论定义","reason":null,"preview":null,"original":"根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。","sentences":["根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。","从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。","而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。"],"blocks":[{"text":"根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。","role":"理论定义","structure":null,"heading_level":null,"priority":"精读","sentences":["根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。","从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。","而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。"],"preview":null,"emphasis":[{"start":21,"end":30,"text":"语义翻译和交际翻译","score":0.98},{"start":98,"end":108,"text":"尽可能将二者结合起来","score":0.92}]}],"foldable":false},{"seg_no":2,"priority":"精读","role":"方法论","reason":null,"preview":null,"original":"基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。","sentences":["基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。"],"blocks":[{"text":"基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。","role":"方法论","structure":null,"heading_level":null,"priority":"精读","sentences":["基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。"],"preview":null,"emphasis":[]}],"foldable":false},{"seg_no":3,"priority":"精读","role":"概念定义","reason":null,"preview":null,"original":"借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"：","sentences":["借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。","例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"："],"blocks":[{"text":"借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。","role":"概念定义","structure":null,"heading_level":null,"priority":"精读","sentences":["借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。"],"preview":null,"emphasis":[]},{"text":"例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"：","role":"例证","structure":null,"heading_level":null,"priority":"速览","sentences":["例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"："],"preview":null,"emphasis":[]}],"foldable":false},{"seg_no":4,"priority":"跳读","role":"引文","reason":null,"preview":"《红楼梦》第117回原文引文","original":"他何尝是真要银子呢，也只当化个善缘就是了。（第117回）","sentences":["他何尝是真要银子呢，也只当化个善缘就是了。","（第117回）"],"blocks":[{"text":"他何尝是真要银子呢，也只当化个善缘就是了。（第117回）","role":"引文","structure":null,"heading_level":null,"priority":"跳读","sentences":["他何尝是真要银子呢，也只当化个善缘就是了。","（第117回）"],"preview":"《红楼梦》第117回原文引文","emphasis":[]}],"foldable":true},{"seg_no":5,"priority":"跳读","role":"引文","reason":null,"preview":"霍克思英译原文","original":"霍译：At the most he was hoping for a friendly contribution, which would create good karma．","sentences":["霍译：At the most he was hoping for a friendly contribution, which would create good karma．"],"blocks":[{"text":"霍译：At the most he was hoping for a friendly contribution, which would create good karma．","role":"引文","structure":null,"heading_level":null,"priority":"跳读","sentences":["霍译：At the most he was hoping for a friendly contribution, which would create good karma．"],"preview":"霍克思英译原文","emphasis":[]}],"foldable":true},{"seg_no":6,"priority":"精读","role":"局限","reason":null,"preview":null,"original":"这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。","sentences":["这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。"],"blocks":[{"text":"这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。","role":"局限","structure":null,"heading_level":null,"priority":"精读","sentences":["这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。"],"preview":null,"emphasis":[]}],"foldable":false}],"original_text":"根据纽马克的翻译理论，英汉翻译主要可以采取语义翻译和交际翻译两种侧重形式。从理论上讲，语义翻译倾向于保留原文文化的表达，而交际翻译更关注将含有文化色彩的概念转化为本民族的表达方式。而好的翻译，则应尽可能将二者结合起来，以平衡本民族与其他民族的文化差异。\n\n基于这种翻译理论，针对\"缘分\"为代表的文化负载词在英语中的词义空缺现象，译者可以采取借词、替代和释义这三种相对适用的方法来进行填补。\n\n借词是通过引用其他语言中的单词从而创造出本语言中新词的方法。例如，在《红楼梦》英译本中，\"缘分\"的英译借用了早期的佛经语言\"karma\"：\n\n他何尝是真要银子呢，也只当化个善缘就是了。（第117回）\n\n霍译：At the most he was hoping for a friendly contribution, which would create good karma．\n\n这种翻译方法虽解决了英语中的词义空缺，但其弊端也比较明显：读者必须理解源于第三者文化中的新词，这仍然需要花费相当的精力。","conservative":false,"requires_review":false,"output_status":"ready"};
const colorData={"title":"阅读辅助","mode":"聚焦阅读","high_risk":false,"modules":[{"title":"核心论点","content":"为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。意识总是关于某物的意识，这一命题构成现象学分析的起点。"},{"title":"论证","content":"对象在侧显中被给予，而侧显总是从某个视角出发。视角的更换并不取消对象，而是丰富对象的规定性。"},{"title":"限定","content":"胡塞尔的分析并没有彻底解决这些问题。后来者对意向性结构的修正，构成了后续讨论的出发点。"}],"segments":[{"seg_no":1,"priority":null,"role":"标题","reason":null,"preview":null,"original":"第一部分　意向性与表述","sentences":["第一部分　意向性与表述"],"blocks":[{"text":"第一部分　意向性与表述","role":"标题","structure":null,"heading_level":1,"priority":null,"sentences":["第一部分　意向性与表述"],"preview":null,"emphasis":[]}],"foldable":false},{"seg_no":2,"priority":"精读","role":"核心论点","reason":null,"preview":null,"original":"为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。意识总是关于某物的意识，这一命题构成现象学分析的起点。","sentences":["为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。","意识总是关于某物的意识，这一命题构成现象学分析的起点。"],"blocks":[{"text":"为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。意识总是关于某物的意识，这一命题构成现象学分析的起点。","role":"核心论点","structure":null,"heading_level":null,"priority":"精读","sentences":["为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。","意识总是关于某物的意识，这一命题构成现象学分析的起点。"],"preview":null,"emphasis":[]}],"foldable":false},{"seg_no":3,"priority":"精读","role":"论证","reason":null,"preview":null,"original":"对象在侧显中被给予，而侧显总是从某个视角出发。视角的更换并不取消对象，而是丰富对象的规定性。","sentences":["对象在侧显中被给予，而侧显总是从某个视角出发。","视角的更换并不取消对象，而是丰富对象的规定性。"],"blocks":[{"text":"对象在侧显中被给予，而侧显总是从某个视角出发。视角的更换并不取消对象，而是丰富对象的规定性。","role":"论证","structure":null,"heading_level":null,"priority":"精读","sentences":["对象在侧显中被给予，而侧显总是从某个视角出发。","视角的更换并不取消对象，而是丰富对象的规定性。"],"preview":null,"emphasis":[]}],"foldable":false},{"seg_no":4,"priority":"精读","role":"限定","reason":null,"preview":null,"original":"胡塞尔的分析并没有彻底解决这些问题。后来者对意向性结构的修正，构成了后续讨论的出发点。","sentences":["胡塞尔的分析并没有彻底解决这些问题。","后来者对意向性结构的修正，构成了后续讨论的出发点。"],"blocks":[{"text":"胡塞尔的分析并没有彻底解决这些问题。后来者对意向性结构的修正，构成了后续讨论的出发点。","role":"限定","structure":null,"heading_level":null,"priority":"精读","sentences":["胡塞尔的分析并没有彻底解决这些问题。","后来者对意向性结构的修正，构成了后续讨论的出发点。"],"preview":null,"emphasis":[]}],"foldable":false}],"original_text":"第一部分　意向性与表述\n\n为了说明表述能够指向对象，胡塞尔将意向性引入意识结构分析。意识总是关于某物的意识，这一命题构成现象学分析的起点。\n\n对象在侧显中被给予，而侧显总是从某个视角出发。视角的更换并不取消对象，而是丰富对象的规定性。\n\n胡塞尔的分析并没有彻底解决这些问题。后来者对意向性结构的修正，构成了后续讨论的出发点。","conservative":false,"requires_review":true,"output_status":"blocked_pending_agent_review"};
const demo=makeFixture('demo.html',demoData);
const colorFile=makeFixture('color_case.html',colorData);
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
async function clickAt(x,y){await send('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',clickCount:1});await sleep(280)}
async function touchAt(x,y){await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await sleep(280)}
async function key(key,code=key,virtualKey=0){await send('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode:virtualKey});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode:virtualKey});await sleep(100)}
async function select(id,value){await evaluate(`(()=>{const e=document.getElementById(${JSON.stringify(id)});e.value=${JSON.stringify(value)};e.dispatchEvent(new Event('change',{bubbles:true}))})()`);await sleep(280)}
async function screenshot(name){const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(OUT,name),Buffer.from(r.data,'base64'))}
async function screenshotClip(name,selectors){
  await evaluate(`document.querySelector(${JSON.stringify(selectors[0])}).scrollIntoView({block:'start'})`);await sleep(100);
  const clip=await evaluate(`(()=>{const rs=${JSON.stringify(selectors)}.map(s=>document.querySelector(s)?.getBoundingClientRect()).filter(Boolean);if(!rs.length)return null;const x=Math.min(...rs.map(r=>r.left))-8,y=Math.min(...rs.map(r=>r.top))-8,width=Math.max(...rs.map(r=>r.right))+8-x,height=Math.max(...rs.map(r=>r.bottom))+8-y;return {x:Math.max(0,x),y:Math.max(0,y),width:Math.max(80,width),height:Math.max(80,height),scale:1}})()`);
  if(!clip)throw new Error('截图区域不存在');
  const r=await send('Page.captureScreenshot',{format:'png',clip,captureBeyondViewport:false});
  fs.writeFileSync(path.join(OUT,name),Buffer.from(r.data,'base64'));return clip;
}
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
  test('V4.0无footer及上下句遗留控件',await evaluate(`!document.querySelector('footer,#readerFooter,#prev,#next,#pos')&&getComputedStyle(document.querySelector('main')).paddingBottom==='32px'`));
  const initial=await evaluate(`(()=>{const f=document.querySelector('.block[data-pri="精读"]'),s=document.querySelector('.block[data-pri="速览"]'),r=f.closest('.region'),d=document.querySelector('.skip-fold');return {focusBg:getComputedStyle(f).backgroundColor,focusBorder:getComputedStyle(r).borderLeftWidth,focusColor:getComputedStyle(f).color,strong:[...f.querySelectorAll('strong')].map(x=>({weight:getComputedStyle(x).fontWeight,color:getComputedStyle(x).color,text:x.textContent})),skimColor:getComputedStyle(s).color,skimWeight:getComputedStyle(s).fontWeight,skimBg:getComputedStyle(s).backgroundColor,skimText:s.textContent,skimExpected:DATA.segments.flatMap(x=>x.blocks).find(x=>x.priority==='速览').text,bodyColor:getComputedStyle(document.body).color,folds:document.querySelectorAll('.skip-fold').length,skipOpen:d.open,skipBg:getComputedStyle(d).backgroundColor,skipBorder:getComputedStyle(d).borderLeftStyle,skipBorderWidth:getComputedStyle(d).borderLeftWidth,previewColor:getComputedStyle(d.querySelector('.skip-preview')).color,preview:d.querySelector('.skip-preview').textContent,previewVisible:d.querySelector('.skip-preview').getClientRects().length>0,regions:document.querySelectorAll('.region').length,blocks:document.querySelectorAll('.block').length,perSegmentButtons:document.querySelectorAll('.segfoot').length,originalButtons:document.querySelectorAll('#origAll').length}})()`);
  test('精读暖底/3-4px边框计算样式生效',initial.focusBg==='rgb(255, 242, 233)'&&initial.focusBorder==='3px',initial);
  test('跳读无填充且弱于速览',initial.skipBg==='rgba(0, 0, 0, 0)'&&initial.skipBorder==='dashed'&&initial.skipBorderWidth==='2px'&&contrast(initial.previewColor,'rgb(255,255,255)')>=4.5,initial);
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

  await click('#hlBtn');
  const sentPoint=await evaluate(`(()=>{const idx=sents.findIndex(x=>{const r=x.el.getBoundingClientRect();return visible(x.el)&&r.top>headerEl.getBoundingClientRect().bottom+4&&r.bottom<window.innerHeight-4});if(idx<0)return null;const r=sents[idx].el.getBoundingClientRect();return {idx,x:r.left+r.width/2,y:r.top+r.height/2}})()`);
  if(!sentPoint)throw new Error('未找到安全视口内句子');
  await clickAt(sentPoint.x,sentPoint.y);
  const focusLight=await evaluate(`(()=>{const a=document.querySelector('.sent.active'),cur=a.closest('.block'),dim=document.querySelector('.block.dimmed');return {activeBg:getComputedStyle(a).backgroundColor,currentBg:getComputedStyle(cur).backgroundColor,dimColor:getComputedStyle(dim).color,dimmed:document.querySelectorAll('.block.dimmed').length,cur:state.cur}})()`);
  test('点句聚焦且静态块填充让位',focusLight.activeBg==='rgb(255, 243, 205)'&&focusLight.currentBg==='rgba(0, 0, 0, 0)',focusLight);
  test('其他语义块明显减淡',focusLight.dimmed>0&&focusLight.dimColor==='rgb(95, 95, 95)',focusLight);
  test('浅色减淡对比度≥4.5:1',contrast(focusLight.dimColor,'rgb(255,255,255)')>=4.5,contrast(focusLight.dimColor,'rgb(255,255,255)'));
  await click('.skip-fold summary');
  test('点击跳读预览只展开不进入聚焦',await evaluate('state.cur')===focusLight.cur&&await evaluate(`document.querySelector('.skip-fold').open`));
  await click('.skip-fold summary');
  const rootRect=await evaluate(`(()=>{const r=root.getBoundingClientRect();return {x:r.right-7,y:Math.min(r.bottom-20,window.innerHeight-120),target:null}})()`);
  await clickAt(rootRect.x,rootRect.y);
  test('真实空白点击清除聚焦但保留高亮功能',await evaluate('({cur:state.cur,hl:state.hl,focusActive:document.body.classList.contains("focus-active"),active:document.querySelectorAll(".sent.active,.block.dimmed").length})').then(x=>x.cur===-1&&x.hl===true&&x.focusActive===false&&x.active===0));
  await click('.sent',sentPoint.idx);
  test('空白取消后可立即重新聚焦',await evaluate('state.cur')===focusLight.cur);
  const settingsBefore=await evaluate('({fs:state.fs,th:state.th,mode:state.mode})');
  await key('Escape','Escape',27);
  const escState=await evaluate('({cur:state.cur,fs:state.fs,th:state.th,mode:state.mode})');
  test('Esc清除聚焦且不修改设置',escState.cur===-1&&escState.fs===settingsBefore.fs&&escState.th===settingsBefore.th&&escState.mode===settingsBefore.mode,escState);
  await click('.sent',sentPoint.idx);
  await select('th','dark');
  const dark=await evaluate(`(()=>{const a=document.querySelector('.sent.active'),d=document.querySelector('.block.dimmed');return {bg:getComputedStyle(document.body).backgroundColor,fg:getComputedStyle(document.body).color,hl:getComputedStyle(a).backgroundColor,dim:getComputedStyle(d).color}})()`);
  test('深色高亮与页面背景有可测亮度差',dark.hl==='rgb(90, 71, 24)'&&Math.abs(lum(rgb(dark.hl))-lum(rgb(dark.bg)))>.01,dark);
  test('深色高亮文字对比度≥4.5:1',contrast(dark.fg,dark.hl)>=4.5,contrast(dark.fg,dark.hl));
  test('深色减淡文字对比度≥4.5:1',contrast(dark.dim,dark.bg)>=4.5,contrast(dark.dim,dark.bg));
  await screenshot('02-dark-focus.png');
  await click('#hlBtn');
  test('关闭高亮恢复填充并清除减淡',await evaluate(`document.querySelectorAll('.sent.active,.block.dimmed').length===0&&getComputedStyle(document.querySelector('.block[data-pri="精读"]')).backgroundColor!=='rgba(0, 0, 0, 0)'`));
  await select('th','light');

  // 关闭跳读后，从它之前的可见句用真实键盘向右导航。
  await click('#hlBtn');
  const beforeSkip=await evaluate(`(()=>{const i=sents.findIndex((x,i)=>visible(x.el)&&sents.slice(i+1).some(y=>!visible(y.el)));return i})()`);
  if(beforeSkip>=0){await evaluate(`sents[${beforeSkip}].el.scrollIntoView({block:'center'})`);await click('.sent',beforeSkip);await key('ArrowRight','ArrowRight',39);test('键盘导航不进入折叠内容',await evaluate(`state.cur<0||visible(sents[state.cur].el)`))}else test('键盘导航不进入折叠内容',false,'未找到折叠前句子');
  const readingBeforeOriginal=await evaluate('capturePosition()');
  await click('#hlBtn');
  await click('#origAll');
  test('切换原文定位当前阅读块而非页首',await evaluate('capturePosition().id')===readingBeforeOriginal.id,readingBeforeOriginal);
  const original=await evaluate(`(()=>{const o=document.getElementById('original-full'),all=[o,...o.querySelectorAll('*')];return {same:o.textContent===DATA.original_text,strong:o.querySelectorAll('strong').length,folds:document.querySelectorAll('.skip-fold').length,assisted:document.querySelectorAll('.block,.region').length,buttons:[...document.querySelectorAll('button')].filter(x=>x.textContent==='查看原文').length,noResidue:all.every(e=>{const s=getComputedStyle(e);return s.backgroundColor==='rgba(0, 0, 0, 0)'&&s.borderLeftWidth==='0px'&&s.boxShadow==='none'&&s.fontWeight==='400'})}})()`);
  test('全局原文与输入逐字一致且包含折叠内容',original.same,original);
  test('原文模式无任何辅助标记或视觉残留',original.strong===0&&original.folds===0&&original.assisted===0&&original.noResidue,original);
  await click('#origAll');
  test('返回辅助版无重复渲染',await evaluate(`document.querySelectorAll('#original-full').length===0&&document.querySelectorAll('.skip-fold').length===1`));
  await click('#hlBtn');
  await click('#origAll');
  await click('.original-block .sent',0);
  const originalFocus=await evaluate(`(()=>{const o=document.getElementById('original-full');const a=document.querySelector('.sent.active');return {cur:state.cur,active:!!a,same:o.textContent===DATA.original_text,dimColor:getComputedStyle(o).color,activeColor:a?getComputedStyle(a).color:null,dimmed:document.querySelectorAll('.original-block.dimmed').length}})()`);
  test('原文模式可视觉层聚焦且文本不变',originalFocus.cur>=0&&originalFocus.active&&originalFocus.same,originalFocus);
  test('原文模式其他文字实际减淡且当前句正常',originalFocus.dimColor==='rgb(95, 95, 95)'&&originalFocus.activeColor==='rgb(26, 26, 26)'&&originalFocus.dimmed>0,originalFocus);
  await key('Escape','Escape',27);
  test('原文模式Esc清除聚焦',await evaluate('state.cur')===-1&&await evaluate('document.querySelectorAll(".sent.active,.original-block.dimmed").length')===0);
  await click('#origAll');

  // 统一辅助视图：不再有三模式按钮；辅助/原文、高亮、折叠可独立组合。
  const beforeUnified=await evaluate('({view:state.view,hl:state.hl,allExpanded:state.allExpanded})');
  test('统一视图无模式按钮',await evaluate(`!document.getElementById('modeBtn')&&typeof state.mode==='undefined'&&document.querySelectorAll('.skip-fold').length===1`),beforeUnified);
  test('统一视图默认折叠跳读且原文/高亮可用',await evaluate(`state.view==='assisted'&&document.getElementById('hlBtn')&&document.getElementById('expandAll')&&!document.getElementById('expandAll').disabled`),beforeUnified);

  // 标题层级 fixture：真实渲染语义化标题且无策略底色。
  const headingData={title:'标题层级测试',mode:'聚焦阅读',segments:[
    {seg_no:1,original:'文档主标题',sentences:['文档主标题'],blocks:[{text:'文档主标题',role:'标题',heading_level:0,priority:null,sentences:['文档主标题'],preview:null}]},
    {seg_no:2,original:'一级章节',sentences:['一级章节'],blocks:[{text:'一级章节',role:'标题',heading_level:1,priority:null,sentences:['一级章节'],preview:null}]},
    {seg_no:3,original:'二级章节',sentences:['二级章节'],blocks:[{text:'二级章节',role:'标题',heading_level:2,priority:null,sentences:['二级章节'],preview:null}]},
    {seg_no:4,original:'正文一句。',sentences:['正文一句。'],blocks:[{text:'正文一句。',role:'核心论点',priority:'精读',sentences:['正文一句。'],preview:null}]}
  ],original_text:'文档主标题\n\n一级章节\n\n二级章节\n\n正文一句。',conservative:false};
  const headingFile=path.join(OUT,'heading_fixture.html');fs.writeFileSync(headingFile,fs.readFileSync(path.join(ROOT,'assets','reader_template.html'),'utf8').replace('__READER_DATA__',JSON.stringify(headingData)));
  await navigate(headingFile);await select('th','light');
  const headings=await evaluate(`(()=>{const hs=['h1.heading','h2.heading','h3.heading'].map(s=>document.querySelector(s));return {tags:hs.map(x=>x?.tagName),texts:hs.map(x=>x?.textContent),inRegion:hs.map(x=>!!x?.closest('.region')),bg:hs.map(x=>getComputedStyle(x).backgroundColor),weight:hs.map(x=>getComputedStyle(x).fontWeight),sizes:hs.map(x=>getComputedStyle(x).fontSize),regions:document.querySelectorAll('.region').length}})()`);
  test('标题渲染h1/h2/h3且文字正确',JSON.stringify(headings.tags)===JSON.stringify(['H1','H2','H3'])&&JSON.stringify(headings.texts)===JSON.stringify(['文档主标题','一级章节','二级章节']),headings);
  test('标题无区域底色且可读层级',headings.inRegion.every(x=>!x)&&headings.bg.every(x=>x==='rgba(0, 0, 0, 0)')&&headings.weight.every(x=>x==='700')&&parseFloat(headings.sizes[0])>parseFloat(headings.sizes[1])&&parseFloat(headings.sizes[1])>parseFloat(headings.sizes[2]),headings);

  // 用户报告区间的受控色差用例：两个连续精读块必须同区同背景。
  await navigate(colorFile);await select('th','light');
  const anchorIds=await evaluate(`(()=>{const a1=entries.find(e=>e.block.text.includes('为了说明表述能够指向对象'));const a2=entries.find(e=>e.block.text.includes('胡塞尔的分析并没有彻底解决这些问题'));return [a1?.id,a2?.id]})()`);
  test('色差用例两端锚点定位成功',anchorIds.every(Boolean),anchorIds);
  const colorSelectors=anchorIds.map(id=>`[data-block-id="${id}"]`);
  const colorStyles={themes:{},states:{}};
  for(const theme of ['light','dark','sepia']){
    await select('th',theme);
    colorStyles.themes[theme]=await evaluate(`(()=>{const els=${JSON.stringify(anchorIds)}.map(id=>document.querySelector('[data-block-id="'+id+'"]'));const rs=els.map(x=>x.closest('.region'));return els.map((x,i)=>({bg:getComputedStyle(x).backgroundColor,color:getComputedStyle(x).color,borderLeftColor:getComputedStyle(rs[i]).borderLeftColor,opacity:getComputedStyle(x).opacity,focusFill:getComputedStyle(x).getPropertyValue('--focus-fill').trim(),regionPri:rs[i].dataset.pri,sameRegion:rs[0]===rs[1]}))})()`);
    const pair=colorStyles.themes[theme];
    test(`${theme}主题连续精读背景一致`,pair.length===2&&pair[0].bg===pair[1].bg&&pair[0].sameRegion&&pair[0].regionPri==='精读'&&pair[0].opacity==='1',{theme,pair});
  }
  await select('th','light');
  colorStyles.states.unfocused=await evaluate(`document.querySelectorAll('.sent.active,.block.dimmed').length===0&&document.body.classList.contains('focus-active')===false`);
  if(!await evaluate('state.hl'))await click('#hlBtn');
  colorStyles.states.highlightNoSelection=await evaluate(`state.hl===true&&state.cur===-1&&document.body.classList.contains('focus-active')===false`);
  await click(colorSelectors[0]+' .sent');
  colorStyles.states.highlightSelected=await evaluate(`(()=>{const els=${JSON.stringify(anchorIds)}.map(id=>document.querySelector('[data-block-id="'+id+'"]'));return {active:document.querySelectorAll('.sent.active').length,focusActive:document.body.classList.contains('focus-active'),bgs:els.map(x=>getComputedStyle(x).backgroundColor)}})()`);
  test('聚焦状态下同区两块填充同步让位',colorStyles.states.highlightSelected.active===1&&colorStyles.states.highlightSelected.focusActive&&new Set(colorStyles.states.highlightSelected.bgs).size===1&&colorStyles.states.highlightSelected.bgs[0]==='rgba(0, 0, 0, 0)',colorStyles.states.highlightSelected);
  await click('#hlBtn');
  colorStyles.states.afterRestore=await evaluate(`document.querySelectorAll('.sent.active,.block.dimmed').length===0&&getComputedStyle(document.querySelector('[data-block-id="${anchorIds[0]}"]')).backgroundColor===getComputedStyle(document.querySelector('[data-block-id="${anchorIds[1]}"]')).backgroundColor`);
  test('取消聚焦后色差区间背景一致恢复',colorStyles.states.afterRestore,colorStyles.states);
  const beforeModeBg=await evaluate(`getComputedStyle(document.querySelector('[data-block-id="${anchorIds[0]}"]')).backgroundColor`);
  colorStyles.states.afterModes=await evaluate(`getComputedStyle(document.querySelector('[data-block-id="${anchorIds[0]}"]')).backgroundColor`);
  test('未聚焦同区背景稳定',colorStyles.states.afterModes===beforeModeBg,{beforeModeBg,afterModes:colorStyles.states.afterModes});
  fs.writeFileSync(path.join(OUT,'color_case_styles.json'),JSON.stringify({note:'受控fixture，非原始哲学论文报告数据',anchors:anchorIds,styles:colorStyles},null,2));
  await screenshotClip('04-color-case-light.png',colorSelectors);await select('th','dark');await screenshotClip('05-color-case-dark.png',colorSelectors);await select('th','sepia');await screenshotClip('06-color-case-sepia.png',colorSelectors);

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
  await click('.skip-fold summary');
  const skipOpenBg=await evaluate(`[...document.querySelectorAll('.skip-fold .block')].map(x=>getComputedStyle(x).backgroundColor)`);
  test('跳读展开后正文仍无填充',skipOpenBg.every(x=>x==='rgba(0, 0, 0, 0)'),skipOpenBg);
  const alignment=await evaluate(`(()=>{const kinds=['精读','速览','跳读'];return kinds.map(k=>{const sel=k==='跳读'?'.skip-fold .block .sent':'.region[data-pri="'+k+'"] .block .sent';const el=document.querySelector(sel);return el?{k,left:Math.round(el.getBoundingClientRect().left),textLeft:Math.round((el.getClientRects()[0]||el.getBoundingClientRect()).left),maxWidth:getComputedStyle(el.closest('.block')).maxWidth}:null})})()`);
  test('普通正文统一列宽且左边缘对齐',alignment.every(Boolean)&&new Set(alignment.map(x=>x.left)).size===1&&new Set(alignment.map(x=>x.maxWidth)).size===1,{alignment});
  await click('.skip-fold summary');

  await navigate(demo);
  const themeFills={};
  for(const theme of ['light','dark','sepia']){await select('th',theme);themeFills[theme]=await evaluate(`(()=>{const f=document.querySelector('.block[data-pri="精读"]'),d=document.querySelector('.skip-fold');return {fill:getComputedStyle(f).backgroundColor,page:getComputedStyle(document.body).backgroundColor,border:getComputedStyle(f.closest('.region')).borderLeftWidth,skipBg:getComputedStyle(d).backgroundColor,skipPreview:getComputedStyle(d.querySelector('.skip-preview')).color}})()`);
    const s=themeFills[theme];test(`${theme}主题跳读仍无填充且预览可读`,s.skipBg==='rgba(0, 0, 0, 0)'&&contrast(s.skipPreview,s.page)>=4.5,s)}
  test('三主题精读均有可辨填充而非只剩边框',Object.values(themeFills).every(x=>x.fill!=='rgba(0, 0, 0, 0)'&&x.fill!==x.page&&contrast(x.fill,x.page)>1.03&&x.border==='3px'),themeFills);
  await select('fs','20');await select('th','sepia');
  const sepia=await evaluate(`(()=>{const b=document.querySelector('.block[data-pri="速览"]');return {size:getComputedStyle(b).fontSize,fg:getComputedStyle(b).color,bg:getComputedStyle(document.body).backgroundColor}})()`);
  test('护眼主题字号统一且对比度≥4.5:1',sepia.size==='20px'&&contrast(sepia.fg,sepia.bg)>=4.5,{...sepia,contrast:contrast(sepia.fg,sepia.bg)});

  // V4.0 滚动验收：无底部导航，正常留白，最后一句在真实视口内完整可见。
  const scrollFixture={title:'V4.0 滚动验收',segments:[],original_text:'',conservative:false};
  for(let i=1;i<=48;i++){
    const text=`滚动验收第${i}句：这一句用于确认正常底部留白、顶部工具栏、动态视口和长文末行都能稳定适配，不依赖固定导航栏。`;
    scrollFixture.segments.push({seg_no:i,original:text,sentences:[text],blocks:[{text,role:'核心论点',priority:i%3===0?'速览':'精读',sentences:[text],preview:null}]});
    scrollFixture.original_text+=(scrollFixture.original_text?'\n\n':'')+text;
  }
  const scrollFile=path.join(OUT,'scroll_fixture_v400.html');fs.writeFileSync(scrollFile,fs.readFileSync(path.join(ROOT,'assets','reader_template.html'),'utf8').replace('__READER_DATA__',JSON.stringify(scrollFixture)));
  await navigate(scrollFile);await select('fs','24');await select('lh','2.0');await select('th','light');
  const scrollCheck=async()=>{
    await evaluate('window.scrollTo(0,document.documentElement.scrollHeight)');await sleep(120);
    return evaluate(`(()=>{const h=document.querySelector('header'),last=[...document.querySelectorAll('.sent')].at(-1),main=document.querySelector('main');const hr=h.getBoundingClientRect(),lr=last.getBoundingClientRect();return {gap:getComputedStyle(document.documentElement).getPropertyValue('--bottom-gap').trim(),mainPadding:getComputedStyle(main).paddingBottom,inViewport:lr.bottom<=window.innerHeight+1,belowHeader:lr.top>=hr.bottom-1,right:lr.right<=document.documentElement.clientWidth+1,viewport:window.innerHeight,lastBottom:lr.bottom,text:last.textContent.slice(-6)}})()`);
  };
  const desktopScroll=await scrollCheck();
  test('桌面长文最后一个字完整可见且留白适度',desktopScroll.inViewport&&desktopScroll.belowHeader&&desktopScroll.right&&desktopScroll.mainPadding==='32px',{desktopScroll});
  await evaluate('if(!state.hl)state.hl=true;applySettings();render()');await sleep(80);
  await evaluate('focusAt(sents.length-1)');await sleep(280);
  const lastFocus=await evaluate(`(()=>{const h=document.querySelector('header'),last=[...document.querySelectorAll('.sent')].at(-1);const hr=h.getBoundingClientRect(),lr=last.getBoundingClientRect();return {cur:state.cur,total:sents.length,inViewport:lr.bottom<=window.innerHeight+1,belowHeader:lr.top>=hr.bottom-1}})()`);
  test('桌面最后一句聚焦后仍完整可见',lastFocus.cur===lastFocus.total-1&&lastFocus.inViewport&&lastFocus.belowHeader,lastFocus);
  await evaluate('focusAt(0)');await sleep(280);
  const firstFocus=await evaluate(`(()=>{const h=document.querySelector('header'),first=document.querySelector('.sent');const fr=h.getBoundingClientRect(),lr=first.getBoundingClientRect();return {cur:state.cur,visible:lr.top>=fr.bottom-1&&lr.bottom<=window.innerHeight}})()`);
  test('桌面第一句聚焦后不被工具栏遮挡',firstFocus.cur===0&&firstFocus.visible,firstFocus);
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await sleep(120);
  const mobileScroll=await scrollCheck();
  test('390px长文末行完整可见且无横向滚动',mobileScroll.inViewport&&mobileScroll.belowHeader&&mobileScroll.right&&!(await evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth')),mobileScroll);
  await evaluate('focusAt(sents.length-1)');await sleep(280);
  const mobileLastFocus=await evaluate(`(()=>{const h=document.querySelector('header'),last=[...document.querySelectorAll('.sent')].at(-1);const hr=h.getBoundingClientRect(),lr=last.getBoundingClientRect();return {cur:state.cur,total:sents.length,inViewport:lr.bottom<=window.innerHeight+1,belowHeader:lr.top>=hr.bottom-1}})()`);
  test('390px最后一句聚焦后仍完整可见',mobileLastFocus.cur===mobileLastFocus.total-1&&mobileLastFocus.inViewport&&mobileLastFocus.belowHeader,mobileLastFocus);
  await screenshot('07-v400-mobile-scroll.png');
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await send('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});await sleep(100);
  const mobile=await evaluate(`({overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,minButton:Math.min(...[...document.querySelectorAll('.tbtn')].map(x=>x.getBoundingClientRect().height)),width:document.documentElement.clientWidth})`);
  test('移动端无横向溢出且触摸目标≥44px',!mobile.overflow&&mobile.minButton>=44,mobile);
  if(!await evaluate('state.hl'))await click('#hlBtn');
  const mobileTouch=await evaluate(`(()=>{const sp=[...document.querySelectorAll('.sent')].find(visible);const r=sp.getBoundingClientRect();const rr=root.getBoundingClientRect();let blank=null;for(const y of [window.innerHeight-130,window.innerHeight-150,window.innerHeight-180,rr.top+8]){for(const x of [rr.right-3,rr.left+3,rr.right-5]){const el=document.elementFromPoint(x,y);if(el===root){blank={bx:x,by:y};break}}if(blank)break}return {sx:r.left+r.width/2,sy:r.top+r.height/2,...blank,target:document.elementFromPoint(r.left+r.width/2,r.top+r.height/2)?.className}})()`);
  if(!mobileTouch.bx)throw new Error('移动端未找到root空白点');
  await touchAt(mobileTouch.sx,mobileTouch.sy);
  const mobileFocused=await evaluate('state.cur>=0&&document.body.classList.contains("focus-active")');
  await touchAt(mobileTouch.bx,mobileTouch.by);
  const mobileCleared=await evaluate('state.cur===-1&&state.hl===true&&!document.body.classList.contains("focus-active")');
  test('移动端触摸聚焦后可点空白取消',mobileFocused&&mobileCleared,{mobileFocused,mobileCleared});
  await screenshot('03-mobile-sepia.png');

  // V4.0 同源 iframe 宿主近似验收（不冒充 Work 专用宿主）。
  const hostFile=path.join(OUT,'iframe_host_v400.html');
  const embeddedHtml=fs.readFileSync(scrollFile,'utf8').replace(/&/g,'&amp;').replace(/"/g,'&quot;');
  fs.writeFileSync(hostFile,`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{margin:0;height:100%;overflow:hidden}iframe{display:block;border:0;width:100%;height:100%}</style><iframe id="readerFrame" srcdoc="${embeddedHtml}"></iframe>`);
  const embeddedCheck=async()=>{
    await send('Page.navigate',{url:pathToFileURL(hostFile).href});
    for(let i=0;i<60;i++){if(await evaluate(`!!document.getElementById('readerFrame')?.contentDocument?.querySelector('#root')`)){await sleep(120);break}await sleep(50)}
    return evaluate(`(()=>{const f=document.getElementById('readerFrame'),w=f.contentWindow,d=f.contentDocument;if(!d)return {accessible:false};w.scrollTo(0,d.documentElement.scrollHeight);const h=d.querySelector('header'),last=[...d.querySelectorAll('.sent')].at(-1),hr=h.getBoundingClientRect(),lr=last.getBoundingClientRect();return {accessible:true,noFooter:!d.querySelector('footer,#prev,#next,#pos'),inViewport:lr.bottom<=w.innerHeight+1,belowHeader:lr.top>=hr.bottom-1,viewport:w.innerHeight,lastBottom:lr.bottom}})()`);
  };
  await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
  const embeddedDesktop=await embeddedCheck();
  test('iframe桌面末行可见且无底部控件',embeddedDesktop.accessible&&embeddedDesktop.noFooter&&embeddedDesktop.inViewport&&embeddedDesktop.belowHeader,embeddedDesktop);
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const embeddedMobile=await embeddedCheck();
  test('iframe手机末行可见且无横向溢出',embeddedMobile.accessible&&embeddedMobile.noFooter&&embeddedMobile.inViewport&&embeddedMobile.belowHeader,embeddedMobile);
  test('全程无浏览器脚本异常',errors.length===0,errors);
}catch(e){test('浏览器测试执行',false,{message:e.message,stack:e.stack});process.exitCode=1}
finally{
  const report={browser:'Chrome headless (CDP)',timestamp:new Date().toISOString(),passed:results.filter(x=>x.status==='通过').length,failed:results.filter(x=>x.status==='失败').length,results};
  fs.writeFileSync(path.join(OUT,'browser_results.json'),JSON.stringify(report,null,2));
  console.log(`真实浏览器测试：通过 ${report.passed} / 失败 ${report.failed} / 共 ${results.length}；本地临时产物：${OUT}`);
  try{await send('Browser.close')}catch{}try{ws?.close()}catch{}proc.kill();await sleep(250);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}
  if(report.failed)process.exitCode=1;
}
