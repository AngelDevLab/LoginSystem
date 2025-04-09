import axios from "axios";

// 用戶登出邏輯
const handleLogout = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.reload();
        return { result: false, message: "無法找到有效的登入資訊" };
    }

    try {
        const host = import.meta.env.VITE_APP_HOST;
        const url = host.includes("http:") ? `${host}/user/logout` : `https://${host}/user/logout`;

        const response = await axios.post(url, null, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        if (response.data.message === "logout successfully") {
            localStorage.removeItem('access_token');
            return { result: true, message: "登出成功" };
        }
    } catch (error) {
        return { result: false, message: "登出時發生錯誤" };
    }
};

// 用戶數據請求邏輯
const handleUserData = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.reload();
        return { result: false, message: "無法找到有效的登入資訊" };
    }

    try {
        const host = import.meta.env.VITE_APP_HOST;
        const url = host.includes("http:") ? `${host}/user/me` : `https://${host}/user/me`;

        const response = await axios.post(url, null, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        return {
            result: true,
            data: {
                email: response.data.email,
                level: response.data.level,
                status: response.data.status,
                today_api_use: response.data.today_api_use,
                created_at: response.data.created_at,
                updated_at: response.data.updated_at,
            }
        };
    } catch (error) {
        if (error.response && (error.response.data.detail === "Could not validate credentials" || error.response.data.detail === "Token is blacklisted")) {
            localStorage.removeItem('access_token');
            return { result: false, message: "登入已過期，請重新登入" };
        } else {
            return { result: false, message: "發生錯誤，請稍後再試" };
        }
    }
};

// 用戶列表請求邏輯
const handleUserList = async () => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.reload();
        return { result: false, message: "無法找到有效的登入資訊" };
    }

    try {
        const host = import.meta.env.VITE_APP_HOST;
        const url = host.includes("http:") ? `${host}/user/list` : `https://${host}/user/list`;

        const response = await axios.post(url, null, {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        return {
            result: true,
            data: response.data
        };
    } catch (error) {
        return { result: false, message: "伺服器請求錯誤" };
    }
};

export { handleLogout, handleUserData, handleUserList };
