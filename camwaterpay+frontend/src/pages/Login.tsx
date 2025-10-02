import { useState } from 'react'
import { api } from '../lib/api'
import { useNavigate, Link } from 'react-router-dom'
export default function Login(){
  const nav = useNavigate(); const [mobile, setMobile] = useState(''); const [pin, setPin] = useState('')
  const submit = async (e:any)=>{ e.preventDefault(); const {data} = await api.post('/auth/login',{ mobile, pin }); localStorage.setItem('jwt', data.access_token); nav('/meters') }
  return (<div className="space-y-4 mt-6"><h1 className="text-2xl font-bold">Welcome back</h1>
    <form onSubmit={submit} className="card space-y-3">
      <div><label className="label">Mobile number</label><input className="input" value={mobile} onChange={e=>setMobile(e.target.value)}/></div>
      <div><label className="label">PIN</label><input className="input" type="password" value={pin} onChange={e=>setPin(e.target.value)}/></div>
      <button className="btn btn-primary w-full">Login</button>
      <div className="text-sm text-center"><Link to="/register" className="text-blue-600">Create account</Link> · <Link to="/forgot" className="text-blue-600">Forgot PIN?</Link></div>
    </form></div>)
}
