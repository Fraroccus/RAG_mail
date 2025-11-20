import React, { useState, useEffect } from 'react';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
  Checkbox,
  Grid,
  MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  DeleteSweep as BulkDeleteIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import axios from 'axios';

function HistoricalEmails({ workspaceId }) {
  const [emails, setEmails] = useState([]);
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState([]);
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    minRating: '',
    language: ''
  });
  const [formData, setFormData] = useState({
    oggetto: '',
    domanda_studente: '',
    risposta: '',
    lingua: 'it',
    tags: '',
    paese: '',
    programma: '',
    data_invio: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    if (workspaceId) {
      loadEmails();
    }
  }, [workspaceId]);

  const loadEmails = async () => {
    if (!workspaceId) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`/api/historical-emails?workspace_id=${workspaceId}`);
      setEmails(response.data.email_storiche);
      setFilteredEmails(response.data.email_storiche);
      setError(null);
    } catch (err) {
      setError('Errore nel caricamento');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...emails];

    // Date filter
    if (filters.dateFrom) {
      filtered = filtered.filter(e => 
        new Date(e.date_sent) >= new Date(filters.dateFrom)
      );
    }
    if (filters.dateTo) {
      filtered = filtered.filter(e => 
        new Date(e.date_sent) <= new Date(filters.dateTo)
      );
    }

    // Language filter
    if (filters.language) {
      filtered = filtered.filter(e => e.language === filters.language);
    }

    // Note: Rating filter would require backend changes to store ratings
    // For now, we'll skip it or you can add a rating field to HistoricalEmail model

    setFilteredEmails(filtered);
  };

  const clearFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      minRating: '',
      language: ''
    });
    setFilteredEmails(emails);
  };

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedIds(filteredEmails.map(e => e.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      alert('Seleziona almeno una email da eliminare');
      return;
    }

    if (!window.confirm(`Sei sicuro di voler eliminare ${selectedIds.length} email?`)) {
      return;
    }

    try {
      await Promise.all(
        selectedIds.map(id => axios.delete(`/api/historical-emails/${id}`))
      );
      setSelectedIds([]);
      loadEmails();
      alert(`${selectedIds.length} email eliminate con successo`);
    } catch (err) {
      alert('Errore nell\'eliminazione: ' + err.message);
    }
  };

  const handleSubmit = async () => {
    try {
      await axios.post('/api/historical-emails', { ...formData, workspace_id: workspaceId });
      setDialogOpen(false);
      resetForm();
      loadEmails();
      alert('Email storica aggiunta e indicizzata!');
    } catch (err) {
      alert('Errore: ' + (err.response?.data?.errore || err.message));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Sei sicuro di voler eliminare questa email?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/historical-emails/${id}`);
      loadEmails();
    } catch (err) {
      alert('Errore nell\'eliminazione: ' + err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      oggetto: '',
      domanda_studente: '',
      risposta: '',
      lingua: 'it',
      tags: '',
      paese: '',
      programma: '',
      data_invio: new Date().toISOString().split('T')[0]
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('it-IT');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Box mb={3} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1">
          Email Storiche ({filteredEmails.length})
        </Typography>
        <Box display="flex" gap={1}>
          {selectedIds.length > 0 && (
            <Button
              variant="outlined"
              color="error"
              startIcon={<BulkDeleteIcon />}
              onClick={handleBulkDelete}
            >
              Elimina ({selectedIds.length})
            </Button>
          )}
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
          >
            Aggiungi Email Storica
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Box display="flex" alignItems="center" mb={2}>
          <FilterIcon sx={{ mr: 1 }} />
          <Typography variant="h6">Filtri</Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              label="Data Da"
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
              InputLabelProps={{ shrink: true }}
              fullWidth
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              label="Data A"
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
              InputLabelProps={{ shrink: true }}
              fullWidth
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              label="Lingua"
              select
              value={filters.language}
              onChange={(e) => setFilters({...filters, language: e.target.value})}
              fullWidth
              size="small"
            >
              <MenuItem value="">Tutte</MenuItem>
              <MenuItem value="it">Italiano</MenuItem>
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="fr">Français</MenuItem>
              <MenuItem value="ar">العربية</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box display="flex" gap={1}>
              <Button variant="contained" onClick={applyFilters} fullWidth>
                Applica
              </Button>
              <Button variant="outlined" onClick={clearFilters} fullWidth>
                Reset
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Alert severity="info" sx={{ mb: 3 }}>
        Le email storiche vengono utilizzate per apprendere il tuo stile di scrittura.
        Aggiungi esempi delle tue risposte precedenti agli studenti.
      </Alert>

      {filteredEmails.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            Nessuna email storica. Inizia ad aggiungerne per migliorare lo stile delle risposte!
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={selectedIds.length === filteredEmails.length && filteredEmails.length > 0}
                    indeterminate={selectedIds.length > 0 && selectedIds.length < filteredEmails.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell>Data</TableCell>
                <TableCell>Oggetto</TableCell>
                <TableCell>Lingua</TableCell>
                <TableCell>Paese</TableCell>
                <TableCell>Programma</TableCell>
                <TableCell>Tags</TableCell>
                <TableCell>Indicizzata</TableCell>
                <TableCell>Azioni</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredEmails.map((email) => (
                <TableRow key={email.id} hover>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedIds.includes(email.id)}
                      onChange={() => handleSelectOne(email.id)}
                    />
                  </TableCell>
                  <TableCell>{formatDate(email.date_sent)}</TableCell>
                  <TableCell>{email.subject || 'N/A'}</TableCell>
                  <TableCell>
                    <Chip label={email.language?.toUpperCase()} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{email.country || 'N/A'}</TableCell>
                  <TableCell>{email.program || 'N/A'}</TableCell>
                  <TableCell>
                    {email.tags && email.tags.length > 0 ? (
                      email.tags.map((tag, idx) => (
                        <Chip key={idx} label={tag} size="small" sx={{ mr: 0.5 }} />
                      ))
                    ) : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {email.indexed ? (
                      <Chip label="Sì" color="success" size="small" />
                    ) : (
                      <Chip label="No" color="warning" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(email.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Aggiungi Email Storica</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Oggetto (opzionale)"
              value={formData.oggetto}
              onChange={(e) => setFormData({ ...formData, oggetto: e.target.value })}
              fullWidth
            />
            <TextField
              label="Domanda Studente *"
              value={formData.domanda_studente}
              onChange={(e) => setFormData({ ...formData, domanda_studente: e.target.value })}
              multiline
              rows={4}
              fullWidth
              required
            />
            <TextField
              label="Tua Risposta *"
              value={formData.risposta}
              onChange={(e) => setFormData({ ...formData, risposta: e.target.value })}
              multiline
              rows={6}
              fullWidth
              required
            />
            <Box display="flex" gap={2}>
              <TextField
                label="Lingua"
                value={formData.lingua}
                onChange={(e) => setFormData({ ...formData, lingua: e.target.value })}
                select
                SelectProps={{ native: true }}
                sx={{ flex: 1 }}
              >
                <option value="it">Italiano</option>
                <option value="en">English</option>
                <option value="fr">Français</option>
                <option value="ar">العربية</option>
              </TextField>
              <TextField
                label="Paese"
                value={formData.paese}
                onChange={(e) => setFormData({ ...formData, paese: e.target.value })}
                sx={{ flex: 1 }}
              />
            </Box>
            <TextField
              label="Programma"
              value={formData.programma}
              onChange={(e) => setFormData({ ...formData, programma: e.target.value })}
              fullWidth
            />
            <TextField
              label="Tags (separati da virgola)"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="es: iscrizione, visto, scadenza"
              fullWidth
            />
            <TextField
              label="Data Invio"
              type="date"
              value={formData.data_invio}
              onChange={(e) => setFormData({ ...formData, data_invio: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Annulla</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={!formData.domanda_studente || !formData.risposta}
          >
            Aggiungi
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default HistoricalEmails;
