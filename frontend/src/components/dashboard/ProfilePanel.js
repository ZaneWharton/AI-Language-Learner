import React, { useContext, useState, useEffect } from 'react';
import API from "../../api";
import { AuthContext } from '../../context/AuthContext';
import { useNavigate } from "react-router-dom";

export default function ProfilePanel() {
    const { logout } = useContext(AuthContext);
    const [profile, setProfile] = useState(null);
    const nav = useNavigate();

    //Get user from backend, if cannot get user, redirected to login
    useEffect(() => {
        API.get("/auth/me")
            .then((res) => setProfile(res.data))
            .catch(() => {
                logout();
                nav("/login");
            });
    }, [logout, nav]);

    if (!profile) {
        return (
            <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
              <p className="text-center text-gray-300 mt-8">Loading…</p>
            </div>
        );
    }

    return (
        <div>
            <h2 className="text-2xl text-teal-800 mb-2">Your Profile</h2>
            <p>Email: {profile.email}</p>
        </div>
    );
}