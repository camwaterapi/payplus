import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
export default function PaymentReturn(){
  const [sp] = useSearchParams(); const txn_id = sp.get('txn_id') || ''
  const [loading, setLoading] = useState(true); const [error, setError] = useState<string>('')
  const [tui, setTui] = useState<any>(null); const [topup, setTopup] = useState<any>(null); const [offerRemote, setOfferRemote] = useState(false)
  useEffect(()=>{(async()=>{
    try{
      if(!txn_id) { setError('Missing txn_id'); setLoading(false); return }
      const { data: t } = await api.get(`/topups/by-txn/${txn_id}`); setTopup(t)
      const { data: tuiRes } = await api.post(`/topups/${t.id}/tui`); setTui(tuiRes); setLoading(false)
      const intent = `intent://write?session=tui&tid=${tuiRes.tui_id}&return=${encodeURIComponent(window.location.origin+'/nfc/return')}#Intent;scheme=camwaterpay;package=com.camwater.payplus.nfcbridge;end`
      window.location.href = intent
    }catch(e:any){
      const msg = e?.response?.data?.detail || e?.message || 'Failed to prepare card write'
      if(msg === 'CARD_PROFILE_UNAVAILABLE_USE_REMOTE_APPLY'){ setOfferRemote(true); setError('Card write temporarily unavailable. You can apply credit to the meter remotely.') }
      else { setError(msg) }
      setLoading(false)
    }
  })()},[txn_id])
  const applyRemote = async ()=>{
    try{ setLoading(true); const meterNumber = topup?.meter_id; await api.post('/luna/workorders/loadcredit', null, { params: { meter_number: String(meterNumber), amount: Number(topup.amount) } }); alert('Remote apply initiated.') }
    catch(e:any){ alert(e?.response?.data?.detail || 'Remote apply failed') }
    finally{ setLoading(false) }
  }
  return (<div className="mt-6 space-y-4"><h1 className="text-2xl font-bold">Payment successful</h1>
    <div className="card space-y-3 text-center">
      {loading && <p>Preparing your card write…</p>}
      {error && <p className="text-red-600">{error}</p>}
      {!loading && !error && tui && (<>
        <p>Launching NFC writer… If nothing happens, tap the button below.</p>
        <a className="btn btn-primary" href={`intent://write?session=tui&tid=${tui.tui_id}&return=${encodeURIComponent(window.location.origin+'/nfc/return')}#Intent;scheme=camwaterpay;package=com.camwater.payplus.nfcbridge;end`}>Write to Card</a>
      </>)}
      {offerRemote && (<button className="btn btn-primary" onClick={applyRemote}>Apply credit to meter remotely</button>)}
    </div></div>)
}
