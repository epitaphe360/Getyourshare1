import React from 'react';
import { Box } from '@mui/material';
import Navigation from '../Navigation';

const PublicLayout = ({ children }) => {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navigation />
      <Box component="main" sx={{ flexGrow: 1 }}>
        {children}
      </Box>
    </Box>
  );
};

export default PublicLayout;
