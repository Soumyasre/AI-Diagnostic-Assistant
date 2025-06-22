// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login"; 
import Register from "./pages/Register";
import Archimedes from "./Archimedes"; 
import IQTest from "./pages/IQTest";
import LoadingPage from "./pages/LoadingPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/IQTest" element={<IQTest />} />
        <Route path="/LoadingPage" element={<LoadingPage />} />
        <Route path="/SamaVeda" element={<Archimedes />} /> {/* Route to home page */}
      </Routes>
    </Router>
  );
}

export default App;
