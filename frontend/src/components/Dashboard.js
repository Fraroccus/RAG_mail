import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Rating,
  Divider
} from '@mui/material';
import {
  Email as EmailIcon,
  Drafts as DraftsIcon,
  CheckCircle as CheckIcon,
  Send as SendIcon,
  ContentPaste as PasteIcon,
  Star as StarIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import axios from 'axios';

function Dashboard({ workspaceId }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fetching, setFetching] = useState(false);
  const [pasteDialogOpen, setPasteDialogOpen] = useState(false);
  const [manualEmail, setManualEmail] = useState({
    subject: '',
    body: '',
    sender: ''
  });
  const [generatedResponse, setGeneratedResponse] = useState('');
  const [generating, setGenerating] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [savingToHistory, setSavingToHistory] = useState(false);

  useEffect(() => {
    if (workspaceId) {
      loadStats();
    }
  }, [workspaceId]);

  const loadStats = async () => {
    if (!workspaceId) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`/api/stats?workspace_id=${workspaceId}`);
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Errore nel caricamento delle statistiche');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchEmails = async () => {
    try {
      setFetching(true);
      const response = await axios.post('/api/emails/fetch');
      alert(`${response.data.nuove_email} nuove email recuperate`);
      loadStats();
    } catch (err) {
      alert('Errore nel recupero email: ' + (err.response?.data?.errore || err.message));
    } finally {
      setFetching(false);
    }
  };

  const handleGenerateFromPaste = async () => {
    if (!manualEmail.body) {
      alert('Inserisci almeno il testo dell\'email');
      return;
    }

    try {
      setGenerating(true);
      const response = await axios.post('/api/emails/generate-manual', {
        workspace_id: workspaceId,
        oggetto: manualEmail.subject,
        corpo: manualEmail.body,
        mittente: manualEmail.sender
      });
      
      setGeneratedResponse(response.data.risposta);
      alert('Risposta generata! Puoi copiarla qui sotto.');
    } catch (err) {
      alert('Errore nella generazione: ' + (err.response?.data?.errore || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyResponse = () => {
    navigator.clipboard.writeText(generatedResponse);
    alert('Risposta copiata negli appunti!');
  };

  const handleClosePasteDialog = () => {
    setPasteDialogOpen(false);
    setManualEmail({ subject: '', body: '', sender: '' });
    setGeneratedResponse('');
    setFeedbackRating(0);
    setFeedbackComment('');
  };

  const handleSaveToHistory = async () => {
    if (feedbackRating === 0) {
      alert('Dai una valutazione prima di salvare');
      return;
    }

    try {
      setSavingToHistory(true);
      await axios.post('/api/historical-emails', {
        workspace_id: workspaceId,
        oggetto: manualEmail.subject || 'Email manuale',
        domanda_studente: manualEmail.body,
        risposta: generatedResponse,
        lingua: 'it', // You could detect this
        data_invio: new Date().toISOString()
      });
      
      alert(`Risposta salvata in Email Storiche (${feedbackRating} stelle)!`);
      handleClosePasteDialog();
      loadStats();
    } catch (err) {
      alert('Errore nel salvataggio: ' + (err.response?.data?.errore || err.message));
    } finally {
      setSavingToHistory(false);
    }
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

  const statCards = [
    { title: 'Email Totali', value: stats?.email_totali || 0, icon: <EmailIcon fontSize="large" />, color: '#1976d2' },
    { title: 'Bozze in Attesa', value: stats?.bozze_pending || 0, icon: <DraftsIcon fontSize="large" />, color: '#ed6c02' },
    { title: 'Bozze Approvate', value: stats?.bozze_approvate || 0, icon: <CheckIcon fontSize="large" />, color: '#2e7d32' },
    { title: 'Email Inviate', value: stats?.email_inviate || 0, icon: <SendIcon fontSize="large" />, color: '#9c27b0' }
  ];

  return (
    <Box>
      <Box mb={4} display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<PasteIcon />}
            onClick={() => setPasteDialogOpen(true)}
          >
            Incolla Testo Email
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleFetchEmails}
            disabled={fetching}
          >
            {fetching ? <CircularProgress size={24} /> : 'Recupera Nuove Email'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3} mb={4}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="body2">
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Knowledge Base
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Email Storiche:</strong> {stats?.email_storiche || 0}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body1">
              <strong>Documenti di Contesto:</strong> {stats?.documenti_iscrizione || 0}
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configurazione Sistema
        </Typography>
        <Typography variant="body2" color="textSecondary">
          <strong>Modello LLM:</strong> {stats?.llm_model || 'N/A'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          <strong>Modello Embedding:</strong> {stats?.embedding_model || 'N/A'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          <strong>Device:</strong> {stats?.device || 'N/A'}
        </Typography>
      </Paper>

      <Dialog open={pasteDialogOpen} onClose={handleClosePasteDialog} maxWidth="md" fullWidth>
        <DialogTitle>Genera Risposta da Testo Incollato</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Mittente (opzionale)"
              value={manualEmail.sender}
              onChange={(e) => setManualEmail({...manualEmail, sender: e.target.value})}
              placeholder="nome@esempio.com"
              fullWidth
            />
            <TextField
              label="Oggetto (opzionale)"
              value={manualEmail.subject}
              onChange={(e) => setManualEmail({...manualEmail, subject: e.target.value})}
              fullWidth
            />
            <TextField
              label="Testo Email *"
              value={manualEmail.body}
              onChange={(e) => setManualEmail({...manualEmail, body: e.target.value})}
              multiline
              rows={8}
              placeholder="Incolla qui il testo dell'email dello studente..."
              fullWidth
              required
            />
            
            {!generatedResponse ? (
              <Button
                variant="contained"
                color="primary"
                onClick={handleGenerateFromPaste}
                disabled={generating || !manualEmail.body}
                fullWidth
              >
                {generating ? <CircularProgress size={24} /> : 'Genera Risposta'}
              </Button>
            ) : (
              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                  Risposta Generata:
                </Typography>
                <TextField
                  value={generatedResponse}
                  multiline
                  rows={10}
                  fullWidth
                  InputProps={{ readOnly: true }}
                  sx={{ mb: 2 }}
                />
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Valuta la risposta:
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Rating
                    value={feedbackRating}
                    onChange={(e, newValue) => setFeedbackRating(newValue)}
                    size="large"
                  />
                  {feedbackRating > 0 && (
                    <Typography variant="body2" color="textSecondary">
                      ({feedbackRating} {feedbackRating === 1 ? 'stella' : 'stelle'})
                    </Typography>
                  )}
                </Box>
                
                <TextField
                  label="Feedback scritto (opzionale)"
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  multiline
                  rows={3}
                  fullWidth
                  placeholder="Es: La risposta menziona prezzi diversi, ma tutti i corsi costano €200"
                  sx={{ mb: 2 }}
                />
                
                <Box display="flex" gap={2}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleCopyResponse}
                    fullWidth
                  >
                    Copia Risposta
                  </Button>
                  {feedbackRating >= 4 && (
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveToHistory}
                      disabled={savingToHistory}
                      fullWidth
                    >
                      {savingToHistory ? <CircularProgress size={20} /> : 'Salva in Storico'}
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    onClick={() => {
                      setGeneratedResponse('');
                      setManualEmail({ subject: '', body: '', sender: '' });
                      setFeedbackRating(0);
                      setFeedbackComment('');
                    }}
                    fullWidth
                  >
                    Nuova Email
                  </Button>
                </Box>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePasteDialog}>Chiudi</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Dashboard;
