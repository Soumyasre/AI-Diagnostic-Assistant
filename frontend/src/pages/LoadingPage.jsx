import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "./LoadingPage.css";

export default function LoadingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user_id } = location.state || {};
  const [showSecondLine, setShowSecondLine] = useState(false);

  useEffect(() => {
    const secondLineTimer = setTimeout(() => {
      setShowSecondLine(true);
    }, 1000);

    const navigateTimer = setTimeout(() => {
      navigate("/SamaVeda", { state: { user_id } });
    }, 4000);

    return () => {
      clearTimeout(secondLineTimer);
      clearTimeout(navigateTimer);
    };
  }, [navigate, user_id]);

  return (
    <div className="loading-container">
      <div className="loading-text">
        <p className={`line one`}>Analyzing IQ Score...</p>
        {showSecondLine && <p className={`line two`}>Loading SamaVeda into your pc...</p>}
      </div>
    </div>
  );
}
