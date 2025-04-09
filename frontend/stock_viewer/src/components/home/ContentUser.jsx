
function UserItem ({ name, item }) {
    return (
        <div className="user-item">
            <div className="name">{name} : <span className="item">{item}</span></div>
        </div>
    );
}

function ContentUser( {user} ) {
    return (
        <div className="content-user">
            <div className="user-info">
                <UserItem name="Email" item={user.email}/>
                <UserItem name="用戶等級" item={user.level == -1 ? "admin" : user.level}/>
                <UserItem name="API 使用次數" item={user.today_api_use}/>
            </div>
            <div className="user-other"></div>
        </div>
    );
}

export default ContentUser;
