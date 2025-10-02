import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'
export default function TopUp(){
  const { meterId } = useParams(); const [amount, setAmount] = useState(''); const [method, setMethod] = useState('stripe')
  const pay = async (e:any)=>{ e.preventDefault()
    const { data } = await api.post('/payments/init', { meter_id: Number(meterId), amount: Number(amount), method })
    window.location.href = data.checkout_url
  }
  return (<div className="mt-6 space-y-4"><h1 className="text-2xl font-bold">Top up</h1>
    <form onSubmit={pay} className="card space-y-3">
      <div><label className="label">Amount</label><input className="input" value={amount} onChange={e=>setAmount(e.target.value)} placeholder="e.g. 2000"/></div>
      <div className="flex gap-3"><label className="flex items-center gap-2"><input type="radio" checked={method==='stripe'} onChange={()=>setMethod('stripe')}/>Stripe</label>
      <label className="flex items-center gap-2"><input type="radio" checked={method==='flutterwave'} onChange={()=>setMethod('flutterwave')}/>Flutterwave</label></div>
      <button className="btn btn-primary w-full">Pay</button>
    </form></div>)
}
