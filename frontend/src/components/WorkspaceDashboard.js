import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Card, CardContent, CardActions, Typography, Box,
  IconButton, Menu, MenuItem, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, Button
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import AddIcon from '@mui/icons-material/Add';

// Common emojis for workspace
const COMMON_EMOJIS = ['🎓', '📧', '💼', '🏫', '🌍', '📚', '👨‍🎓', '🎯', '📝', '💡', '🚀', '⭐', '🏆', '📊', '🔔', '📅'];

export default function WorkspaceDashboard({ onSelectWorkspace }) {
  const [workspaces, setWorkspaces] = useState([]);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  
  // Form state
  const [formTitle, setFormTitle] = useState('');
  const [formEmoji, setFormEmoji] = useState('📧');
  const [formColor, setFormColor] = useState('#1976d2');

  useEffect(() => {
    loadWorkspaces();
  }, []);

  const loadWorkspaces = async () => {
    try {
      const res = await fetch('/api/workspaces');
      const data = await res.json();
      if (data.successo) {
        setWorkspaces(data.workspaces);
      }
    } catch (err) {
      console.error('Errore caricamento workspaces:', err);
    }
  };

  const handleMenuOpen = (event, workspace) => {
    event.stopPropagation();
    event.preventDefault(); // Add this
    console.log('Event target:', event.currentTarget);
    console.log('Event target rect:', event.currentTarget.getBoundingClientRect());
    setAnchorEl(event.currentTarget);
    setSelectedWorkspace(workspace);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleCreateOpen = () => {
    setFormTitle('');
    setFormEmoji('📧');
    setFormColor('#1976d2');
    setCreateDialogOpen(true);
  };

  const handleCreateClose = () => {
    setCreateDialogOpen(false);
  };

  const handleCreate = async () => {
    try {
      const res = await fetch('/api/workspaces', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titolo: formTitle,
          emoji: formEmoji,
          colore: formColor
        })
      });
      
      const data = await res.json();
      if (data.successo) {
        setCreateDialogOpen(false);
        loadWorkspaces();
      }
    } catch (err) {
      console.error('Errore creazione workspace:', err);
    }
  };

  const handleEditOpen = () => {
    setFormTitle(selectedWorkspace.title);
    setFormEmoji(selectedWorkspace.emoji);
    setFormColor(selectedWorkspace.color);
    setEditDialogOpen(true);
    handleMenuClose();
  };

  const handleEditSave = async () => {
    try {
      const res = await fetch(`/api/workspaces/${selectedWorkspace.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titolo: formTitle,
          emoji: formEmoji,
          colore: formColor
        })
      });
      
      const data = await res.json();
      if (data.successo) {
        setEditDialogOpen(false);
        loadWorkspaces();
      }
    } catch (err) {
      console.error('Errore aggiornamento workspace:', err);
    }
  };

  const handleDuplicate = async () => {
    try {
      const res = await fetch(`/api/workspaces/${selectedWorkspace.id}/duplicate`, {
        method: 'POST'
      });
      
      const data = await res.json();
      if (data.successo) {
        loadWorkspaces();
      }
    } catch (err) {
      console.error('Errore duplicazione workspace:', err);
    }
    handleMenuClose();
  };

  const handleDelete = async () => {
    if (!window.confirm(`Eliminare il workspace "${selectedWorkspace.title}"? Tutti i dati associati verranno eliminati.`)) {
      return;
    }
    
    try {
      const res = await fetch(`/api/workspaces/${selectedWorkspace.id}`, {
        method: 'DELETE'
      });
      
      const data = await res.json();
      if (data.successo) {
        loadWorkspaces();
      } else {
        alert(data.errore || 'Errore eliminazione workspace');
      }
    } catch (err) {
      console.error('Errore eliminazione workspace:', err);
    }
    handleMenuClose();
  };

  const handleEmojiSelect = (emoji) => {
    setFormEmoji(emoji);
  };

  const WorkspaceCard = ({ workspace }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'scale(1.02)',
          boxShadow: 6,
          backgroundColor: 'rgba(0, 0, 0, 0.02)'
        }
      }}
      onClick={() => onSelectWorkspace(workspace.id)}
    >
      <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: 3 }}>
        <Box sx={{ fontSize: '3.5rem', mb: 2 }}>
          {workspace.emoji}
        </Box>
        <Typography variant="h6" component="div" gutterBottom sx={{ fontWeight: 600 }}>
          {workspace.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {workspace.document_count} documenti • {workspace.email_count} email
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
          {new Date(workspace.last_modified).toLocaleDateString('it-IT')}
        </Typography>
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end', pt: 0 }}>
        <IconButton
          size="small"
          onClick={(e) => {
            e.stopPropagation(); // This stops the card click
            e.preventDefault();  // Add this too
            handleMenuOpen(e, workspace);
          }}
        >
          <MoreVertIcon />
        </IconButton>
      </CardActions>
    </Card>
  );

  const CreateCard = () => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        border: '2px dashed',
        borderColor: 'primary.main',
        backgroundColor: 'rgba(25, 118, 210, 0.04)',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          backgroundColor: 'rgba(25, 118, 210, 0.08)',
          transform: 'scale(1.02)'
        }
      }}
      onClick={handleCreateOpen}
    >
      <CardContent sx={{ textAlign: 'center' }}>
        <AddIcon sx={{ fontSize: '4rem', color: 'primary.main', mb: 1 }} />
        <Typography variant="h6" color="primary">
          Crea Nuovo Workspace
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4, fontWeight: 600 }}>
        I Miei Workspaces
      </Typography>

      <Grid container spacing={3}>
        {/* Create New Card */}
        <Grid item xs={12} sm={6} md={4} lg={3}>
          <CreateCard />
        </Grid>

        {/* Workspace Cards */}
        {workspaces.map((workspace) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={workspace.id}>
            <WorkspaceCard workspace={workspace} />
          </Grid>
        ))}
      </Grid>

      {/* Menu Actions */}
      <Menu
        id="workspace-menu"
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        slotProps={{
          paper: {
            sx: {
              mt: 1 // margin top for spacing
            }
          }
        }}
      >
        <MenuItem onClick={handleEditOpen}>Modifica</MenuItem>
        <MenuItem onClick={handleDuplicate}>Duplica</MenuItem>
        <MenuItem onClick={handleDelete} disabled={selectedWorkspace?.id === 1}>
          Elimina
        </MenuItem>
      </Menu>

      {/* Create Dialog */}
      <Dialog open={createDialogOpen} onClose={handleCreateClose} maxWidth="sm" fullWidth>
        <DialogTitle>Crea Nuovo Workspace</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Titolo"
              value={formTitle}
              onChange={(e) => setFormTitle(e.target.value)}
              fullWidth
              sx={{ mb: 3 }}
              inputProps={{ maxLength: 60 }}
            />

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>Emoji</Typography>
              <Typography variant="caption" display="block" gutterBottom color="text.secondary">
                Seleziona un emoji:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {COMMON_EMOJIS.map((emoji) => (
                  <Button
                    key={emoji}
                    variant={formEmoji === emoji ? 'contained' : 'outlined'}
                    onClick={() => handleEmojiSelect(emoji)}
                    sx={{ fontSize: '1.5rem', minWidth: 56, minHeight: 56 }}
                  >
                    {emoji}
                  </Button>
                ))}
              </Box>
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>Colore</Typography>
              <input
                type="color"
                value={formColor}
                onChange={(e) => setFormColor(e.target.value)}
                style={{ width: '100%', height: 50, cursor: 'pointer' }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCreateClose}>Annulla</Button>
          <Button onClick={handleCreate} variant="contained" disabled={!formTitle.trim()}>
            Crea
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Modifica Workspace</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              label="Titolo"
              value={formTitle}
              onChange={(e) => setFormTitle(e.target.value)}
              fullWidth
              sx={{ mb: 3 }}
              inputProps={{ maxLength: 60 }}
            />

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>Emoji</Typography>
              <Typography variant="caption" display="block" gutterBottom color="text.secondary">
                Seleziona un emoji:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {COMMON_EMOJIS.map((emoji) => (
                  <Button
                    key={emoji}
                    variant={formEmoji === emoji ? 'contained' : 'outlined'}
                    onClick={() => handleEmojiSelect(emoji)}
                    sx={{ fontSize: '1.5rem', minWidth: 56, minHeight: 56 }}
                  >
                    {emoji}
                  </Button>
                ))}
              </Box>
            </Box>

            <Box>
              <Typography variant="subtitle2" gutterBottom>Colore</Typography>
              <input
                type="color"
                value={formColor}
                onChange={(e) => setFormColor(e.target.value)}
                style={{ width: '100%', height: 50, cursor: 'pointer' }}
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Annulla</Button>
          <Button onClick={handleEditSave} variant="contained" disabled={!formTitle.trim()}>
            Salva
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
