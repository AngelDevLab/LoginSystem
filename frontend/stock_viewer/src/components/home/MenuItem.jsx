import React from 'react';

function MenuItem( {name, onClick= () => {}} ) {

    return (
        <div className={`menu-item`} onClick={onClick}>
            {name}
        </div>
    );
};

export default MenuItem;
