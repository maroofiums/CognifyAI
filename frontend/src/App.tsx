import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import HistoryPage from "./pages/History";
import HomePage from "./pages/Home";
import ResultsPage from "./pages/Results";

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <main className="app-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/analysis/:id" element={<ResultsPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <span>CognifyAI - AI Code Optimiser Platform</span>
      </footer>
    </div>
  );
}
