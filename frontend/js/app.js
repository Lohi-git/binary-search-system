const API='';  // same origin by default. frontend on another port? use 'http://127.0.0.1:5000'
const DOWN='Cannot reach the backend. Run python app.py inside the backend folder.';
const $=s=>document.querySelector(s);
const row=$('#row'),msg=$('#msg'),log=$('#log'),code=$('#code'),err=$('#err');
let A=[],T=0,mode='any',steps=[],cur=0,timer=null,lin=1;

// python code per mode, line numbers here are what the steps point at
const CODE={any:['def binary_search(a, target):','    lo, hi = 0, len(a) - 1','    while lo <= hi:','        mid = (lo + hi) // 2','        if a[mid] == target:','            return mid','        elif a[mid] < target:','            lo = mid + 1','        else:','            hi = mid - 1','    return -1'],
first:['def first_occurrence(a, target):','    lo, hi, ans = 0, len(a) - 1, -1','    while lo <= hi:','        mid = (lo + hi) // 2','        if a[mid] == target:','            ans = mid','            hi = mid - 1','        elif a[mid] < target:','            lo = mid + 1','        else:','            hi = mid - 1','    return ans']};
CODE.last=[...CODE.first];CODE.last[0]='def last_occurrence(a, target):';CODE.last[6]='            lo = mid + 1';

// the backend does the searching now, we just replay the steps it sends back
async function build(){
  let r;
  try{r=await fetch(API+'/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({array:A,target:T,mode})})}
  catch(e){throw new Error(DOWN)}
  const d=await r.json();
  if(!r.ok)throw new Error(d.error);
  steps=d.steps;lin=d.linear;
}

function draw(){
  const s=steps[cur],live=s.lo<=s.hi,tot=steps[steps.length-1].c;
  row.innerHTML=A.map((v,i)=>{
    const p=[];let c='t';
    if(!live||i<s.lo||i>s.hi)c+=' out';
    if(live&&i===s.lo){p.push('lo');c+=' lo'}
    if(i===s.mid){p.push('mid');c+=' mid'}
    if(live&&i===s.hi){p.push('hi');c+=' hi'}
    if(i===s.ans)c+=' cand';
    if(s.done==='ok'&&i===s.res)c+=' ok';
    return `<div class="${c}"><b>${v}</b><i>${i}</i><em>${p.join('/')}</em></div>`;
  }).join('');
  msg.textContent=`Step ${cur+1} of ${steps.length}. ${s.msg}`;
  msg.className='msg '+(s.done||'');
  [...code.children].forEach((e,i)=>e.classList.toggle('on',i===s.ln));
  [...log.children].forEach((e,i)=>e.classList.toggle('on',i===cur));
  const li=log.children[cur];log.scrollTop=li.offsetTop-log.clientHeight/2;
  $('#bc').textContent=s.c;$('#lc').textContent=lin;
  $('#bb').style.width=Math.max(2,Math.min(100,s.c/lin*100))+'%';
  $('#note').textContent=!s.done?'':lin>tot?`${(lin/tot).toFixed(1)}× fewer comparisons than a linear scan.`:'Tiny list or a lucky target, so the linear scan ties or wins here. Grow the list to see the gap.';
  $('#back').disabled=cur===0;$('#next').disabled=cur===steps.length-1;
}
const go=i=>{cur=Math.max(0,Math.min(steps.length-1,i));draw()};
function stop(){clearInterval(timer);timer=null;$('#play').textContent='Play'}
function play(){
  if(timer)return stop();
  if(cur>=steps.length-1)go(0);
  $('#play').textContent='Pause';
  timer=setInterval(()=>{if(cur>=steps.length-1)return stop();go(cur+1)},1800/$('#spd').value);
}
async function rebuild(){
  stop();
  try{await build();err.textContent=''}catch(e){err.textContent=e.message;return}
  code.innerHTML=CODE[mode].map(l=>`<span>${l}</span>`).join('');
  log.innerHTML=steps.map((s,i)=>`<li data-i="${i}">${s.msg}</li>`).join('');
  go(0);
}
function pickTarget(){
  const dup=A.filter((v,i)=>A[i+1]===v),pool=(mode!=='any'&&dup.length)?dup:A;
  if(mode==='any'&&Math.random()<.25){ // sometimes a miss, so the not-found path shows up
    const top=A[A.length-1]+5,r=()=>1+Math.floor(Math.random()*top);let x=r();
    for(let k=0;k<50&&A.includes(x);k++)x=r();T=x;
  }else T=pool[Math.floor(Math.random()*pool.length)];
  $('#tgt').value=T;rebuild();
}
async function newList(){
  try{A=(await (await fetch(API+'/api/random-list?size='+$('#size').value)).json()).array}
  catch(e){err.textContent=DOWN;return}
  err.textContent='';pickTarget();
}

$('#size').oninput=()=>{$('#sizeo').textContent=$('#size').value};
$('#size').onchange=newList;$('#newl').onclick=newList;$('#rand').onclick=pickTarget;
$('#use').onclick=()=>{
  const nums=$('#mine').value.split(/[\s,;]+/).filter(Boolean).map(Number);
  if(!nums.length||nums.length>60||nums.some(x=>!Number.isInteger(x)||Math.abs(x)>9999)){err.textContent='Use 1 to 60 whole numbers (up to 9999), separated by commas.';return}
  err.textContent='';A=nums.sort((a,b)=>a-b);pickTarget();
};
$('#tgt').onchange=()=>{if($('#tgt').value==='')return;T=+$('#tgt').value;rebuild()};
$('#mode').onclick=e=>{
  const b=e.target.closest('button');if(!b)return;
  mode=b.dataset.m;[...$('#mode').children].forEach(x=>x.classList.toggle('on',x===b));pickTarget();
};
$('#play').onclick=play;
$('#next').onclick=()=>{stop();go(cur+1)};
$('#back').onclick=()=>{stop();go(cur-1)};
$('#reset').onclick=()=>{stop();go(0)};
$('#spd').oninput=()=>{if(timer){stop();play()}};
log.onclick=e=>{const li=e.target.closest('li');if(li){stop();go(+li.dataset.i)}};
document.onkeydown=e=>{
  if(e.target.matches('input,button'))return;
  if(e.key==='ArrowRight')$('#next').click();
  if(e.key==='ArrowLeft')$('#back').click();
  if(e.key===' '){e.preventDefault();play()}
};
$('#copy').onclick=async()=>{
  const txt=CODE[mode].join('\n');
  try{await navigator.clipboard.writeText(txt)}catch(e){
    const ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy')}catch(_){}ta.remove();
  }
  $('#copy').textContent='Copied';setTimeout(()=>$('#copy').textContent='Copy code',1200);
};

// scale table
$('#sc').innerHTML='<tr><th>List size</th><th>Binary search, worst case</th><th>Linear search, worst case</th></tr>'+
  [1e3,1e6,1e9,8e9].map(n=>`<tr><td>${n.toLocaleString()}</td><td>${Math.ceil(Math.log2(n+1))} comparisons</td><td>${n.toLocaleString()} comparisons</td></tr>`).join('');

// benchmark runs in python on the backend
$('#bench').onclick=async()=>{
  const b=$('#bench'),br=$('#br');b.disabled=true;br.textContent='Running in Python on the backend…';
  try{
    const d=await (await fetch(API+'/api/benchmark')).json();
    br.textContent=`${d.queries} searches in ${d.n.toLocaleString()} sorted numbers (pure Python): linear ${d.linear_ms} ms, binary ${d.binary_ms} ms, about ${Math.round(d.linear_ms/d.binary_ms).toLocaleString()}× faster.`;
  }catch(e){br.textContent=DOWN}
  b.disabled=false;
};

newList();
