import { Link, Routes, Route } from "react-router-dom";
import ComplaintForm from "./features/citizen/ComplaintForm";

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
