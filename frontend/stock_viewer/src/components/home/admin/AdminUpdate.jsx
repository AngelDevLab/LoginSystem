import { useState } from "react";
import axios from "axios";

function AdminUpdate() {
    const currentYear = new Date().getFullYear();
    const currentMonth = String(new Date().getMonth() + 1).padStart(2, '0'); // JavaScript月份是從0開始的，所以要加1
    const years = Array.from(new Array(currentYear - 2010 + 1), (val, index) => 2010 + index);
    const months = Array.from({ length: 12 }, (val, index) => String(index + 1).padStart(2, '0'));

    const [selectedYear, setSelectedYear] = useState(currentYear);
    const [selectedMonth, setSelectedMonth] = useState(currentMonth);

    const handlePostRequest = async (url, params) => {
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            window.location.reload();
            return { result: false, message: "無法找到有效的登入資訊" };
        }
    
        try {
            const host = import.meta.env.VITE_APP_HOST;
            const fullUrl = host.includes("http:") ? `${host}${url}` : `https://${host}${url}`;
    
            // 发送 JSON 格式的 POST 请求
            const response = await axios.post(fullUrl, params, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });
    
            return {
                result: true,
                data: response.data,
            };
        } catch (error) {
            return {
                result: false,
                message: error.response?.data?.message || "伺服器請求錯誤",
            };
        }
    };

    const handleUpdateStockData = async () => {
        const params = {
            year: parseInt(selectedYear, 10),  // 确保 year 是整数
            month: parseInt(selectedMonth, 10) // 确保 month 是整数
        };
    
        const response = await handlePostRequest("/admin/stock/data/update", params);
        if (response.result) {
            alert("更新成功！");
        } else {
            alert(response.message);
        }
    };

    return (
        <div className="content-update">
            <h2>股票資訊</h2>
            <button className="update-button" onClick={() => handlePostRequest("/admin/stock/info/update", "")}>更新</button>

            <h2>股票數據</h2>
            <div className="input-group">
                <button className="update-button" onClick={handleUpdateStockData}>更新</button>
                
                <select 
                    className="select-year" 
                    defaultValue={currentYear}
                    onChange={(e) => setSelectedYear(e.target.value)}>
                    {years.map((year) => (
                        <option key={year} value={year}>
                            {year}
                        </option>
                    ))}
                </select>
                <span>年</span>

                <select 
                    className="select-month" 
                    defaultValue={currentMonth}
                    onChange={(e) => setSelectedMonth(e.target.value)}>
                    {months.map((month) => (
                        <option key={month} value={month}>
                            {month}
                        </option>
                    ))}
                </select>
                <span>月</span>
            </div>
        </div>
    );
}

export default AdminUpdate;
