import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'
import MapView from './features/geo/MapView'

function App() {
  const [count, setCount] = useState(0)

/** Displays the CivicWatch home page. */
function Home() {
  return (
    <>
      <MapView />
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Get started</h1>
          <p>
            Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
          </p>
        </div>
        <button
          type="button"
          className="counter"
          onClick={() => setCount((count) => count + 1)}
        >
          Count is {count}
        </button>
      </section>

      <div className="ticks"></div>

/** Displays the placeholder for the complaint reporting page. */
function Report() {
  return (
    <main>
      <h1>Report a Complaint</h1>
      <p>The complaint form will be added here.</p>
      <Link to="/">Back to Home</Link>
    </main>
  );
}

/** Defines the application routes. Teammates add their own routes here. */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/report" element={<Report />} />
    </Routes>
  );
}

export default App;
