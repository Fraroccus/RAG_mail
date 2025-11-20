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
  IconButton
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import axios from 'axios';

function EnrollmentDocs({ workspaceId }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentDocId, setCurrentDocId] = useState(null);
  const [formData, setFormData] = useState({
    titolo: '',
    contenuto: '',
    tipo_documento: 'general',
    paese: 'ALL',
    programma: 'ALL',
    lingua: 'it',
    priorita: 'medium'
  });

  useEffect(() => {
    if (workspaceId) {
      loadDocs();
    }
  }, [workspaceId]);

  const loadDocs = async () => {
    if (!workspaceId) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`/api/enrollment-docs?workspace_id=${workspaceId}`);
      setDocs(response.data.documenti);
      setError(null);
    } catch (err) {
      setError('Errore nel caricamento');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      if (editMode) {
        await axios.put(`/api/enrollment-docs/${currentDocId}`, formData);
      } else {
        await axios.post('/api/enrollment-docs', { ...formData, workspace_id: workspaceId });
      }
      setDialogOpen(false);
      resetForm();
      loadDocs();
      alert(editMode ? 'Documento aggiornato!' : 'Documento aggiunto e indicizzato!');
    } catch (err) {
      alert('Errore: ' + (err.response?.data?.errore || err.message));
    }
  };

  const handleEdit = (doc) => {
    setFormData({
      titolo: doc.title,
      contenuto: doc.content,
      tipo_documento: doc.document_type,
      paese: doc.country,
      programma: doc.program,
      lingua: doc.language,
      priorita: doc.priority
    });
    setCurrentDocId(doc.id);
    setEditMode(true);
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo documento?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/enrollment-docs/${id}`);
      loadDocs();
    } catch (err) {
      alert('Errore nell\'eliminazione: ' + err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      titolo: '',
      contenuto: '',
      tipo_documento: 'general',
      paese: 'ALL',
      programma: 'ALL',
      lingua: 'it',
      priorita: 'medium'
    });
    setEditMode(false);
    setCurrentDocId(null);
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
          Documenti di Contesto
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => {
            resetForm();
            setDialogOpen(true);
          }}
        >
          Aggiungi Documento
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        I documenti di iscrizione contengono informazioni ufficiali su procedure, requisiti, scadenze e FAQ.
        Vengono utilizzati per fornire risposte accurate agli studenti.
      </Alert>

      {docs.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            Nessun documento. Inizia ad aggiungere procedure di iscrizione e informazioni ufficiali!
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Titolo</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Paese</TableCell>
                <TableCell>Programma</TableCell>
                <TableCell>Lingua</TableCell>
                <TableCell>Priorità</TableCell>
                <TableCell>Ultimo Aggiornamento</TableCell>
                <TableCell>Indicizzato</TableCell>
                <TableCell>Azioni</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {docs.map((doc) => (
                <TableRow key={doc.id} hover>
                  <TableCell>{doc.title}</TableCell>
                  <TableCell>
                    <Chip label={doc.document_type} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>{doc.country}</TableCell>
                  <TableCell>{doc.program}</TableCell>
                  <TableCell>
                    <Chip label={doc.language?.toUpperCase()} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={doc.priority} 
                      size="small"
                      color={
                        doc.priority === 'high' ? 'error' :
                        doc.priority === 'medium' ? 'warning' : 'default'
                      }
                    />
                  </TableCell>
                  <TableCell>{formatDate(doc.last_updated)}</TableCell>
                  <TableCell>
                    {doc.indexed ? (
                      <Chip label="Sì" color="success" size="small" />
                    ) : (
                      <Chip label="No" color="warning" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleEdit(doc)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(doc.id)}
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
        <DialogTitle>{editMode ? 'Modifica Documento' : 'Aggiungi Documento'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Titolo *"
              value={formData.titolo}
              onChange={(e) => setFormData({ ...formData, titolo: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Contenuto *"
              value={formData.contenuto}
              onChange={(e) => setFormData({ ...formData, contenuto: e.target.value })}
              multiline
              rows={10}
              fullWidth
              required
              placeholder="Inserisci procedure, requisiti, informazioni..."
            />
            <Box display="flex" gap={2}>
              <TextField
                label="Tipo Documento"
                value={formData.tipo_documento}
                onChange={(e) => setFormData({ ...formData, tipo_documento: e.target.value })}
                select
                SelectProps={{ native: true }}
                sx={{ flex: 1 }}
              >
                <option value="general">Generale</option>
                <option value="procedure">Procedura</option>
                <option value="requirement">Requisito</option>
                <option value="faq">FAQ</option>
                <option value="deadline">Scadenza</option>
                <option value="visa">Visto</option>
                <option value="fees">Tasse/Costi</option>
              </TextField>
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
              </TextField>
            </Box>
            <Box display="flex" gap={2}>
              <TextField
                label="Paese"
                value={formData.paese}
                onChange={(e) => setFormData({ ...formData, paese: e.target.value })}
                placeholder="es: Italia, India, ALL"
                sx={{ flex: 1 }}
              />
              <TextField
                label="Programma"
                value={formData.programma}
                onChange={(e) => setFormData({ ...formData, programma: e.target.value })}
                placeholder="es: AI, Cybersecurity, ALL"
                sx={{ flex: 1 }}
              />
            </Box>
            <TextField
              label="Priorità"
              value={formData.priorita}
              onChange={(e) => setFormData({ ...formData, priorita: e.target.value })}
              select
              SelectProps={{ native: true }}
              fullWidth
            >
              <option value="low">Bassa</option>
              <option value="medium">Media</option>
              <option value="high">Alta</option>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDialogOpen(false);
            resetForm();
          }}>
            Annulla
          </Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.titolo || !formData.contenuto}
          >
            {editMode ? 'Aggiorna' : 'Aggiungi'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default EnrollmentDocs;
