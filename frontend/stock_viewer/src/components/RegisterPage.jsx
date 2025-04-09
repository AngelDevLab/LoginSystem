import React, { useState, useEffect  } from "react";
import axios from "axios";
import UserFormInput from "./UserFormInput";

function RegisterPage({ toggleLoginPage, toggleAuthenticatePage, setAuthenticateEmail }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [messageFail, setMessageFail] = useState(false);
    const [passwordMismatch, setPasswordMismatch] = useState(false);

    const updateMessage = (message, isError) => {
        setMessage(message);
        setMessageFail(isError);
    };

    const handleRegister = async (e) => {
        updateMessage("註冊中...", false);

        e.preventDefault();
        if (password !== confirmPassword) {
            updateMessage("密碼不相同", true);
            setPasswordMismatch(true);
            return;
        }
        
        setPasswordMismatch(false);

        try {
            const host = import.meta.env.VITE_APP_HOST;
            const url = host.includes("http:") ? `${host}/user/register` : `https://${host}/user/register`;
            const response = await axios.post(url, {
                email,
                password,
            });

            if (response.status === 200) {
                updateMessage("註冊成功", false);
                setTimeout(() => {
                    setAuthenticateEmail(email)
                    toggleAuthenticatePage();
                }, 1500);
            }
        } catch (error) {
            if (error.response && error.response.status === 400) {
                updateMessage("此電子郵件已經被註冊", true);
            } else {
                updateMessage("發生錯誤，請稍後再試", true);
            }
        }
    }

    return (
        <div className="user-wrapper">
            <div className="form-container">
                <h2>註冊</h2>

                <form className="register-form" onSubmit={handleRegister}>
                    <UserFormInput 
                        title="電子郵件地址"
                        name="email"
                        type="email"
                        placeholder="輸入您的電子郵件"
                        inputValue={email}
                        setInputValue={setEmail}
                        style={{}}/>

                    <UserFormInput 
                        title="密碼"
                        name="password"
                        type="password"
                        placeholder="輸入您的密碼"
                        inputValue={password}
                        setInputValue={setPassword}
                        style={{}}/>

                    <UserFormInput 
                        title="再次輸入密碼"
                        name="confirm-password"
                        type="password"
                        placeholder="輸入您的密碼"
                        inputValue={confirmPassword}
                        setInputValue={setConfirmPassword}
                        style={{ borderColor: passwordMismatch ? "red" : "#dadce0" }}/>

                    <button type="submit" className="register-button">
                        註冊
                    </button>
                </form>

                {message && (
                    <p className="message-text" style={{ color: messageFail ? "red" : "green" }}>
                        {message}
                    </p>
                )}

                <p className="signup-text">
                    已經有帳號了？{" "}
                    <span className="signup-link" onClick={toggleLoginPage}>
                    登入
                    </span>
                </p>

                
            </div>
        </div>
    );
}

export default RegisterPage;
