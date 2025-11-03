import React, { useState } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Menu, 
  MenuItem, 
  Box,
  Avatar,
  Divider,
  IconButton
} from '@mui/material';
import {
  Menu as MenuIcon,
  Home,
  Store,
  Analytics,
  People,
  Settings,
  ExitToApp
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const Navigation = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setUserMenuAnchor(null);
  };

  const navigationItems = [
    { label: 'Accueil', icon: <Home />, path: '/' },
    { label: 'À Propos', icon: <People />, path: '/about' },
    { label: 'Marketplace', icon: <Store />, path: '/marketplace' },
    { label: 'Tarifs', icon: <Settings />, path: '/pricing' },
    { label: 'Contact', icon: <Analytics />, path: '/contact' },
  ];

  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{ 
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        py: 1
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between', maxWidth: '1400px', width: '100%', mx: 'auto', px: { xs: 2, sm: 3 } }}>
        {/* Logo */}
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer',
            transition: 'transform 0.2s',
            '&:hover': {
              transform: 'scale(1.05)'
            }
          }}
          onClick={() => navigate('/')}
        >
          <img 
            src="/logo.png" 
            alt="GetYourShare Logo" 
            style={{ height: 45, objectFit: 'contain' }}
          />
        </Box>

        {/* Navigation Items - Desktop */}
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
          {navigationItems.map((item) => (
            <Button
              key={item.label}
              onClick={() => navigate(item.path)}
              sx={{ 
                color: '#1a1a1a',
                fontWeight: 500,
                fontSize: '0.95rem',
                px: 2.5,
                py: 1,
                borderRadius: 2,
                textTransform: 'none',
                transition: 'all 0.2s',
                '&:hover': {
                  backgroundColor: '#f5f5f5',
                  color: '#667eea',
                  transform: 'translateY(-2px)'
                }
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Mobile Menu */}
        <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
          <IconButton
            size="large"
            onClick={handleMenuOpen}
            sx={{ color: '#1a1a1a' }}
          >
            <MenuIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            PaperProps={{
              sx: { 
                mt: 1.5,
                minWidth: 200,
                borderRadius: 2,
                boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
              }
            }}
          >
            {navigationItems.map((item) => (
              <MenuItem 
                key={item.label} 
                onClick={() => {
                  navigate(item.path);
                  handleClose();
                }}
                sx={{
                  py: 1.5,
                  px: 2.5,
                  '&:hover': {
                    backgroundColor: '#f5f5f5'
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, color: '#1a1a1a' }}>
                  {item.icon}
                  <Typography>{item.label}</Typography>
                </Box>
              </MenuItem>
            ))}
          </Menu>
        </Box>

        {/* Right Side - Auth Buttons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {user ? (
            <>
              <IconButton
                size="large"
                onClick={handleUserMenuOpen}
                sx={{ 
                  p: 0.5,
                  '&:hover': {
                    backgroundColor: 'rgba(102, 126, 234, 0.1)'
                  }
                }}
              >
                <Avatar 
                  sx={{ 
                    width: 38, 
                    height: 38, 
                    bgcolor: '#667eea',
                    fontWeight: 600
                  }}
                >
                  {user.username?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={handleClose}
                PaperProps={{
                  sx: { 
                    mt: 1.5, 
                    minWidth: 220,
                    borderRadius: 2,
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
                  }
                }}
              >
                <MenuItem onClick={handleClose} sx={{ py: 2, px: 2.5 }}>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#1a1a1a' }}>
                      {user.username}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#666' }}>
                      {user.role} • {user.subscription_plan}
                    </Typography>
                  </Box>
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { 
                  navigate('/settings'); 
                  handleClose(); 
                }} sx={{ py: 1.5, px: 2.5 }}>
                  <Settings sx={{ mr: 2, fontSize: 20, color: '#667eea' }} />
                  <Typography>Paramètres</Typography>
                </MenuItem>
                <MenuItem onClick={() => { 
                  navigate('/dashboard'); 
                  handleClose(); 
                }} sx={{ py: 1.5, px: 2.5 }}>
                  <Analytics sx={{ mr: 2, fontSize: 20, color: '#667eea' }} />
                  <Typography>Tableau de bord</Typography>
                </MenuItem>
                <Divider />
                <MenuItem 
                  onClick={() => { handleClose(); onLogout(); }}
                  sx={{ py: 1.5, px: 2.5, color: '#dc2626' }}
                >
                  <ExitToApp sx={{ mr: 2, fontSize: 20 }} />
                  <Typography>Déconnexion</Typography>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1.5 }}>
              <Button 
                variant="text"
                onClick={() => navigate('/login')}
                sx={{
                  color: '#1a1a1a',
                  fontWeight: 500,
                  textTransform: 'none',
                  px: 2.5,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: '#f5f5f5'
                  }
                }}
              >
                Connexion
              </Button>
              <Button 
                variant="contained"
                onClick={() => navigate('/register')}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  fontWeight: 600,
                  textTransform: 'none',
                  px: 3,
                  py: 1,
                  borderRadius: 2,
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                    boxShadow: '0 6px 16px rgba(102, 126, 234, 0.4)',
                    transform: 'translateY(-2px)'
                  },
                  transition: 'all 0.2s'
                }}
              >
                Inscription
              </Button>
            </Box>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;