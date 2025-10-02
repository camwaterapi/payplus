import { useEffect, useState } from 'react'
import { api } from '../lib/api'
export default function Meters(){
  const [meters, setMeters] = useState<any[]>([]); const [number, setNumber] = useState(''); const [alias, setAlias] = useState('')
  const load = async ()=>{ const {data} = await api.get('/meters'); setMeters(data) }
  const link = async (e:any)=>{ e.preventDefault(); await api.post('/meters/link', null, { params: { meter_number: number, alias } }); setNumber(''); setAlias(''); load() }
  useEffect(()=>{ load() },[])
  return (<div className="mt-6 space-y-4"><h1 className="text-2xl font-bold">Your meters</h1>
    <div className="space-y-3">{meters.map(m=> (<div key={m.id} className="card flex items-center justify-between">
      <div><div className="font-semibold">{m.alias || 'Meter'}</div><div className="text-sm text-gray-500">{m.meter_number}</div></div>
      <a className="btn btn-primary" href={`/topup/${m.id}`}>Top up</a></div>))}</div>
    <form onSubmit={link} className="card space-y-3">
      <div><label className="label">Meter number</label><input className="input" value={number} onChange={e=>setNumber(e.target.value)}/></div>
      <div><label className="label">Alias (optional)</label><input className="input" value={alias} onChange={e=>setAlias(e.target.value)}/></div>
      <button className="btn btn-primary w-full">Link meter</button>
    </form></div>)
}
