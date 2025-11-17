import { Route, Routes, useLocation } from "react-router-dom";
import SignIn from "./Pages/SignIn";
import Dashboard from "./Pages/Dashboard"
import SignUp from "./Pages/SignUp";
import History from "./Pages/History";
import Settings from "./Pages/Settings";
import TopNavbar from "./Components/TopNavbar"; 
import AdminRecords from "./Admin/AdminRecords";
import AdminSettings from "./Admin/AdminSettings";
import UserDashboard from "./Admin/UserDashboard";

const App = () => {
  const location = useLocation();
  const isAuthPage = location.pathname === '/' || location.pathname === '/signup';
  const isAdminPage = location.pathname.includes('/userDashboard/') || 
                      location.pathname === '/records' || 
                      location.pathname === '/adminSettings';

  return (
    <div className="min-h-screen bg-background">
      {!isAuthPage && <TopNavbar isAdmin={isAdminPage} />}
          <Routes>
        <Route path="/" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/userDashboard/:employeeId" element={<UserDashboard />} />
        <Route path="/records" element={<AdminRecords />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/adminSettings" element={<AdminSettings />} />
          </Routes>
        </div>
  )
}

export default App