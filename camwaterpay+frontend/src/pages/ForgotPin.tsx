import { useState } from 'react'
import { api } from '../lib/api'
export default function ForgotPin(){
  const [mobile, setMobile] = useState(''); const [secret, setSecret] = useState(''); const [token, setToken] = useState(''); const [newPin, setNewPin] = useState(''); const [step, setStep] = useState(1)
  const start = async (e:any)=>{ e.preventDefault(); await api.post('/auth/forgot/start',{mobile}); setStep(2) }
  const verify = async (e:any)=>{ e.preventDefault(); const {data} = await api.post('/auth/forgot/verify',{mobile, secret_word:secret}); setToken(data.reset_token); setStep(3) }
  const reset = async (e:any)=>{ e.preventDefault(); await api.post('/auth/forgot/reset',{mobile, reset_token: token, new_pin: newPin}); alert('PIN reset. Please login.') }
  return (<div className="mt-6 space-y-4"><h1 className="text-2xl font-bold">Reset PIN</h1>
    {step===1 && (<form onSubmit={start} className="card space-y-3"><div><label className="label">Mobile</label><input className="input" value={mobile} onChange={e=>setMobile(e.target.value)}/></div><button className="btn btn-primary w-full">Continue</button></form>)}
    {step===2 && (<form onSubmit={verify} className="card space-y-3"><div><label className="label">Secret word</label><input className="input" value={secret} onChange={e=>setSecret(e.target.value)}/></div><button className="btn btn-primary w-full">Verify</button></form>)}
    {step===3 && (<form onSubmit={reset} className="card space-y-3"><div><label className="label">New PIN</label><input className="input" value={newPin} onChange={e=>setNewPin(e.target.value)}/></div><button className="btn btn-primary w-full">Set new PIN</button></form>)}
  </div>)
}
