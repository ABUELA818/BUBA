import { useState } from 'react';

interface HeightInputProps {
  onConfirm: (heightCm: number) => void;
}

export function HeightInput({ onConfirm }: HeightInputProps) {
  const [value, setValue] = useState('');
  const [error, setError] = useState('');

  const handleConfirm = () => {
    const num = parseInt(value, 10);
    if (isNaN(num) || num < 100 || num > 250) {
      setError('Ingresa una altura válida entre 100 y 250 cm');
      return;
    }
    setError('');
    onConfirm(num);
  };

  return (
    <div style={containerStyle}>
      <h2 style={{ color: 'white', margin: '0 0 8px 0' }}>¿Cuál es tu altura?</h2>
      <p style={{ color: '#aaa', margin: '0 0 20px 0', fontSize: '14px' }}>
        Necesitamos tu altura real para calcular las medidas correctamente.
      </p>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        <input
          type="number"
          value={value}
          onChange={e => setValue(e.target.value)}
          placeholder="170"
          min={100}
          max={250}
          style={inputStyle}
          onKeyDown={e => e.key === 'Enter' && handleConfirm()}
        />
        <span style={{ color: '#aaa', fontSize: '18px' }}>cm</span>
      </div>
      {error && (
        <p style={{ color: '#ff4444', fontSize: '13px', margin: '8px 0 0 0' }}>{error}</p>
      )}
      <button onClick={handleConfirm} style={buttonStyle}>
        Continuar
      </button>
    </div>
  );
}

const containerStyle: React.CSSProperties = {
  background: '#1a1a1a',
  borderRadius: '16px',
  padding: '32px',
  width: '100%',
  maxWidth: '400px',
  display: 'flex',
  flexDirection: 'column',
};

const inputStyle: React.CSSProperties = {
  background: '#2a2a2a',
  border: '1px solid #444',
  borderRadius: '8px',
  color: 'white',
  fontSize: '24px',
  padding: '12px 16px',
  width: '120px',
  outline: 'none',
};

const buttonStyle: React.CSSProperties = {
  marginTop: '24px',
  background: '#6366f1',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  padding: '12px 24px',
  fontSize: '16px',
  cursor: 'pointer',
  fontWeight: 600,
};