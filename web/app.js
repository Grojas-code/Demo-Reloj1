const el = id => document.getElementById(id)

async function load(){
  const res = await fetch('/api/agenda')
  const data = await res.json()
  const list = el('list')
  list.innerHTML = ''
  data.sort((a,b)=> (a.datetime||'').localeCompare(b.datetime||''))
  data.forEach(n=>{
    const d = document.createElement('div')
    d.className = 'note'
    d.innerHTML = `<b>${n.datetime}</b> - ${n.text} ${n.repeat!=='None'?'<i>('+n.repeat+')</i>':''}`
    const actions = document.createElement('div')
    actions.className='actions'
    const del = document.createElement('button')
    del.textContent='Eliminar'
    del.onclick = async ()=>{
      await fetch('/api/agenda/'+n.id, {method:'DELETE'})
      load()
    }
    const comp = document.createElement('button')
    comp.textContent='Marcar completado'
    comp.onclick = async ()=>{
      await fetch('/api/agenda/'+n.id+'/complete', {method:'PUT'})
      load()
    }
    actions.appendChild(del)
    actions.appendChild(comp)
    d.appendChild(actions)
    list.appendChild(d)
  })
}

el('add').onclick = async ()=>{
  const text = el('text').value.trim()
  const date = el('date').value
  const time = el('time').value
  const repeat = el('repeat').value
  if(!text || !date || !time){ alert('Complete todos los campos'); return }
  const datetime = date + ' ' + time
  await fetch('/api/agenda', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text, datetime, repeat})})
  el('text').value=''
  load()
}

load()
