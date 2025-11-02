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
  IconButton,
  Badge
} from '@mui/material';
import {
  AccountCircle,
  ShoppingCart,
  Notifications,
  Menu as MenuIcon,
  Home,
  Store,
  Analytics,
  People,
  Settings,
  ExitToApp
} from '@mui/icons-material';

const Navigation = ({ user, onLogout }) => {
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
    { label: 'Fonctionnalités', icon: <Analytics />, path: '/features' },
    { label: 'À Propos', icon: <People />, path: '/about' },
    { label: 'Marketplace', icon: <Store />, path: '/marketplace' },
    { label: 'Tarifs', icon: <Settings />, path: '/pricing' },
    { label: 'Contact', icon: <Home />, path: '/contact' },
  ];

  return (
    <AppBar position="static" sx={{ background: 'linear-gradient(45deg, #2E7D32, #388E3C)', boxShadow: 3 }}>
      <Toolbar>
        {/* Logo - Plus grand */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 0 }}>
          <img 
            src="/logo.jpg" 
            alt="Logo" 
            style={{ height: 60, marginRight: 0, objectFit: 'contain' }}
            onError={(e) => {
              e.target.src = '/logo.png';
            }}
          />
        </Box>

        {/* Navigation Items - Desktop */}
        <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' }, ml: 4 }}>
          {navigationItems.map((item) => (
            <Button
              key={item.label}
              startIcon={item.icon}
              sx={{ 
                color: 'white', 
                mx: 1,
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  borderRadius: 2
                }
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Mobile Menu */}
        <Box sx={{ display: { xs: 'flex', md: 'none' }, flexGrow: 1, justifyContent: 'flex-end' }}>
          <IconButton
            size="large"
            aria-label="menu"
            onClick={handleMenuOpen}
            color="inherit"
          >
            <MenuIcon />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            {navigationItems.map((item) => (
              <MenuItem key={item.label} onClick={handleClose}>
                {item.icon}
                <Typography sx={{ ml: 2 }}>{item.label}</Typography>
              </MenuItem>
            ))}
          </Menu>
        </Box>

        {/* Right Side Icons */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Notifications */}
          <IconButton color="inherit">
            <Badge badgeContent={3} color="error">
              <Notifications />
            </Badge>
          </IconButton>

          {/* Shopping Cart */}
          <IconButton color="inherit">
            <Badge badgeContent={2} color="error">
              <ShoppingCart />
            </Badge>
          </IconButton>

          {/* User Menu */}
          {user ? (
            <>
              <IconButton
                size="large"
                onClick={handleUserMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  {user.username?.charAt(0).toUpperCase() || 'U'}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={userMenuAnchor}
                open={Boolean(userMenuAnchor)}
                onClose={handleClose}
                PaperProps={{
                  sx: { mt: 1, minWidth: 200 }
                }}
              >
                <MenuItem onClick={handleClose}>
                  <Avatar sx={{ width: 24, height: 24, mr: 2 }} />
                  <Box>
                    <Typography variant="subtitle2">{user.username}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {user.role} • {user.subscription_plan}
                    </Typography>
                  </Box>
                </MenuItem>
                <Divider />
                <MenuItem onClick={handleClose}>
                  <Settings sx={{ mr: 2 }} />
                  Paramètres
                </MenuItem>
                <MenuItem onClick={handleClose}>
                  <Analytics sx={{ mr: 2 }} />
                  Tableau de bord
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => { handleClose(); onLogout(); }}>
                  <ExitToApp sx={{ mr: 2 }} />
                  Déconnexion
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button color="inherit" variant="outlined" size="small">
                Connexion
              </Button>
              <Button color="secondary" variant="contained" size="small">
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