import React, { useState, useEffect } from "react";
import AdminUserList from "./admin/AdminUserList";
import AdminUpdate from "./admin/AdminUpdate";

function SubMenuItem({ name, onClick= () => {} }) {
    return (
        <div className="submenu-item" onClick={onClick}>
            {name}
        </div>
    );
}

function CounterAdmin( {userList} ) {
    const [currentPage, setCurrentPage] = useState("user-list");
    const renderPage = () => {
        switch (currentPage) {
            case "user-list":
                return <AdminUserList userList={userList}/>
            case "update":
                return <AdminUpdate/>
        }
    };

    return (
        <div className="content-admin">
            <div className="submenu">
                <SubMenuItem name="用戶列表" onClick={() => setCurrentPage("user-list")}/>
                <SubMenuItem name="手動更新" onClick={() => setCurrentPage("update")}/>
            </div>
            <div className="sub-content">
                {renderPage()}
            </div>
        </div>
    );
}

export default CounterAdmin;
