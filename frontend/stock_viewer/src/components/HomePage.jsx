import React, { useState, useEffect } from "react";
import MenuItem from './home/MenuItem';
import { handleLogout, handleUserData, handleUserList } from "./hooks/handlerUser";
import ContentUser from "./home/ContentUser";
import CounterAdmin from "./home/CountentAdmin";

function HomePage() {
    const [user, setUser] = useState({
        email: null,
        level: null,
        status: null,
        today_api_use: null,
        created_at: null,
        updated_at: null
    });

    const [userList, setUserList] = useState([]);  // 定義 user_list 狀態

    useEffect(() => {
        const fetchUserData = async () => {
            const { result, data, message } = await handleUserData();
            
            if (result) {
                setUser(data);

                if (data.level == -1) {
                    fetchUserList();
                }
            } 
            else {
                alert(message);
                window.location.reload();
            }
        };

        const fetchUserList = async () => {
            const { result, data, message } = await handleUserList();
            if (result) {
                setUserList(data);
            }
        };

        fetchUserData();
    }, []);

    const logout = async () => {
        const { result, message } = await handleLogout();
        alert(message);
        window.location.reload();
    };

    const [currentPage, setCurrentPage] = useState("user");
    const renderPage = () => {
        switch (currentPage) {
            case "user":
                return <ContentUser user={user}/>
            case "stock-filter":
                return <div>菜單2內容</div>;
            case "admin":
                return <CounterAdmin userList={userList}/>;
        }
    };

    return (
        <div className="container">
            <div className="top-menu-wrapper">
                <div className="menu-wrapper">
                    <MenuItem name="用戶" onClick={() => setCurrentPage("user")} />
                    <MenuItem name="股票篩選器" onClick={() => setCurrentPage("stock-filter")} />
                    {user.level == -1 && (<MenuItem name="開發人員選項" onClick={() => setCurrentPage("admin")} />)}
                </div>
                <MenuItem name="登出" onClick={logout} />
            </div>

            <div className="main-wrapper">
                {renderPage()}
            </div>
        </div>
    );
}

export default HomePage;
