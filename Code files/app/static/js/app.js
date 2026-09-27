window.PocketSmart=(()=> {
const money=v=>`₹${Number(v||0).toLocaleString("en-IN",{maximumFractionDigits:0})}`;
const msg=(id,t,ok=false)=>{const e=document.getElementById(id);if(e){e.textContent=t||"";e.className=`form-message${ok?" success":""}`}};
async function api(url,opt={}){const r=await fetch(url,{credentials:"same-origin",...opt});let d={};try{d=await r.json()}catch(_){}if(!r.ok)throw Error(d.detail||"Something went wrong.");return d}
function initRegister(){const f=document.getElementById("register-form");if(!f)return;f.addEventListener("submit",async e=>{e.preventDefault();msg("form-message","");try{await api("/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(f).entries()))});msg("form-message","Account created. Redirecting...",true);setTimeout(()=>location.href="/login",700)}catch(x){msg("form-message",x.message)}})}
function initLogin(){const f=document.getElementById("login-form");if(!f)return;f.addEventListener("submit",async e=>{e.preventDefault();msg("form-message","");try{await api("/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(Object.fromEntries(new FormData(f).entries()))});location.href="/dashboard"}catch(x){msg("form-message",x.message)}})}
function item(){return `<div class="home-item"><label>Room<select class="room"><option>Living Room</option><option>Kitchen</option><option>Bedroom</option><option>Dining Room</option><option>Study Room</option><option>Bathroom</option></select></label><label>Item<input class="item" required placeholder="Ceiling fan"></label><label>Quantity<input class="quantity" type="number" min="1" max="50" value="1"></label><button class="remove-item" type="button">×</button></div>`}
function initHomePlanner(){const f=document.getElementById("home-form"),list=document.getElementById("home-items");if(!f)return;list.innerHTML=item();document.getElementById("add-home-item").onclick=()=>list.insertAdjacentHTML("beforeend",item());list.onclick=e=>{if(e.target.classList.contains("remove-item")&&list.children.length>1)e.target.closest(".home-item").remove()};f.onsubmit=async e=>{e.preventDefault();msg("home-message","Generating your plan...");const rooms=[...list.querySelectorAll(".home-item")].map(r=>({room:r.querySelector(".room").value,item:r.querySelector(".item").value.trim(),quantity:Number(r.querySelector(".quantity").value)}));try{const d=await api("/generate-home",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({budget:Number(f.budget.value),style:f.style.value,rooms,notes:f.notes.value.trim()})});sessionStorage.setItem("pocketsmart_result",JSON.stringify(d));location.href="/recommendations"}catch(x){msg("home-message",x.message)}}}
function initPartyPlanner(){const f=document.getElementById("party-form");if(!f)return;f.onsubmit=async e=>{e.preventDefault();msg("party-message","Generating your party plan...");const d={budget:Number(f.budget.value),guests:Number(f.guests.value),event_type:f.event_type.value,venue_details:f.venue_details.value.trim(),location:f.location.value.trim(),food_preference:f.food_preference.value,notes:f.notes.value.trim()};try{const r=await api("/generate-party",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(d)});sessionStorage.setItem("pocketsmart_result",JSON.stringify(r));location.href="/recommendations"}catch(x){msg("party-message",x.message)}}}
function initJewelryPlanner(){const f=document.getElementById("jewelry-form");if(!f)return;f.onsubmit=async e=>{e.preventDefault();msg("jewelry-message","Analyzing your preferences and generating recommendations...");try{const r=await api("/generate-jewelry",{method:"POST",body:new FormData(f)});sessionStorage.setItem("pocketsmart_result",JSON.stringify(r));location.href="/recommendations"}catch(x){msg("jewelry-message",x.message)}}}
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
function renderResult(r){const t=document.getElementById("recommendation-output");if(!t)return;const a=(r.allocation||[]).map(x=>`<div class="allocation-row"><div class="allocation-top"><span>${esc(x.category)}</span><span>${money(x.amount)} · ${Number(x.percentage||0).toFixed(0)}%</span></div><div class="allocation-bar"><span style="width:${Math.min(100,Number(x.percentage||0))}%"></span></div></div>`).join("");const rec=(r.recommendations||[]).map(x=>`<article class="recommendation-card"><div class="rec-top"><h3>${esc(x.name)}</h3><span class="price">${money(x.estimated_price)}</span></div><div class="platform">${esc(x.platform||"Platform")}${x.quantity>1?` · Qty ${x.quantity}`:""}</div><p class="rec-desc">${esc(x.description||"")}</p><p class="reason"><strong>Why:</strong> ${esc(x.reason||"")}</p>${x.url?`<a class="rec-link" target="_blank" rel="noopener noreferrer" href="${esc(x.url)}">Search on ${esc(x.platform)} →</a>`:""}</article>`).join("");t.innerHTML=`<div class="result-head"><span class="ai-badge">${r.ai_used?"GEMINI AI":"BUDGET FALLBACK"}</span><h1>${esc(r.title)}</h1><p>${esc(r.summary)}</p><strong>Budget: ${money(r.budget)}</strong></div><div class="result-grid"><div class="result-card"><h2>Budget Allocation</h2>${a||"<p>No allocation returned.</p>"}</div><div class="result-card"><h2>Recommended Options</h2>${rec||"<p>No recommendations returned.</p>"}</div></div>`}
async function initRecommendationPage(){
const t=document.getElementById("recommendation-output");
const params=new URLSearchParams(location.search);
const detailId=params.get("id");
if(detailId){
  try{
    const d=await api(`/recommendations-details/${encodeURIComponent(detailId)}`);
    const r=d.result;
    r.recommendation_id=d.id;
    r.planner_type=d.planner_type;
    r.budget=d.input.budget;
    renderResult(r);
    return;
  }catch(x){
    t.innerHTML=`<div class="result-card"><h2>Recommendation unavailable</h2><p>${esc(x.message)}</p><a class="btn btn-primary" href="/history">Back to history</a></div>`;
    return;
  }
}
const raw=sessionStorage.getItem("pocketsmart_result");
if(!raw){
  t.innerHTML=`<div class="result-card"><h2>No recommendation selected</h2><p>Generate a plan from a planner first.</p><a class="btn btn-primary" href="/dashboard">Go to Dashboard</a></div>`;
  return;
}
try{renderResult(JSON.parse(raw))}catch(_){}
}
function card(x){
return `<article class="history-card"><span class="tag">${esc(x.planner_type)}</span><h3>${esc(x.title)}</h3><p>${esc(x.summary)}</p><div class="meta">${money(x.budget)} · ${new Date(x.created_at).toLocaleString()}</div><a class="rec-link" href="/recommendations?id=${encodeURIComponent(x.id)}">Open details →</a></article>`
}
async function loadHistory(){const t=document.getElementById("history-list");if(!t)return;try{const d=await api("/history");t.innerHTML=d.length?d.map(card).join(""):`<div class="result-card"><h2>No history yet</h2><p>Create your first recommendation.</p></div>`}catch(x){t.innerHTML=`<div class="result-card"><p>${esc(x.message)}</p></div>`}}
async function loadDashboard(){const t=document.getElementById("recent-list");if(!t)return;try{const d=await api("/session-data");const rows=d.recent_recommendations||[];t.innerHTML=rows.length?rows.map(card).join(""):`<div class="result-card"><h2>Start your first plan</h2><p>Your generated recommendations will appear here.</p></div>`}catch(x){t.innerHTML=`<div class="result-card"><p>${esc(x.message)}</p></div>`}}
return{initRegister,initLogin,initHomePlanner,initPartyPlanner,initJewelryPlanner,initRecommendationPage,loadHistory,loadDashboard}})();
if(location.pathname==="/recommendations")window.PocketSmart.initRecommendationPage();
