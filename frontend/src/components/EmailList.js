import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert
} from '@mui/material';
import { Visibility as ViewIcon } from '@mui/icons-material';
import axios from 'axios';

function EmailList() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/emails');
      setEmails(response.data.email);
      setError(null);
    } catch (err) {
      setError('Errore nel caricamento delle email');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (email) => {
    if (!email.bozza) {
      return <Chip label="Nuova" color="default" size="small" />;
    }
    
    const status = email.bozza.status;
    const statusMap = {
      'pending': { label: 'In Attesa', color: 'warning' },
      'approved': { label: 'Approvata', color: 'success' },
      'rejected': { label: 'Rifiutata', color: 'error' },
      'sent': { label: 'Inviata', color: 'primary' }
    };
    
    const statusInfo = statusMap[status] || { label: status, color: 'default' };
    return <Chip label={statusInfo.label} color={statusInfo.color} size="small" />;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('it-IT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
          Email
        </Typography>
      </Box>

      {emails.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="textSecondary">
            Nessuna email trovata. Clicca su "Recupera Nuove Email" nella Dashboard.
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Data Ricezione</TableCell>
                <TableCell>Da</TableCell>
                <TableCell>Oggetto</TableCell>
                <TableCell>Lingua</TableCell>
                <TableCell>Stato</TableCell>
                <TableCell>Azioni</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {emails.map((email) => (
                <TableRow key={email.id} hover>
                  <TableCell>{formatDate(email.received_date)}</TableCell>
                  <TableCell>
                    <div>
                      <strong>{email.sender_name}</strong>
                    </div>
                    <div style={{ fontSize: '0.85em', color: '#666' }}>
                      {email.sender_email}
                    </div>
                  </TableCell>
                  <TableCell>{email.subject}</TableCell>
                  <TableCell>
                    <Chip 
                      label={email.detected_language?.toUpperCase() || 'N/A'} 
                      size="small" 
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{getStatusChip(email)}</TableCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<ViewIcon />}
                      onClick={() => navigate(`/emails/${email.id}`)}
                    >
                      Visualizza
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}

export default EmailList;
