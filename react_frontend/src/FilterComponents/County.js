import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Autocomplete from '@mui/material/Autocomplete';

function CountySelect({county, setCounty}) {
    return (
        <Autocomplete 
        disablePortal
        options={['cuyahoga', 'lake']}
        sx={{width : 250}}
        value={county}
        onChange={(event, newValue) => setCounty(newValue)}
        renderInput={(params) => <TextField {...params} label="County" />}
        />
    );
}

export default CountySelect;