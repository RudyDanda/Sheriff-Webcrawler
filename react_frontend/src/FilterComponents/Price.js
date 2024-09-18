import React, { useState } from 'react';
import { Box, Typography } from '@mui/material';
import Slider from '@mui/material/Slider';

function PriceFilter({priceRange, setPriceRange}) {
  // // Define state to hold the price range
  // const [priceRange, setPriceRange] = useState([0, 1000000]); // Example price range (min, max)

  // Handle the slider value change
  const handlePriceChange = (event, newValue) => {
    setPriceRange(newValue);
  };

  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h6" gutterBottom>
        Opening Bid
      </Typography>
      <Slider
        getAriaLabel={() => 'Price range'}
        value={priceRange}
        onChange={handlePriceChange}
        valueLabelDisplay="auto"
        min={0}
        max={500000}
        disableSwap
      />
      <Typography>
        ${priceRange[0]} - ${priceRange[1]}
      </Typography>
    </Box>
  );
}

export default PriceFilter;