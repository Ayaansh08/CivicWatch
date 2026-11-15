import { Link, Routes, Route } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";

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

/** Defines the application routes. */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/report" element={<ComplaintForm />} />
    </Routes>
  );
}

export default App;
