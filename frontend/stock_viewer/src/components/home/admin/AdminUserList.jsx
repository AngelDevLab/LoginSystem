function AdminUserList({ userList }) {
    return (
        <div className="user-list-wrapper">
            <div className="user-list-header">
                <div className="header-item" style={{flex : 1}}>ID</div>
                <div className="header-item" style={{flex : 4}}>Email</div>
                <div className="header-item" style={{flex : 2}}>認證</div>
                <div className="header-item" style={{flex : 2}}>等級</div>
                <div className="header-item" style={{flex : 2}}>API Usage</div>
                <div className="header-item" style={{flex : 4}}>建立時間</div>
                <div className="header-item" style={{flex : 4}}>更新時間</div>
            </div>
            <div className="user-list-body">
                {userList.map((user, index) => (
                    <div className="user-row" key={index}>
                        <div className="user-item" style={{flex : 1}}>{user.id}</div>
                        <div className="user-item" style={{flex : 4}}>{user.email}</div>
                        <div className="user-item" style={{flex : 2}}>{user.authenticate_status ? "Yes" : "No"}</div>
                        <div className="user-item" style={{flex : 2}}>{user.level}</div>
                        <div className="user-item" style={{flex : 2}}>{user.today_api_use}</div>
                        <div className="user-item" style={{flex : 4}}>{user.created_at}</div>
                        <div className="user-item" style={{flex : 4}}>{user.updated_at}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default AdminUserList;
