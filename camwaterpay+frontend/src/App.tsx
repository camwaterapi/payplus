import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPin from './pages/ForgotPin'
import Home from './pages/Home'
import TopUp from './pages/TopUp'
import PaymentReturn from './pages/PaymentReturn'
import NFCReturn from './pages/NFCReturn'
import Meters from './pages/Meters'

function IconHome(){ return (<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><path d="M3 10.5L12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-10.5z" stroke="currentColor" strokeWidth="1.6"/></svg>) }
function IconMeter(){ return (<svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6"/><path d="M12 12l4-4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>) }

function NavBar() {
  const loc = useLocation()
  const tabs = [{ to: '/', label: 'Home', icon: <IconHome/> }, { to: '/meters', label: 'Meters', icon: <IconMeter/> }]
  return (
    <nav className="navbar">
      {tabs.map(t => {
        const active = loc.pathname===t.to
        return <Link key={t.to} to={t.to} className={`nav-item ${active? 'text-blue-700':'text-gray-600'}`}>{t.icon}<span>{t.label}</span></Link>
      })}
    </nav>
  )
}
export default function App(){
  return (<div className="max-w-md mx-auto pb-20 px-4">
    <Routes>
      <Route path="/login" element={<Login/>} />
      <Route path="/register" element={<Register/>} />
      <Route path="/forgot" element={<ForgotPin/>} />
      <Route path="/topup/:meterId" element={<TopUp/>} />
      <Route path="/pay/return" element={<PaymentReturn/>} />
      <Route path="/nfc/return" element={<NFCReturn/>} />
      <Route path="/meters" element={<Meters/>} />
      <Route path="/" element={<Home/>} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
    <NavBar/>
  </div>)
}
