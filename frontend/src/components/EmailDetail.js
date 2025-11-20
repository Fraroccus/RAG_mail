import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Rating,
  FormGroup,
  FormControlLabel,
  Checkbox
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  AutoFixHigh as GenerateIcon,
  Check as ApproveIcon,
  Close as RejectIcon,
  Send as SendIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import axios from 'axios';

function EmailDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [email, setEmail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedResponse, setEditedResponse] = useState('');
  const [adminNotes, setAdminNotes] = useState('');
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [feedbackDialogOpen, setFeedbackDialogOpen] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackCategories, setFeedbackCategories] = useState({
    tone: false,
    accuracy: false,
    completeness: false,
    language: false,
    style: false
  });

  useEffect(() => {
    loadEmail();
  }, [id]);

  const loadEmail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/emails/${id}`);
      setEmail(response.data);
      if (response.data.bozza) {
        setEditedResponse(response.data.bozza.edited_response || response.data.bozza.generated_response);
        setAdminNotes(response.data.bozza.admin_notes || '');
      }
      setError(null);
    } catch (err) {
      setError('Errore nel caricamento dell\'email');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDraft = async () => {
    try {
      setGenerating(true);
      await axios.post(`/api/drafts/generate/${id}`);
      await loadEmail();
      alert('Bozza generata con successo!');
    } catch (err) {
      alert('Errore nella generazione: ' + (err.response?.data?.errore || err.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleUpdateDraft = async () => {
    try {
      await axios.put(`/api/drafts/${email.bozza.id}`, {
        testo_modificato: editedResponse,
        note_admin: adminNotes
      });
      setIsEditing(false);
      await loadEmail();
      alert('Bozza aggiornata!');
    } catch (err) {
      alert('Errore nell\'aggiornamento: ' + err.message);
    }
  };

  const handleApproveDraft = async () => {
    try {
      await axios.post(`/api/drafts/${email.bozza.id}/approve`, {
        revisore: 'admin'
      });
      await loadEmail();
      alert('Bozza approvata!');
    } catch (err) {
      alert('Errore nell\'approvazione: ' + err.message);
    }
  };

  const handleRejectDraft = async () => {
    try {
      await axios.post(`/api/drafts/${email.bozza.id}/reject`, {
        revisore: 'admin',
        motivo: rejectReason
      });
      setRejectDialogOpen(false);
      setRejectReason('');
      await loadEmail();
      alert('Bozza rifiutata');
    } catch (err) {
      alert('Errore nel rifiuto: ' + err.message);
    }
  };

  const handleSendEmail = async () => {
    if (!window.confirm('Sei sicuro di voler inviare questa email?')) {
      return;
    }
    
    try {
      await axios.post(`/api/drafts/${email.bozza.id}/send`);
      await loadEmail();
      alert('Email inviata con successo!');
    } catch (err) {
      alert('Errore nell\'invio: ' + (err.response?.data?.errore || err.message));
    }
  };

  const handleSubmitFeedback = async () => {
    try {
      const categories = Object.keys(feedbackCategories).filter(k => feedbackCategories[k]);
      
      await axios.post(`/api/drafts/${email.bozza.id}/feedback`, {
        rating: feedbackRating,
        comment: feedbackComment,
        categories: categories
      });

      setMessage({ type: 'success', text: 'Feedback inviato con successo!' });
      setFeedbackDialogOpen(false);
      loadEmail();
    } catch (error) {
      console.error('Errore invio feedback:', error);
      setMessage({ type: 'error', text: 'Errore nell\'invio del feedback' });
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error || !email) {
    return <Alert severity="error">{error || 'Email non trovata'}</Alert>;
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('it-IT');
  };

  return (
    <Box>
      <Button
        startIcon={<BackIcon />}
        onClick={() => navigate('/emails')}
        sx={{ mb: 2 }}
      >
        Torna alle Email
      </Button>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {email.subject}
        </Typography>
        
        <Grid container spacing={2} sx={{ mt: 2, mb: 2 }}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              <strong>Da:</strong> {email.sender_name} ({email.sender_email})
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              <strong>Data:</strong> {formatDate(email.received_date)}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="textSecondary">
              <strong>Lingua Rilevata:</strong> <Chip label={email.detected_language?.toUpperCase()} size="small" />
            </Typography>
          </Grid>
          {email.query_type && (
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                <strong>Tipo Query:</strong> {email.query_type}
              </Typography>
            </Grid>
          )}
        </Grid>

        <Divider sx={{ my: 2 }} />

        <Typography variant="h6" gutterBottom>
          Testo Email
        </Typography>
        <Box 
          sx={{ 
            p: 2, 
            backgroundColor: '#f5f5f5', 
            borderRadius: 1,
            whiteSpace: 'pre-wrap',
            maxHeight: '400px',
            overflow: 'auto'
          }}
        >
          {email.body}
        </Box>
      </Paper>

      {!email.bozza ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" gutterBottom>
            Nessuna bozza generata per questa email
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={generating ? <CircularProgress size={20} /> : <GenerateIcon />}
            onClick={handleGenerateDraft}
            disabled={generating}
            sx={{ mt: 2 }}
          >
            {generating ? 'Generazione in corso...' : 'Genera Bozza Risposta'}
          </Button>
        </Paper>
      ) : (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Bozza Risposta
            </Typography>
            <Box>
              <Chip 
                label={email.bozza.status.toUpperCase()} 
                color={
                  email.bozza.status === 'sent' ? 'primary' :
                  email.bozza.status === 'approved' ? 'success' :
                  email.bozza.status === 'rejected' ? 'error' : 'warning'
                }
              />
              {email.bozza.confidence_score && (
                <Chip 
                  label={`Confidenza: ${(email.bozza.confidence_score * 100).toFixed(0)}%`}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
          </Box>

          {isEditing ? (
            <Box>
              <TextField
                fullWidth
                multiline
                rows={12}
                value={editedResponse}
                onChange={(e) => setEditedResponse(e.target.value)}
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                multiline
                rows={3}
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                label="Note Admin"
                variant="outlined"
                sx={{ mb: 2 }}
              />
              <Button variant="contained" onClick={handleUpdateDraft} sx={{ mr: 1 }}>
                Salva Modifiche
              </Button>
              <Button variant="outlined" onClick={() => setIsEditing(false)}>
                Annulla
              </Button>
            </Box>
          ) : (
            <Box>
              <Box 
                sx={{ 
                  p: 2, 
                  backgroundColor: '#f5f5f5', 
                  borderRadius: 1,
                  whiteSpace: 'pre-wrap',
                  mb: 2,
                  maxHeight: '500px',
                  overflow: 'auto'
                }}
              >
                {editedResponse}
              </Box>
              
              {email.bozza.status === 'pending' && (
                <Box display="flex" gap={1} mb={2}>
                  <Button
                    variant="outlined"
                    startIcon={<EditIcon />}
                    onClick={() => setIsEditing(true)}
                  >
                    Modifica
                  </Button>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<ApproveIcon />}
                    onClick={handleApproveDraft}
                  >
                    Approva
                  </Button>
                  <Button
                    variant="contained"
                    color="error"
                    startIcon={<RejectIcon />}
                    onClick={() => setRejectDialogOpen(true)}
                  >
                    Rifiuta
                  </Button>
                </Box>
              )}

              {email.bozza.status === 'approved' && (
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<SendIcon />}
                  onClick={handleSendEmail}
                >
                  Invia Email
                </Button>
              )}

              {email.bozza.status === 'sent' && !email.bozza.feedback_submitted_at && (
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => setFeedbackDialogOpen(true)}
                  sx={{ mt: 2 }}
                >
                  Dai Feedback
                </Button>
              )}

              {email.bozza.feedback_rating && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Feedback Inviato
                  </Typography>
                  <Rating value={email.bozza.feedback_rating} readOnly />
                  {email.bozza.feedback_comment && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {email.bozza.feedback_comment}
                    </Typography>
                  )}
                  {email.bozza.feedback_categories && email.bozza.feedback_categories.length > 0 && (
                    <Box sx={{ mt: 1 }}>
                      {email.bozza.feedback_categories.map(cat => (
                        <Chip key={cat} label={cat} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </Box>
                  )}
                </Box>
              )}

              {email.bozza.admin_notes && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  <strong>Note:</strong> {email.bozza.admin_notes}
                </Alert>
              )}
            </Box>
          )}
        </Paper>
      )}

      <Dialog open={feedbackDialogOpen} onClose={() => setFeedbackDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Feedback sulla Risposta Generata</DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom sx={{ mt: 1 }}>
            Quanto è stata buona la risposta generata?
          </Typography>
          <Rating
            value={feedbackRating}
            onChange={(event, newValue) => setFeedbackRating(newValue)}
            size="large"
            sx={{ mb: 2 }}
          />

          <TextField
            fullWidth
            multiline
            rows={4}
            value={feedbackComment}
            onChange={(e) => setFeedbackComment(e.target.value)}
            label="Commenti e suggerimenti (opzionale)"
            placeholder="Es: La risposta era troppo formale, usare un tono più amichevole..."
            variant="outlined"
            sx={{ mb: 2 }}
          />

          <Typography variant="body2" gutterBottom>
            Aree da migliorare:
          </Typography>
          <FormGroup>
            <FormControlLabel
              control={<Checkbox checked={feedbackCategories.tone} onChange={(e) => setFeedbackCategories({...feedbackCategories, tone: e.target.checked})} />}
              label="Tono / Stile"
            />
            <FormControlLabel
              control={<Checkbox checked={feedbackCategories.accuracy} onChange={(e) => setFeedbackCategories({...feedbackCategories, accuracy: e.target.checked})} />}
              label="Precisione informazioni"
            />
            <FormControlLabel
              control={<Checkbox checked={feedbackCategories.completeness} onChange={(e) => setFeedbackCategories({...feedbackCategories, completeness: e.target.checked})} />}
              label="Completezza"
            />
            <FormControlLabel
              control={<Checkbox checked={feedbackCategories.language} onChange={(e) => setFeedbackCategories({...feedbackCategories, language: e.target.checked})} />}
              label="Uso della lingua"
            />
            <FormControlLabel
              control={<Checkbox checked={feedbackCategories.style} onChange={(e) => setFeedbackCategories({...feedbackCategories, style: e.target.checked})} />}
              label="Formattazione"
            />
          </FormGroup>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialogOpen(false)}>Annulla</Button>
          <Button onClick={handleSubmitFeedback} variant="contained" disabled={feedbackRating === 0}>
            Invia Feedback
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)}>
        <DialogTitle>Rifiuta Bozza</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            label="Motivo del rifiuto"
            variant="outlined"
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)}>Annulla</Button>
          <Button onClick={handleRejectDraft} color="error" variant="contained">
            Rifiuta
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default EmailDetail;
