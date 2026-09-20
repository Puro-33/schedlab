'use strict';
const $ = id => document.getElementById(id);
const palette = ['#7662d8', '#55a69a', '#e3a760', '#7096d1', '#bc7fa7', '#8da772', '#c87c72', '#8b8cab'];
const names = {fcfs:'FCFS', sjf:'SJF', srtf:'SRTF', rr:'RR', priority:'Priority', hrrn:'HRRN'};
let results = null, snapshot = null, selected = 'fcfs', benchmarkResult = null, timer = null, busy = false;

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function status(message, error = false) { $('status').textContent = message; $('status').classList.toggle('error', error); }
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {} : {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}
function syncButtons() {
  $('save').disabled = !results;
  $('export-json').disabled = !results;
  $('benchmark-export').disabled = !benchmarkResult;
  $('add-process').disabled = $('process-rows').children.length >= 100;
}
async function action(work) {
  if (busy) return;
  busy = true;
  stop();
  const controls = [...document.querySelectorAll('button,input,select')];
  const previous = controls.map(node => node.disabled);
  controls.forEach(node => node.disabled = true);
  try { await work(); } catch (error) { status(error.message, true); }
  finally { controls.forEach((node,i) => node.disabled = previous[i]); busy = false; syncButtons(); }
}
function readInteger(id) {
  const field = $(id);
  if (!field.checkValidity() || field.value === '') throw new Error(`Check the ${id} field`);
  return Number(field.value);
}
function config() { return {seed:readInteger('seed'), count:readInteger('count'), profile:$('profile').value, quantum:readInteger('quantum')}; }
function invalidate() {
  results = snapshot = null;
  $('results').hidden = true;
  stop(); syncButtons();
  $('insight').replaceChildren(el('span','06','insight-number'),el('p','Scheduling policies, ready for a fair comparison.'));
  status('Workload changed. Compare policies to update the results.');
}
function processRow(row) {
  const tr = el('tr');
  for (const key of ['id','arrival','burst','priority']) {
    const td = el('td'), field = el('input');
    field.value = row[key] ?? 0; field.dataset.key = key;
    field.setAttribute('aria-label', `${row.id} ${key}`);
    if (key === 'id') { field.className = 'pid'; field.maxLength = 24; field.pattern = '[A-Za-z0-9_-]{1,24}'; }
    else { field.type = 'number'; field.min = key === 'burst' ? 1 : 0; field.max = key === 'arrival' ? 10000 : key === 'burst' ? 1000 : 99; }
    field.required = true;
    field.addEventListener('input', invalidate);
    td.append(field); tr.append(td);
  }
  const td = el('td'), remove = el('button','×','remove');
  remove.setAttribute('aria-label',`Remove ${row.id}`);
  remove.addEventListener('click', () => {tr.remove(); updateCount(); invalidate();});
  td.append(remove); tr.append(td); return tr;
}
function updateCount() { $('process-count').textContent = `${$('process-rows').children.length} PROCESSES`; }
function setRows(rows) { $('process-rows').replaceChildren(...rows.map(processRow)); updateCount(); invalidate(); }
function readRows() {
  return [...$('process-rows').children].map(tr => Object.fromEntries([...tr.querySelectorAll('input')].map(field => {
    if (!field.checkValidity()) throw new Error(`Invalid ${field.dataset.key} in workload`);
    return [field.dataset.key, field.dataset.key === 'id' ? field.value : Number(field.value)];
  })));
}
async function runComparison() {
  const processes = readRows(), quantum = readInteger('quantum');
  status('Comparing six scheduling policies…');
  const response = await api('/api/compare', {processes, quantum});
  results = response.results; snapshot = {processes, quantum, engine_version:'1.0.0'};
  $('results').hidden = false; renderCards(); renderSelected(); syncButtons();
  status(`Compared all six policies across ${processes.length} processes. All times are simulation units.`);
}
const fmt = value => Number.isInteger(value) ? String(value) : value.toFixed(2);
function color(pid) { if (pid === null) return '#d3d8e0'; return palette[snapshot.processes.findIndex(p => p.id === pid) % palette.length]; }
function current() { return results.find(result => result.algorithm === selected); }
function renderCards() {
  const metric = $('metric').value;
  const values = results.map(result => result.metrics[metric]);
  const best = Math.min(...values), max = Math.max(...values, 1);
  $('policy-cards').replaceChildren(...results.map(result => {
    const card = el('button',undefined,'policy-card' + (selected === result.algorithm ? ' selected' : ''));
    card.setAttribute('aria-pressed', String(selected === result.algorithm));
    card.setAttribute('aria-label',`${result.label}: ${fmt(result.metrics[metric])}`);
    card.append(el('span',names[result.algorithm],'policy-name'),el('span',fmt(result.metrics[metric]),'policy-value'));
    if (result.metrics[metric] === best) card.append(el('span','BEST','best'));
    const bar = el('div',undefined,'bar'), fill = el('i'); fill.style.width = `${result.metrics[metric]/max*100}%`; bar.append(fill); card.append(bar);
    card.addEventListener('click', () => { if (busy) return; selected = result.algorithm; renderCards(); renderSelected(); });
    return card;
  }));
  const winners = results.filter(r => r.metrics[metric] === best).map(r => names[r.algorithm]);
  $('insight').replaceChildren(el('span',fmt(best),'insight-number'),el('p',`${winners.join(' / ')} achieves the lowest ${$('metric').selectedOptions[0].textContent.toLowerCase()} on this workload.`));
}
function renderSelected() {
  stop();
  const result = current(), end = result.metrics.makespan;
  $('selected-policy').textContent = names[selected];
  $('timeline-legend').replaceChildren(...[...snapshot.processes.map(p=>p.id),null].map(pid=>{
    const item = el('span'), swatch = el('i'); swatch.style.background = color(pid); item.append(swatch,document.createTextNode(pid ?? 'Idle')); return item;
  }));
  const track = el('div',undefined,'timeline-track');
  for (const segment of result.timeline) {
    const block = el('div', segment.id ?? 'Idle', 'segment');
    block.style.width = `${(segment.end-segment.start)/end*100}%`; block.style.background = color(segment.id);
    block.title = `${segment.id ?? 'Idle'}: ${segment.start}–${segment.end}`; track.append(block);
  }
  const timeline = $('timeline'); timeline.style.minWidth = `${Math.max(600, Math.min(6000, result.timeline.length*28))}px`;
  timeline.replaceChildren(track);
  const cursor = el('div',undefined,'cursor'); cursor.id = 'time-cursor'; timeline.append(cursor);
  for (let i=0;i<=10;i++) { const tick = el('span',fmt(end*i/10),'axis-label'); tick.style.left=`${i*10}%`; timeline.append(tick); }
  $('scrubber').max = end; $('scrubber').value = 0;
  $('outcomes').replaceChildren(...result.processes.map(p=>{ const tr=el('tr'); for (const key of ['id','completion','turnaround','waiting','response']) tr.append(el('td',p[key])); return tr; }));
  $('statistics').replaceChildren(...[
    ['CPU utilization', `${(result.metrics.utilization*100).toFixed(1)}%`], ['Total elapsed', `${end} units`],
    ['Throughput',`${result.metrics.throughput.toFixed(3)} jobs/unit`],['Context switches',result.metrics.context_switches],
    ['Max waiting',`${result.metrics.max_waiting} units`],['Mean slowdown',`${result.metrics.mean_slowdown.toFixed(2)}×`]
  ].map(([label,value])=>{const row=el('div'); row.append(el('dt',label),el('dd',value));return row;}));
  renderTime();
}
function renderTime() {
  if (!results) return;
  const t=Number($('scrubber').value), result=current();
  $('clock').textContent=`t = ${t}`;
  $('time-cursor').style.left=`${t/result.metrics.makespan*100}%`;
  const active=result.timeline.find(s=>s.start<=t && t<s.end)?.id;
  $('running-label').textContent=t===result.metrics.makespan?'Completed':active?`Running ${active}`:'CPU idle';
  const ready=result.processes.filter(p=>p.arrival<=t && p.completion>t && p.id!==active).map(p=>p.id);
  $('ready-queue').textContent=ready.length?ready.join(' · '):'No processes waiting';
}
function stop() { if(timer) clearInterval(timer); timer=null; $('play').textContent='▶ Play'; }
function download(name, content, type) {
  const url=URL.createObjectURL(new Blob([content],{type})), link=el('a'); link.href=url; link.download=name; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function csv(rows) { const keys=Object.keys(rows[0]); return [keys,...rows.map(row=>keys.map(key=>row[key]))].map(row=>row.map(value=>`"${String(value).replaceAll('"','""')}"`).join(',')).join('\n'); }
async function loadNotebook() {
  const runs=await api('/api/experiments');
  $('saved-runs').replaceChildren(...(runs.length ? runs.map(run=>{
    const row=el('div',undefined,'saved-run'), info=el('div'), load=el('button','Load run','button secondary');
    info.append(el('strong',run.name),el('small',new Date(run.created).toLocaleString()));
    load.addEventListener('click',()=>action(async()=>{
      const stored=await api(`/api/experiments/${run.id}`);
      setRows(stored.payload.processes); $('quantum').value=stored.payload.quantum; $('experiment-name').value=stored.name;
      await runComparison(); $('laboratory').scrollIntoView({behavior:'smooth'});
    })); row.append(info,load); return row;
  }) : [el('p','No saved experiments yet. Run a comparison and save your first result.','muted')]));
}
$('generate').addEventListener('click',()=>action(async()=>{const response=await api('/api/generate',config());setRows(response.processes);status('Generated a reproducible workload. Compare policies to see the results.');}));
$('add-process').addEventListener('click',()=>{const ids=readRows().map(p=>p.id);let i=1;while(ids.includes(`P${i}`))i++;$('process-rows').append(processRow({id:`P${i}`,arrival:0,burst:5,priority:0}));updateCount();invalidate();});
$('quantum').addEventListener('input',invalidate);
$('run').addEventListener('click',()=>action(runComparison));
$('metric').addEventListener('change',()=>{if(results)renderCards();});
$('scrubber').addEventListener('input',()=>{stop();renderTime();});
$('play').addEventListener('click',()=>{
  if(timer){stop();return;} if(Number($('scrubber').value)>=current().metrics.makespan)$('scrubber').value=0;
  $('play').textContent='Ⅱ Pause';timer=setInterval(()=>{ $('scrubber').value=Math.min(Number($('scrubber').value)+1,current().metrics.makespan);renderTime();if(Number($('scrubber').value)>=current().metrics.makespan)stop(); },100);
});
$('export-json').addEventListener('click',()=>download('schedlab-run.json',JSON.stringify({...snapshot,results},null,2),'application/json'));
$('export-csv').addEventListener('click',()=>download(`schedlab-${selected}.csv`,csv(current().processes),'text/csv'));
$('import-file').addEventListener('change',()=>action(async()=>{
  const file=$('import-file').files[0];if(!file)return;
  try {
    if(file.size>8*1024*1024)throw new Error('Import is limited to 8 MB');
    const value=JSON.parse(await file.text());
    const rows=Array.isArray(value)?value:value.processes;
    const quantum=Array.isArray(value)?readInteger('quantum'):value.quantum??readInteger('quantum');
    await api('/api/compare',{processes:rows,quantum});
    setRows(rows);$('quantum').value=quantum;await runComparison();
  } finally {$('import-file').value='';}
}));
$('benchmark').addEventListener('click',()=>action(async()=>{
  status('Running repeated, paired experiments…');
  benchmarkResult=await api('/api/benchmark',{...config(),repeats:readInteger('repeats')});
  const c=benchmarkResult.config;
  $('benchmark-config').textContent=`${c.profile} · ${c.count} processes · seeds ${c.seed}–${c.seed+c.repeats-1} · quantum ${c.quantum}`;
  const table=el('table'),thead=el('thead'),head=el('tr');
  for(const label of ['Policy','Waiting','Response','Turnaround','P95 waiting','Switches'])head.append(el('th',label));
  thead.append(head);table.append(thead);const tbody=el('tbody');
  for(const row of benchmarkResult.summary){const tr=el('tr');tr.append(el('td',names[row.algorithm]));for(const key of ['mean_waiting','mean_response','mean_turnaround','p95_waiting','context_switches']){const m=row.metrics[key];tr.append(el('td',`${m.mean.toFixed(2)} ± ${m.stddev.toFixed(2)}`));}tbody.append(tr);}
  table.append(tbody);$('benchmark-results').replaceChildren(table,el('p','Values show mean ± sample standard deviation across repetitions. Lower is better for these metrics.','muted'));
  status(`Benchmark complete: ${c.repeats*6} simulations across ${c.repeats} paired workloads.`);
}));
$('benchmark-export').addEventListener('click',()=>download('schedlab-benchmark.json',JSON.stringify(benchmarkResult,null,2),'application/json'));
$('save').addEventListener('click',()=>action(async()=>{await api('/api/experiments',{name:$('experiment-name').value,processes:snapshot.processes,quantum:snapshot.quantum});await loadNotebook();status('Experiment saved locally with its workload, settings, and results.');}));
action(async()=>{const data=await api('/api/generate',config());setRows(data.processes);await runComparison();await loadNotebook();});
