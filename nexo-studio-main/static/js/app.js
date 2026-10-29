document.addEventListener('DOMContentLoaded',()=>{
 const menuButton=document.querySelector('[data-menu-toggle]'); const sidebar=document.querySelector('.sidebar');
 if(menuButton&&sidebar) menuButton.addEventListener('click',()=>sidebar.classList.toggle('mobile-open'));
 document.querySelectorAll('[data-confirm]').forEach(form=>form.addEventListener('submit',e=>{if(!confirm(form.dataset.confirm||'Deseja realmente continuar?')) e.preventDefault()}));
 document.querySelectorAll('[data-copy]').forEach(btn=>btn.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(btn.dataset.copy);const old=btn.textContent;btn.textContent='Copiado!';setTimeout(()=>btn.textContent=old,1400)}catch(e){alert(btn.dataset.copy)}}));
 const chart=document.querySelector('[data-chart-values]');
 if(chart){let values=[];try{values=JSON.parse(chart.dataset.chartValues)}catch(e){};const max=Math.max(1,...values.map(x=>x.count));chart.querySelectorAll('.bar').forEach((bar,i)=>{bar.style.height=Math.max(3,(values[i]?.count||0)/max*100)+'%';});}
});