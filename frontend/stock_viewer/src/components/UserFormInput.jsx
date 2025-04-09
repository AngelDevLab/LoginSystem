function UserFormInput ({ title, name, type, placeholder, inputValue, setInputValue, style, readonly = false }) {
    const inputStyle = readonly 
        ? { backgroundColor: "#BEBEBE", color: "#000", border: "1px solid #ccc", ...style } 
        : { ...style };

    return (
        <div className="input-group">
            <label htmlFor={name}>{title}</label>
            <input
                type={type}
                id={name}
                name={name}
                placeholder={placeholder}
                value={inputValue}
                autoComplete="on"
                onChange={(e) => setInputValue(e.target.value)}
                style={inputStyle}
                readOnly={readonly}
                required
            />
        </div>
    );
}

export default UserFormInput;