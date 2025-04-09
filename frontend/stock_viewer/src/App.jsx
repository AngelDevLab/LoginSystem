import './App.css'
import React, { useState, useEffect } from "react";
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import HomePage from './components/HomePage';
import AuthenticatePage from './components/AuthenticatePage';

const PAGES = Object.freeze({
    LOGIN: "LOGIN",
    REGISTER: "REGISTER",
    HOME: "HOME",
    AUTHENTICATE: "AUTHENTICATE"
});

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const [pageStatus, setPageStatus] = useState(PAGES.LOGIN);
    const [authenticateEmail, setAuthenticateEmail] = useState("");
    const [authenticatedEmail, setAuthenticatedEmail] = useState("");

    const renderPage = () => {
        switch (pageStatus) {
            case PAGES.LOGIN:
                return <LoginPage 
                            toggleRegisterPage={() => setPageStatus(PAGES.REGISTER)} 
                            authenticatedEmail={authenticatedEmail}/>;
            case PAGES.REGISTER:
                return <RegisterPage 
                            toggleLoginPage={() => setPageStatus(PAGES.LOGIN)} 
                            toggleAuthenticatePage={() => setPageStatus(PAGES.AUTHENTICATE)} 
                            setAuthenticateEmail={setAuthenticateEmail}/>;
            case PAGES.AUTHENTICATE:
                return <AuthenticatePage 
                            toggleLoginPage={() => setPageStatus(PAGES.LOGIN)}
                            authenticateEmail={authenticateEmail}
                            setAuthenticatedEmail={setAuthenticatedEmail}/>;
            default:
                return <LoginPage 
                            toggleRegisterPage={() => setPageStatus(PAGES.REGISTER)} 
                            authenticatedEmail={authenticatedEmail}/>;
        }
    };


    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            setIsAuthenticated(true);
        }
    }, []);

    return (
        <>
            {isAuthenticated ? (<HomePage />) : renderPage()}
        </>
    );
}

export default App
