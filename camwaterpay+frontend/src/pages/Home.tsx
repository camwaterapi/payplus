import { Link } from 'react-router-dom'
export default function Home(){
  return (<div className="mt-6 space-y-4">
    <h1 className="text-2xl font-bold">Camwater PAY+</h1>
    <div className="card space-y-3"><p>Top up prepaid water meters. Manage usage. Simple and fast.</p>
      <div className="grid grid-cols-2 gap-3">
        <Link to="/meters" className="btn btn-primary text-center">My meters</Link>
        <Link to="/login" className="btn border border-blue-300 text-blue-700 text-center">Sign in</Link>
      </div>
    </div>
  </div>)
}
