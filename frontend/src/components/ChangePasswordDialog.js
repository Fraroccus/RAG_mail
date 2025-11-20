import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Alert,
  Typography
} from '@mui/material';
import axios from 'axios';

function ChangePasswordDialog({ open, onClose, mustChange }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (newPassword.length < 4) {
      setError('Password must be at least 4 characters');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword
      });

      if (response.data.successo) {
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
        onClose(true); // true = password changed
      }
    } catch (err) {
      setError(err.response?.data?.errore || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={mustChange ? null : onClose}
      maxWidth="sm"
      fullWidth
    >
      <form onSubmit={handleSubmit}>
        <DialogTitle>
          {mustChange ? 'Change Password Required' : 'Change Password'}
        </DialogTitle>

        <DialogContent>
          {mustChange && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              You must change your temporary password before continuing.
            </Alert>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TextField
            fullWidth
            label="Current Password"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            margin="normal"
            required
            autoFocus
            disabled={loading}
          />

          <TextField
            fullWidth
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            margin="normal"
            required
            disabled={loading}
            helperText="At least 4 characters"
          />

          <TextField
            fullWidth
            label="Confirm New Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            margin="normal"
            required
            disabled={loading}
          />
        </DialogContent>

        <DialogActions>
          {!mustChange && (
            <Button onClick={onClose} disabled={loading}>
              Cancel
            </Button>
          )}
          <Button 
            type="submit" 
            variant="contained"
            disabled={loading}
          >
            Change Password
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}

export default ChangePasswordDialog;
