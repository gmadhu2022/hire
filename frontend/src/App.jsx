import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Login from "./pages/Login";
import { ChangePassword, Register, StaticPage, ForgotPassword, ResetPassword } from "./pages/Misc";
import { ProtectedRoute } from "./components/ui";
import JobSeeker from "./pages/jobseeker/JobSeeker";
import Enterprise from "./pages/enterprise/Enterprise";
import Institute from "./pages/institute/Institute";
import Admin from "./pages/admin/Admin";

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/login/:role" element={<Login />} />
      <Route path="/register/:role" element={<Register />} />
      <Route path="/change-password" element={<ChangePassword />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/about" element={
        <StaticPage title="About us">
          <p>
            Hire is an advanced job-searching platform connecting job seekers, employers and
            institutes — covering everything from daily-wage labour to post-graduate roles.
          </p>
        </StaticPage>
      } />
      <Route path="/contact" element={
        <StaticPage title="Contact us">
          <p>Email: support@hirejobs.example · Phone: +91-00000-00000</p>
        </StaticPage>
      } />

      {/* Role dashboards */}
      <Route path="/jobseeker/*" element={
        <ProtectedRoute role="jobseeker"><JobSeeker /></ProtectedRoute>
      } />
      <Route path="/enterprise/*" element={
        <ProtectedRoute role="enterprise"><Enterprise /></ProtectedRoute>
      } />
      <Route path="/institute/*" element={
        <ProtectedRoute role="institute"><Institute /></ProtectedRoute>
      } />
      <Route path="/admin/*" element={
        <ProtectedRoute role="admin"><Admin /></ProtectedRoute>
      } />

      <Route path="*" element={<Home />} />
    </Routes>
  );
}
