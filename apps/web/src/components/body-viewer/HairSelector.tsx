import type { HairStyle } from './HairMesh';

interface HairSelectorProps {
  hairStyle: HairStyle;
  hairColor: string;
  onStyleChange: (style: HairStyle) => void;
  onColorChange: (color: string) => void;
}

const HAIR_STYLES: { value: HairStyle; label: string }[] = [
  { value: 'bald', label: 'Sin cabello' },
  { value: 'short', label: 'Corto' },
  { value: 'medium', label: 'Medio' },
  { value: 'long', label: 'Largo' },
  { value: 'curly', label: 'Rizado' },
];

const HAIR_COLORS = [
  { value: '#1a0a00', label: 'Negro' },
  { value: '#3b1f0a', label: 'Castaño oscuro' },
  { value: '#7b4a1e', label: 'Castaño' },
  { value: '#c47c2b', label: 'Rubio oscuro' },
  { value: '#e8c170', label: 'Rubio' },
  { value: '#b22222', label: 'Rojo' },
  { value: '#888888', label: 'Gris' },
  { value: '#ffffff', label: 'Blanco' },
];

export function HairSelector({ hairStyle, hairColor, onStyleChange, onColorChange }: HairSelectorProps) {
  return (
    <div style={{
      background: '#1a1a2a',
      border: '1px solid #4f46e5',
      borderRadius: '8px',
      padding: '12px 16px',
      width: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
    }}>
      <p style={{ color: '#a78bfa', margin: 0, fontSize: '13px', fontWeight: 600 }}>
        Cabello
      </p>

      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {HAIR_STYLES.map(s => (
          <button
            key={s.value}
            onClick={() => onStyleChange(s.value)}
            style={{
              background: hairStyle === s.value ? '#6366f1' : '#2a2a3a',
              color: hairStyle === s.value ? 'white' : '#aaa',
              border: `1px solid ${hairStyle === s.value ? '#6366f1' : '#444'}`,
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: hairStyle === s.value ? 600 : 400,
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {hairStyle !== 'bald' && (
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ color: '#aaa', fontSize: '12px' }}>Color:</span>
          {HAIR_COLORS.map(c => (
            <button
              key={c.value}
              onClick={() => onColorChange(c.value)}
              title={c.label}
              style={{
                width: '22px',
                height: '22px',
                borderRadius: '50%',
                background: c.value,
                border: hairColor === c.value ? '2px solid white' : '1px solid #555',
                cursor: 'pointer',
                padding: 0,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}