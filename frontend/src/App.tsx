import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="App">
      <h1>GeoRisk - Geographic Risk Assessment</h1>
      <p>Interactive map and risk visualization coming soon...</p>
      <button onClick={() => setCount(count + 1)}>
        Test Counter: {count}
      </button>
    </div>
  )
}

export default App
