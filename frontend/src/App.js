import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Me from "./pages/Me";
import PlacementTest from "./pages/PlacementTestPage";
import Dashboard from "./components/dashboard/Dashboard";

function PrivateRoute({ children }) {
  const { user } = React.useContext(AuthContext)
  return user ? children : <Navigate to="/login" />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/me"
            element={
              <PrivateRoute>
                <Me />
              </PrivateRoute>
            }
          />
          <Route
            path="/placement-test"
            element={
              <PrivateRoute>
                <PlacementTest />
              </PrivateRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}