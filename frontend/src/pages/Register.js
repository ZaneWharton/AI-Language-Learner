import React, { useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
    const { register } = useContext(AuthContext);
    const nav = useNavigate();
    const [email, setEmail] = useState("");
    const [pw, setPw] = useState("");
    const [msg, setMsg] = useState("");

    const onSubmit = async (e) => {
        e.preventDefault();
        try{
            await register(email, pw);
            setMsg("Registered! Redirecting to Login...")
            setTimeout(() => nav("/login"), 1000);
        } catch (err) {
            setMsg(err.response?.data?.detail || "Registration failed.")
        }
      };

    return (
      <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
        <div className="md:w-2/3 p-8 flex flex-col justify-center items-center">
          <h1 className="text-4xl w-3/5 text-gray-300 text-center mb-4 ">
            Start Speaking Confidently Today!
          </h1>
          <p className="text-lg w-3/5 text-gray-300 text-center">
            --Access to AI-powered lessons tailored just for you--
          </p>
          <p className="text-lg w-3/5 text-gray-300 text-center">
            --Engage in real-time conversations with our AI tutor--
          </p>
          <p className="text-lg w-3/5 text-gray-300 text-center">
            --Monitor your journey with smart analytics--
          </p>
          <p className="text-lg w-3/5 text-gray-300 text-center">
            --Learn at your own pace--
          </p>
        </div>

      <div className="md:w-1/3 md:h-screen flex flex-col justify-center items-center">
        <div className="h-5/6 w-full flex flex-col items-center justify-center bg-white rounded-bl-full rounded-tl-full">
          <h2 className="text-5xl text-teal-800 mb-8">Register</h2>
          <form onSubmit={onSubmit} className="space-y-4">

            <input
              type="email"
              placeholder="Email"
              className="w-full p-3 border rounded-full"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <input
              type="password"
              placeholder="Password"
              className="w-full p-3 border rounded-full"
              value={pw}
              onChange={(e) => setPw(e.target.value)}
              required
            />

            <button
              type="submit"
              className="w-full bg-green-600 text-white py-4 rounded-full hover:bg-green-700"
            >
              Register
            </button>

          </form>

          <p className="mb-4">Already Have an Account? 
            <Link to="/login" className="text-blue-600 hover:underline"> Back to Login!</Link>
          </p>

          {msg && <p className="mt-4 text-center text-sm text-red-600">{msg}</p>}
        </div>
      </div>
    </div>
  );
}