import { useState } from 'react'
import { api } from '../lib/api'
import { useNavigate } from 'react-router-dom'
export default function Register(){
  const nav = useNavigate(); const [mobile, setMobile] = useState(''); const [secret, setSecret] = useState(''); const [pin, setPin] = useState('')
  const submit = async (e:any)=>{ e.preventDefault(); const {data} = await api.post('/auth/register',{ mobile, secret_word: secret, pin }); localStorage.setItem('jwt', data.access_token); nav('/meters') }
  return (<div className="space-y-4 mt-6"><h1 className="text-2xl font-bold">Create Account</h1>
    <form onSubmit={submit} className="card space-y-3">
      <div><label className="label">Mobile number</label><input className="input" value={mobile} onChange={e=>setMobile(e.target.value)} placeholder="+2376…"/></div>
      <div><label className="label">Secret word</label><input className="input" value={secret} onChange={e=>setSecret(e.target.value)} placeholder="e.g. mother's village"/></div>
      <div><label className="label">PIN</label><input className="input" type="password" value={pin} onChange={e=>setPin(e.target.value)} placeholder="4–12 digits"/></div>
      <button className="btn btn-primary w-full">Sign up</button>
    </form></div>)
}
