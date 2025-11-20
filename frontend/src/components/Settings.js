import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Box,
  CircularProgress
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import axios from 'axios';

function Settings({ workspaceId }) {
  const [systemPrompt, setSystemPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (workspaceId) {
      loadSystemPrompt();
    }
  }, [workspaceId]);

  const loadSystemPrompt = async () => {
    if (!workspaceId) return;
    
    try {
      const response = await axios.get(`/api/settings/system_prompt?workspace_id=${workspaceId}`);
      setSystemPrompt(response.data.value || '');
    } catch (error) {
      if (error.response?.status === 404) {
        // Setting doesn't exist yet, that's fine
        setSystemPrompt('');
      } else {
        console.error('Errore caricamento prompt:', error);
        setMessage({ type: 'error', text: 'Errore nel caricamento delle impostazioni' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);

    try {
      await axios.put('/api/settings/system_prompt', {
        value: systemPrompt,
        description: 'Prompt di sistema per guidare il comportamento del LLM',
        workspace_id: workspaceId
      });

      setMessage({ type: 'success', text: 'Impostazioni salvate con successo!' });
    } catch (error) {
      console.error('Errore salvataggio:', error);
      setMessage({ type: 'error', text: 'Errore nel salvataggio' });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setSystemPrompt('Sei un assistente email per ITS MAKER ACADEMY FOUNDATION.');
    setMessage({ type: 'info', text: 'Ripristinato prompt predefinito' });
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Impostazioni Sistema
      </Typography>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Prompt di Sistema
        </Typography>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Questo testo viene utilizzato per guidare il comportamento del modello AI quando genera risposte.
          Puoi specificare il ruolo, il tono, le linee guida e qualsiasi altra istruzione importante.
        </Typography>

        <TextField
          fullWidth
          multiline
          rows={12}
          value={systemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          placeholder="Esempio: Sei un assistente email per ITS MAKER ACADEMY FOUNDATION. Il tuo compito è rispondere alle domande degli studenti internazionali in modo professionale e cortese..."
          variant="outlined"
          sx={{ mb: 2 }}
        />

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Salvataggio...' : 'Salva Modifiche'}
          </Button>

          <Button
            variant="outlined"
            onClick={handleReset}
            disabled={saving}
          >
            Ripristina Predefinito
          </Button>
        </Box>

        {message && (
          <Alert severity={message.type} sx={{ mt: 2 }}>
            {message.text}
          </Alert>
        )}

        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            💡 Suggerimenti
          </Typography>
          <Typography variant="body2" component="div">
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>Specifica chiaramente il ruolo dell'assistente</li>
              <li>Indica il tono desiderato (professionale, amichevole, formale, etc.)</li>
              <li>Menziona informazioni importanti da ricordare sempre</li>
              <li>Fornisci linee guida su cosa fare quando non si hanno informazioni</li>
              <li>Le modifiche si applicheranno alle prossime risposte generate</li>
            </ul>
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}

export default Settings;
