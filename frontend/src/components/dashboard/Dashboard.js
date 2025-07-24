import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom"; 
import { AuthContext } from "../../context/AuthContext";
import API from "../../api";
import HomePanel from './HomePanel';
import ProfilePanel from './ProfilePanel'; 
import SettingsPanel from './SettingsPanel'; 

export default function Dashboard() {
    const { logout } = useContext(AuthContext);
    const [profile, setProfile] = useState(null);
    const [activeTab, setActiveTab] = useState("home");
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

    return (
        <div className="min-h-screen flex flex-col font-mono bg-gradient-to-r from-teal-900 to-blue-900 px-8 pb-8">
            <div className="w-full h-24 rounded-bl-full rounded-br-full bg-white flex items-center justify-between px-16 mb-8">
                <h1 className="text-5xl text-teal-800">Dashboard</h1>
                <nav>
                    <ul className="flex space-x-4">
                        <li className={activeTab === "home" ? "font-bold text-teal-900" : "cursor-pointer"} onClick={() => setActiveTab("home")}>Home</li>
                        <li className={activeTab === "settings" ? "font-bold text-teal-900" : "cursor-pointer"} onClick={() => setActiveTab("settings")}>Settings</li>
                        <li className={activeTab === "profile" ? "font-bold text-teal-900" : "cursor-pointer"} onClick={() => setActiveTab("profile")}>Profile</li>
                        <li className="cursor-pointer" onClick={logout}>Logout</li>
                    </ul>
                </nav>
            </div>
            <div className="flex flex-1 w-full p-8">
                <div className="w-1/5 bg-white shadow-xl rounded-3xl mr-10 p-8 text-center divide-y divide-gray-300">
                    <h1 className="text-3xl text-teal-800 pb-4">Navigation</h1>
                    <nav>
                        <ul className="flex flex-col divide-y divide-gray-300">
                            <li className="py-6 cursor-pointer hover:text-teal-800" onClick={() => nav("/placement-test")}>Placement Test</li>
                            <li className="py-6 cursor-pointer hover:text-teal-800">Something here</li>
                            <li className="py-6 cursor-pointer hover:text-teal-800">Something here</li>
                            <li className="py-6 cursor-pointer hover:text-teal-800">Something here</li>
                            <li className="py-6 cursor-pointer hover:text-teal-800">Something here</li>
                        </ul>
                    </nav>
                </div>
                <div className="w-4/5 bg-white shadow-xl rounded-3xl p-8">
                    {activeTab === 'home' && <HomePanel />}
                    {activeTab === 'settings' && <SettingsPanel />}
                    {activeTab === 'profile' && <ProfilePanel />}
                </div>
            </div>
        </div>
    );
}