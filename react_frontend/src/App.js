import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Box, Grid2, Paper, Drawer } from '@mui/material';
import MapComponent from './MapComponent';
import PriceFilter from './FilterComponents/Price';
import CountySelect from './FilterComponents/County';

function App() {
  const [priceRange, setPriceRange] = useState([0, 500000]);
  const [county, setCounty] = useState('');

  return (
    <Box
      sx={{
        flexGrow: 1,
        height: '100vh',
        background: 'linear-gradient(135deg, #2E3B55 0%, #1F2633 100%)', // Muted dark gradient background
        color: 'white', // Light text color for readability on dark background
        fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif', // Simple, professional font family
      }}
    >
      {/* Header */}
      <AppBar position="static" elevation={0} sx={{ background: 'rgba(0, 0, 0, 0.7)' }}> {/* Darker header */}
        <Toolbar>
          <Typography
            variant="h4"
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 'bold',
              fontSize: '28px', // Clear, large title
              textTransform: 'none', // Professional, lower-case typography
              color: '#f5f5f5', // Slightly off-white for softness
            }}
          >
            Foreclosure Sales - Ohio
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Layout */}
      <Grid2 container spacing={2} sx={{ padding: 2 }}>
        {/* Filter Section */}
        <Grid2 item xs={4}>
          <Drawer variant="permanent" anchor="right" sx={{ backgroundColor: 'rgba(34, 40, 49, 0.9)' }}> {/* Darkened Drawer */}
            <Box sx={{ width: 300, padding: 2, color: '#f5f5f5' }}>
              {/* Filter AppBar */}
              <AppBar position="static" color="transparent" elevation={0} sx={{ background: 'rgba(0,0,0,0.5)' }}>
                <Toolbar>
                  <Typography
                    variant="h6"
                    component="div"
                    sx={{
                      fontWeight: 'medium',
                      fontSize: '18px',
                      color: '#ffffff',
                    }}
                  >
                    Filters
                  </Typography>
                </Toolbar>
              </AppBar>

              {/* Filter Section with Cards */}
              <Box sx={{ mt: 2 }}>
                <Paper elevation={1} sx={{ padding: 2, marginBottom: 2, backgroundColor: 'rgba(255,255,255,0.1)', color: 'black' }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontSize: '16px',
                      fontWeight: 'normal',
                      color: 'black',
                    }}
                  >
                    Price Range
                  </Typography>
                  <PriceFilter priceRange={priceRange} setPriceRange={setPriceRange} />
                </Paper>

                <Paper elevation={1} sx={{ padding: 2, backgroundColor: 'rgba(255,255,255,0.1)', color: 'black' }}>
                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{
                      fontSize: '16px',
                      fontWeight: 'normal',
                      color: 'black',
                    }}
                  >
                    County
                  </Typography>
                  <CountySelect county={county} setCounty={setCounty} />
                </Paper>
              </Box>
            </Box>
          </Drawer>
        </Grid2>

        {/* Map Section */}
        <Grid2 item xs={8}>
          <Paper elevation={3} sx={{ height: '80vh', padding: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
            <Box sx={{ flexGrow: 1 }}>
              <MapComponent priceRange={priceRange} county={county} />
            </Box>
            <Typography
              variant="h5"
              component="div"
              sx={{
                padding: 2,
                fontSize: '14px',
                letterSpacing: '1px',
                textAlign: 'center',
                color: 'white', 
              }}
            >
              ________________________________________________________________________________________________________________________
            </Typography>
          </Paper>
        </Grid2>
      </Grid2>
    </Box>
  );
}

export default App;
