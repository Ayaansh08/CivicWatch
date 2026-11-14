import { Link, Routes, Route } from "react-router-dom";

/** Displays the CivicWatch home page. */
function Home() {
  return (
    <main>
      <h1>CivicWatch</h1>
      <p>Report and track civic issues in your community.</p>
      <Link to="/report">Report an issue</Link>
    </main>
  );
}

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
