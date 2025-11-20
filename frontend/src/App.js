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
  Button
} from '@mui/material';
import {
  Menu as MenuIcon,
  Email as EmailIcon,
  Drafts as DraftsIcon,
  History as HistoryIcon,
  Description as DescriptionIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Home as HomeIcon
} from '@mui/icons-material';

import WorkspaceDashboard from './components/WorkspaceDashboard';
import Dashboard from './components/Dashboard';
import EmailList from './components/EmailList';
import EmailDetail from './components/EmailDetail';
import HistoricalEmails from './components/HistoricalEmails';
import EnrollmentDocs from './components/EnrollmentDocs';
import Settings from './components/Settings';

const drawerWidth = 240;

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [workspaceInfo, setWorkspaceInfo] = useState(null);

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

  // Show workspace dashboard if no workspace selected
  if (!currentWorkspace) {
    return (
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          <AppBar position="fixed">
            <Toolbar>
              <Typography variant="h6" noWrap component="div">
                ITS MAKER ACADEMY - Sistema Risposta Email
              </Typography>
            </Toolbar>
          </AppBar>
          <Box component="main" sx={{ flexGrow: 1, p: 3, width: '100%' }}>
            <Toolbar />
            <WorkspaceDashboard onSelectWorkspace={handleSelectWorkspace} />
          </Box>
        </Box>
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
            >
              Tutti i Workspaces
            </Button>
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
            </Routes>
          </Container>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
