import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Checkbox,
  FormControlLabel,
  Alert,
  Chip,
  Box,
  Tooltip
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  Delete as DeleteIcon,
  VpnKey as VpnKeyIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import axios from 'axios';

function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [resetPasswordDialog, setResetPasswordDialog] = useState(null);
  
  // New user form
  const [newUser, setNewUser] = useState({
    email: '',
    full_name: '',
    temp_password: '',
    is_admin: false
  });
  const [newUserError, setNewUserError] = useState('');
  const [resetPassword, setResetPassword] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/admin/users');
      setUsers(response.data.users);
      setError('');
    } catch (err) {
      setError(err.response?.data?.errore || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async () => {
    setNewUserError('');

    if (!newUser.email || !newUser.temp_password) {
      setNewUserError('Email and temporary password are required');
      return;
    }

    if (newUser.temp_password.length < 8) {
      setNewUserError('Password must be at least 8 characters');
      return;
    }

    try {
      await axios.post('/api/admin/users', newUser);
      setCreateDialogOpen(false);
      setNewUser({ email: '', full_name: '', temp_password: '', is_admin: false });
      loadUsers();
    } catch (err) {
      setNewUserError(err.response?.data?.errore || 'Failed to create user');
    }
  };

  const handleToggleActive = async (userId, currentStatus) => {
    try {
      await axios.patch(`/api/admin/users/${userId}`, {
        is_active: !currentStatus
      });
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.errore || 'Failed to update user');
    }
  };

  const handleResetPassword = async (userId) => {
    if (!resetPassword || resetPassword.length < 8) {
      return;
    }

    try {
      await axios.post(`/api/admin/users/${userId}/reset-password`, {
        new_password: resetPassword
      });
      setResetPasswordDialog(null);
      setResetPassword('');
      alert('Password reset successfully');
    } catch (err) {
      alert(err.response?.data?.errore || 'Failed to reset password');
    }
  };

  const handleDeleteUser = async (userId, userEmail) => {
    if (!window.confirm(`Are you sure you want to delete user ${userEmail}?`)) {
      return;
    }

    try {
      await axios.delete(`/api/admin/users/${userId}`);
      loadUsers();
    } catch (err) {
      setError(err.response?.data?.errore || 'Failed to delete user');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            User Management
          </Typography>
          <Button
            variant="contained"
            startIcon={<PersonAddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create User
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Email</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Workspaces</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.full_name || '-'}</TableCell>
                  <TableCell>
                    {user.is_active ? (
                      <Chip label="Active" color="success" size="small" />
                    ) : (
                      <Chip label="Inactive" color="default" size="small" />
                    )}
                    {user.must_change_password && (
                      <Chip label="Must change password" color="warning" size="small" sx={{ ml: 1 }} />
                    )}
                  </TableCell>
                  <TableCell>
                    {user.is_admin ? (
                      <Chip label="Admin" color="primary" size="small" />
                    ) : (
                      <Chip label="User" color="default" size="small" />
                    )}
                  </TableCell>
                  <TableCell>{user.workspace_count}</TableCell>
                  <TableCell>
                    {new Date(user.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title={user.is_active ? "Deactivate" : "Activate"}>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleActive(user.id, user.is_active)}
                        color={user.is_active ? "default" : "success"}
                      >
                        {user.is_active ? <BlockIcon /> : <CheckCircleIcon />}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Reset Password">
                      <IconButton
                        size="small"
                        onClick={() => setResetPasswordDialog(user)}
                      >
                        <VpnKeyIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete User">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteUser(user.id, user.email)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create User Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New User</DialogTitle>
        <DialogContent>
          {newUserError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {newUserError}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Email"
            type="email"
            value={newUser.email}
            onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            margin="normal"
            required
          />

          <TextField
            fullWidth
            label="Full Name"
            value={newUser.full_name}
            onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
            margin="normal"
          />

          <TextField
            fullWidth
            label="Temporary Password"
            type="password"
            value={newUser.temp_password}
            onChange={(e) => setNewUser({ ...newUser, temp_password: e.target.value })}
            margin="normal"
            required
            helperText="User will be required to change this on first login"
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={newUser.is_admin}
                onChange={(e) => setNewUser({ ...newUser, is_admin: e.target.checked })}
              />
            }
            label="Admin privileges"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateUser} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Reset Password Dialog */}
      <Dialog 
        open={!!resetPasswordDialog} 
        onClose={() => setResetPasswordDialog(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reset Password for {resetPasswordDialog?.email}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="New Password"
            type="password"
            value={resetPassword}
            onChange={(e) => setResetPassword(e.target.value)}
            margin="normal"
            helperText="At least 8 characters"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetPasswordDialog(null)}>Cancel</Button>
          <Button 
            onClick={() => handleResetPassword(resetPasswordDialog.id)} 
            variant="contained"
            disabled={resetPassword.length < 8}
          >
            Reset Password
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default AdminPanel;
