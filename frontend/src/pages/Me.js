import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 
import { AuthContext } from "../context/AuthContext";
import API from "../api";

export default function Me() {
  const { logout } = useContext(AuthContext);
  const [profile, setProfile] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    API.get("/auth/me")
        .then((res) => setProfile(res.data))
        .catch(() => {
            logout();
            nav("/login");
        });
  }, [logout, nav]);

  if (!profile) {
    return <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
              <p className="text-center text-gray-300 mt-8">Loading profile…</p>
            </div>
  }

  return (
    <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
      <div className="max-w-md mx-auto p-6">
        <h2 className="text-2xl text-gray-300 mb-4">Your Profile</h2>
        <p className="text-gray-300 mb-4">Email: <span className="font-medium">{profile.email}</span></p>
        <button
          onClick={logout}
          className="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700"
        >
          Log Out
        </button>
      </div>
    </div>
  );
}