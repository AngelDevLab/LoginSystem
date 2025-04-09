import React, { useState, useEffect } from "react";
import axios from "axios";
import UserFormInput from "./UserFormInput";

function AuthenticatePage({ toggleLoginPage, authenticateEmail, setAuthenticatedEmail}) {
    const [email, setEmail] = useState("");
    const [authenticateCode, setAuthenticateCode] = useState("");
    const [timeLeft, setTimeLeft] = useState(60*3);
    const [message, setMessage] = useState("");
    const [messageFail, setMessageFail] = useState(false);

    const updateMessage = (message, isError) => {
        setMessage(message);
        setMessageFail(isError);
    };

    const handleAuthenticate = async (e) => {
        e.preventDefault();
        updateMessage("", false)
        try {
            const host = import.meta.env.VITE_APP_HOST;
            const url = host.includes("http:") ? `${host}/user/authenticate` : `https://${host}/user/authenticate`;
            const response = await axios.post(url, {
                email,
                authenticate_code: authenticateCode,
            });

            if (response.status === 200) {
                updateMessage("驗證成功", false)
                localStorage.setItem('access_token', response.data.access_token);

                setTimeout(() => {
                    setAuthenticatedEmail(email)
                    toggleLoginPage()
                }, 1200);
            }
        } catch (error) {
            if (error.response && error.response.status === 400) {
                updateMessage("驗證碼錯誤", true)
            } else {
                updateMessage("發生錯誤，請稍後再試", true)
            }
        }
    }

    useEffect(() => {
        if (authenticateEmail) {
            setEmail(authenticateEmail);
        }
    }, [authenticateEmail]);

    useEffect(() => {
        if (timeLeft > 0) {
            const timer = setInterval(() => {
                setTimeLeft((prevTime) => prevTime - 1);
            }, 1000);

            return () => clearInterval(timer);
        } else {
            toggleLoginPage();
        }
    }, [timeLeft, toggleLoginPage]);

    return (
        <div className="user-wrapper">
            <div className="form-container">
                <h2>信箱驗證</h2>

                <form className="register-form" onSubmit={handleAuthenticate}>
                    <UserFormInput 
                        title="電子郵件地址"
                        name="email"
                        type="email"
                        placeholder="輸入您的電子郵件"
                        inputValue={email}
                        setInputValue={setEmail}
                        style={{}}
                        readonly={true}/>

                    <UserFormInput 
                        title="驗證碼"
                        name="authenticate_code"
                        type="text"
                        placeholder="請輸入信箱驗證碼"
                        inputValue={authenticateCode}
                        setInputValue={setAuthenticateCode}
                        style={{}}/>

                    <button type="submit" className="register-button">
                        驗證
                    </button>
                </form>

                {message && (
                    <p className="message-text" style={{ color: messageFail ? "red" : "green" }}>
                        {message}
                    </p>
                )}

                <p className="message-text">剩餘時間：{timeLeft}秒</p>

            </div>
        </div>
    );
}

export default AuthenticatePage;
