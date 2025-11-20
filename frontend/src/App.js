import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Container,
  Button,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Menu as MenuIcon,
  Email as EmailIcon,
  Drafts as DraftsIcon,
  History as HistoryIcon,
  Description as DescriptionIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Home as HomeIcon,
  AccountCircle as AccountCircleIcon,
  AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import axios from 'axios';

import WorkspaceDashboard from './components/WorkspaceDashboard';
import Dashboard from './components/Dashboard';
import EmailList from './components/EmailList';
import EmailDetail from './components/EmailDetail';
import HistoricalEmails from './components/HistoricalEmails';
import EnrollmentDocs from './components/EnrollmentDocs';
import Settings from './components/Settings';
import Login from './components/Login';
import ChangePasswordDialog from './components/ChangePasswordDialog';
import AdminPanel from './components/AdminPanel';

const drawerWidth = 240;

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [workspaceInfo, setWorkspaceInfo] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [changePasswordOpen, setChangePasswordOpen] = useState(false);
  const [mustChangePassword, setMustChangePassword] = useState(false);
  const [accountMenuAnchor, setAccountMenuAnchor] = useState(null);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      setCurrentUser(response.data);
    } catch (err) {
      // Not logged in
      setCurrentUser(null);
    } finally {
      setAuthChecked(true);
    }
  };

  const handleLoginSuccess = (user, mustChange) => {
    setCurrentUser(user);
    setMustChangePassword(mustChange);
    if (mustChange) {
      setChangePasswordOpen(true);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/auth/logout');
      setCurrentUser(null);
      setCurrentWorkspace(null);
      setAccountMenuAnchor(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const handlePasswordChanged = () => {
    setChangePasswordOpen(false);
    setMustChangePassword(false);
  };

  useEffect(() => {
    if (currentWorkspace) {
      loadWorkspaceInfo();
    }
  }, [currentWorkspace]);

  const loadWorkspaceInfo = async () => {
    try {
      const res = await fetch(`/api/workspaces/${currentWorkspace}`);
      const data = await res.json();
      setWorkspaceInfo(data);
    } catch (err) {
      console.error('Errore caricamento workspace:', err);
    }
  };

  const handleSelectWorkspace = (workspaceId) => {
    setCurrentWorkspace(workspaceId);
  };

  const handleBackToWorkspaces = () => {
    setCurrentWorkspace(null);
    setWorkspaceInfo(null);
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Email', icon: <EmailIcon />, path: '/emails' },
    { text: 'Email Storiche', icon: <HistoryIcon />, path: '/historical-emails' },
    { text: 'Documenti di Contesto', icon: <DescriptionIcon />, path: '/enrollment-docs' },
    { text: 'Impostazioni', icon: <SettingsIcon />, path: '/settings' }
  ];

  // Add admin panel for admins
  if (currentUser?.is_admin) {
    menuItems.push({ text: 'Admin Panel', icon: <AdminIcon />, path: '/admin' });
  }

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Email RAG System
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component={Link} to={item.path}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </div>
  );

  // Show login if not authenticated
  if (!authChecked) {
    return <div>Loading...</div>;
  }

  if (!currentUser) {
    return (
      <>
        <CssBaseline />
        <Login onLoginSuccess={handleLoginSuccess} />
      </>
    );
  }

  // Show workspace dashboard if no workspace selected
  if (!currentWorkspace) {
    return (
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          <AppBar position="fixed">
            <Toolbar>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                ITS MAKER ACADEMY - Sistema Risposta Email
              </Typography>
              
              {/* Account Menu */}
              <IconButton
                color="inherit"
                onClick={(e) => setAccountMenuAnchor(e.currentTarget)}
              >
                <AccountCircleIcon />
              </IconButton>
              <Menu
                anchorEl={accountMenuAnchor}
                open={Boolean(accountMenuAnchor)}
                onClose={() => setAccountMenuAnchor(null)}
              >
                <MenuItem disabled>
                  <Typography variant="body2">{currentUser.username}</Typography>
                </MenuItem>
                <MenuItem onClick={() => { setChangePasswordOpen(true); setAccountMenuAnchor(null); }}>
                  Change Password
                </MenuItem>
                <MenuItem onClick={handleLogout}>Logout</MenuItem>
              </Menu>
            </Toolbar>
          </AppBar>
          <Box component="main" sx={{ flexGrow: 1, p: 3, width: '100%' }}>
            <Toolbar />
            <Routes>
              <Route path="/" element={<WorkspaceDashboard onSelectWorkspace={handleSelectWorkspace} />} />
              <Route path="/admin" element={currentUser.is_admin ? <AdminPanel /> : <div>Access Denied</div>} />
            </Routes>
          </Box>
        </Box>
        <ChangePasswordDialog 
          open={changePasswordOpen}
          onClose={handlePasswordChanged}
          mustChange={mustChangePassword}
        />
      </Router>
    );
  }

  // Show main app with workspace sidebar
  return (
    <Router>
      <Box sx={{ display: 'flex' }}>
        <CssBaseline />
        <AppBar
          position="fixed"
          sx={{
            width: { sm: `calc(100% - ${drawerWidth}px)` },
            ml: { sm: `${drawerWidth}px` },
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="apri menu"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            
            {workspaceInfo && (
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                <Typography sx={{ fontSize: '1.5rem', mr: 1 }}>
                  {workspaceInfo.emoji}
                </Typography>
                <Typography variant="h6" component="div">
                  {workspaceInfo.title}
                </Typography>
              </Box>
            )}
            
            <Box sx={{ flexGrow: 1 }} />
            
            <Button
              color="inherit"
              startIcon={<HomeIcon />}
              onClick={handleBackToWorkspaces}
              sx={{ mr: 2 }}
            >
              Tutti i Workspaces
            </Button>
            
            {/* Account Menu */}
            <IconButton
              color="inherit"
              onClick={(e) => setAccountMenuAnchor(e.currentTarget)}
            >
              <AccountCircleIcon />
            </IconButton>
            <Menu
              anchorEl={accountMenuAnchor}
              open={Boolean(accountMenuAnchor)}
              onClose={() => setAccountMenuAnchor(null)}
            >
              <MenuItem disabled>
                <Typography variant="body2">{currentUser.username}</Typography>
              </MenuItem>
              <MenuItem onClick={() => { setChangePasswordOpen(true); setAccountMenuAnchor(null); }}>
                Change Password
              </MenuItem>
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </Toolbar>
        </AppBar>
        <Box
          component="nav"
          sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        >
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
        <Box
          component="main"
          sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
        >
          <Toolbar />
          <Container maxWidth="xl">
            <Routes>
              <Route path="/" element={<Dashboard workspaceId={currentWorkspace} />} />
              <Route path="/emails" element={<EmailList workspaceId={currentWorkspace} />} />
              <Route path="/emails/:id" element={<EmailDetail workspaceId={currentWorkspace} />} />
              <Route path="/historical-emails" element={<HistoricalEmails workspaceId={currentWorkspace} />} />
              <Route path="/enrollment-docs" element={<EnrollmentDocs workspaceId={currentWorkspace} />} />
              <Route path="/settings" element={<Settings workspaceId={currentWorkspace} />} />
              <Route path="/admin" element={currentUser.is_admin ? <AdminPanel /> : <div>Access Denied</div>} />
            </Routes>
          </Container>
        </Box>
      </Box>
      <ChangePasswordDialog 
        open={changePasswordOpen}
        onClose={handlePasswordChanged}
        mustChange={mustChangePassword}
      />
    </Router>
  );
}

export default App;
