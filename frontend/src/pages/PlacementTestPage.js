import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import API from "../api";

//Current list of supported languages
const languages = ['Spanish', 'French', 'Japanese'];

export default function PlacementTest() {
    const { logout } = useContext(AuthContext);
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [msg, setMsg] = useState("")
    const nav = useNavigate();

    const [testStage, setTestStage] = useState("selection")
    const [language, setLanguage] = useState("Spanish")
    const [competency, setCompetency] = useState(null)

    const [currentIndex, setCurrentIndex] = useState(0)
    const [questions, setQuestions] = useState([])
    const [answers, setAnswers] = useState([])

    //Get user from backend, if cannot get user, redirected to login
    useEffect(() => {
        API.get("/auth/me")
            .then((res) => setProfile(res.data))
            .catch(() => {
                logout();
                nav("/login");
            });
    }, [logout, nav]);

    //Get questions for test
    const getQuestions = async (e) => {
        e.preventDefault();
        setLoading(true);

        //Reset index and answers for new tests
        setCurrentIndex(0);
        setAnswers([]);
        
        //Tries to fetch test questions from the backend
        try {
            const resp = await API.get("/placement-test/test", {
                params: {language: language}
            });
            if (resp.data && resp.data.length > 0) {
                setQuestions(resp.data);
                setTestStage("testing");
            } else {
                setTestStage("error");
                setMsg("No questions found for selected language")
            }
        } catch (err) {
            setTestStage("error");
            setMsg(err.response?.data?.detail || "No questions found for selected language");
        } finally {
            setLoading(false);
        }
    };

    //Will append the user's choice to the answers array and tracks question index
    const submitChoice = (choice) => {
        setAnswers(prevAnswers => [...prevAnswers, choice]); 
        if (currentIndex + 1 < questions.length) {
            setCurrentIndex(prevIndex => prevIndex + 1);
        }
        else {
            setTestStage("finished");
        }
    };

    //Submits answers, calculates competency (Will save competency to user profile in db)
    const submitAnswers = () => {
        setLoading(true);

        //Tracks number of correct choices
        let numCorrect = 0;
        for (let i = 0; i < questions.length; i++) {
            if (answers[i] === questions[i].correct_choice) { numCorrect += 1; }
        }

        //Maps grades to competency
        let grade = ((numCorrect/questions.length) * 100);
        if (grade <= 70) {
            setCompetency("Beginner")
        } else if (grade <= 90) {
            setCompetency("Intermediate")
        } else {
            setCompetency("Advanced")
        }

        setLoading(false);
    };

    useEffect(() => {
        if (testStage === "finished") {
            submitAnswers();
        }
    }, [testStage]);

    useEffect(() => {
        const savePlacement = async () => {
            try {
                await API.post("/placement-test/result", {
                    language: language,
                    level: competency
                });
            } catch (err) {
                console.error("Failed to save placement result", err);
            }
        };

        if (testStage === "finished" && competency) {
            savePlacement();
        }
    }, [competency, testStage, language]);

    //Loading screen
    if (loading) { return (
            <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
              <p className="text-center text-gray-300 mt-8">Loading…</p>
            </div>
        );
    }

    //Error screen
    if (testStage === "error") { return (
            <div className="p-4 text-red-500 text-center min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
                <div className="bg-white p-10 rounded-full shadow-xl text-center w-2/5 space-y-6">
                    <h1 className="text-4xl text-red-800">Error</h1>
                    <p className="text-lg text-gray-700">{msg}</p>
                    <button onClick={() => setTestStage("selection")} className="w-3/5 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">Retry Selection</button>
                </div>
            </div>
        );
    }

    //Selection screen
    if (testStage === "selection") { 
        return (
            <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
                <div className="bg-white p-10 rounded-full shadow-xl text-center w-2/5 space-y-6">
                    <h1 className="text-4xl text-teal-800">Start Your Placement Test</h1>
                    <p className="text-lg text-gray-700">Please select the language you'd like to learn!</p>
                    <select
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                        className="w-4/5 border rounded-lg p-3 text-lg focus:ring-2 focus:ring-blue-500 cursor-pointer"
                        >
                            {languages.map(lang => (
                                <option key={lang} value={lang}>{lang}</option>
                            ))}
                    </select>
                    <button onClick={getQuestions} className="w-3/5 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">Begin Test</button>
                    <p className="hover:text-teal-800 cursor-pointer" onClick={() => nav("/dashboard")}>Back to dashboard</p>
                </div>
            </div>
        );
    }

    //Test screen
    if (testStage === "testing") {
        const question = questions[currentIndex]
        if (!question) {
            return (
                <div className="p-4 text-red-500 text-center min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
                    <div className="bg-white p-10 rounded-full shadow-xl text-center w-2/5 space-y-6">
                        <h1 className="text-4xl text-red-800">Error</h1>
                        <p className="text-lg text-gray-700">No question data found. Please restart the test.</p>
                        <button onClick={() => setTestStage("selection")} className="w-3/5 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">Back to Selection</button>
                    </div>
                </div>
            );
        }

        return (
            <div className="min-h-screen flex items-center justify-center font-mono p-8 bg-gradient-to-r from-teal-900 to-blue-900">
                <div className="flex flex-col w-2/3 space-y-6">
                    <h2 className="text-3xl text-center text-gray-300">Question {currentIndex + 1} of {questions.length}</h2>
                    <p className="text-lg text-center text-gray-300">{question.prompt}</p>
                </div>
                <div className="flex flex-col items-center justify-center w-1/3">
                    {question.choices.map( c => (
                        <button
                            key={c}
                            onClick={() => submitChoice(c)}
                            className="w-4/5 text-left text-gray-300 mb-2 p-2 border rounded hover:text-white hover:bg-blue-800 transition-colors duration-200 ease-in-out">
                                {c}
                        </button>
                    ))}
                    <button
                        onClick={() => submitChoice("I don't know")}
                        className="w-4/5 text-left text-gray-300 mb-2 p-2 border rounded hover:text-white hover:bg-blue-800 transition-colors duration-200 ease-in-out">
                            I don't know
                    </button>
                    <p className="text-gray-300 hover:text-white cursor-pointer" onClick={() => nav("/dashboard")}>Back to dashboard</p>
                </div>
            </div>
        );
    }

//Results screen
return (
    <div className="min-h-screen flex items-center justify-center font-mono bg-gradient-to-r from-teal-900 to-blue-900">
        <div className="bg-white p-10 rounded-full shadow-xl text-center w-2/5 space-y-6">
            <h1 className="text-4xl text-teal-800">Test Complete!</h1>
            <p className="text-3xl text-gray-700">Estimated Competency:</p>
            <p className="text-5xl font-extrabold text-blue-700">{competency}</p>
            <button onClick={() => nav('/dashboard')} className="w-3/5 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">Back to Dashboard</button>
        </div>
    </div>
    );
};