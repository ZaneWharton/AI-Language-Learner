import React, { createContext, useState, useEffect } from "react";
import API from "../api";
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);

    //On mount, load token
    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (token) {
            const { sub: id } = jwtDecode(token);
            setUser({ id, email: id })
        }
    }, []);

    const register = async (email, password) => {
        await API.post("/auth/register", { email, password });
    };

    const login = async (email, password) => {
        const { data } = await API.post("/auth/login", { email, password });
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("refresh_token", data.refresh_token);
        const { sub: id } = jwtDecode(data.access_token);
        setUser({ id, email });
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, register, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}