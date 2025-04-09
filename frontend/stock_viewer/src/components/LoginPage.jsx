import React, { useState, useEffect } from "react";
import axios from "axios";
import UserFormInput from "./UserFormInput";

function LoginPage({ toggleRegisterPage, authenticatedEmail }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [messageFail, setMessageFail] = useState(false);

    const updateMessage = (message, isError) => {
        setMessage(message);
        setMessageFail(isError);
    };

    useEffect(() => {
        if (authenticatedEmail) {
            setEmail(authenticatedEmail);
        }
    }, [authenticatedEmail]); // 當 authenticatedEmail 變化時觸發

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const host = import.meta.env.VITE_APP_HOST;
            const url = host.includes("http:") ? `${host}/user/login` : `https://${host}/user/login`;

            const response = await axios.post(url,
                new URLSearchParams({
                    username: email,
                    password,
                }),
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                }
            );

            if (response.status === 200) {
                updateMessage("登入成功", false)
                localStorage.setItem('access_token', response.data.access_token);

                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } catch (error) {
            if (error.response && error.response.status === 401) {
                updateMessage("電子郵件或密碼不正確", true)
            } else {
                updateMessage("發生錯誤，請稍後再試", true)
            }
        }
    };

    return (
        <div className="user-wrapper">
            <div className="form-container">
                <h2>登入</h2>

                <form className="login-form" onSubmit={handleLogin}>
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

                    <button type="submit" className="login-button">
                        登入
                    </button>
                </form>

                {message && (
                    <p className="message-text" style={{ color: messageFail ? "red" : "green" }}>
                        {message}
                    </p>
                )}

                <p className="signup-text">
                    還沒有帳號？{" "}
                    <span className="signup-link" onClick={toggleRegisterPage}>
                        建立帳號
                    </span>
                </p>
            </div>
        </div>
    );
}

export default LoginPage;
