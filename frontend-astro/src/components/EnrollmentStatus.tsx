import { useEffect, useState } from 'react';

interface Enrollment {
  activity_id: string;
}

interface Props {
  activityId: string;
  apiBase: string;
  participantId: string;
}

function randomColor(): string {
  return `hsl(${Math.floor(Math.random() * 360)}, 70%, 60%)`;
}

export default function EnrollmentStatus({ activityId, apiBase, participantId }: Props) {
  const [enrolled, setEnrolled] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  // Se genera UNA vez cuando el componente se monta en el navegador.
  // Se mantiene igual mientras el componente siga montado (ej: al usar el
  // botón), pero cambia cada vez que recargás la página completa, porque
  // ahí React vuelve a montar el componente desde cero.
  const [clientColor] = useState(randomColor);

  const headers = { 'X-Demo-Participant-Id': participantId };

  useEffect(() => {
    fetch(`${apiBase}/api/v1/me/enrollments`, { headers })
      .then((res) => res.json())
      .then((enrollments: Enrollment[]) =>
        setEnrolled(enrollments.some((e) => e.activity_id === activityId))
      )
      .catch(() => setError('No se pudieron consultar las inscripciones.'));
  }, [activityId, apiBase, participantId]);

  async function toggle() {
    setBusy(true);
    setError('');
    const method = enrolled ? 'DELETE' : 'PUT';

    try {
      const res = await fetch(`${apiBase}/api/v1/me/enrollments/${activityId}`, { method, headers });

      if (res.status === 409) setError('No quedan cupos disponibles.');
      else if (res.status === 400) setError('Identidad de demostración inválida.');
      else if (!res.ok) setError(`Error inesperado: ${res.status}`);
      else setEnrolled(!enrolled);
    } catch {
      setError('Error de red.');
    } finally {
      setBusy(false);
    }
  }

  const wrapperStyle = {
    padding: '0.5rem 1rem',
    background: clientColor,
    borderRadius: '6px',
  };

  if (enrolled === null) {
    return (
      <div style={wrapperStyle}>
        <p>Cargando estado de inscripción...</p>
        {error && <p style={{ color: '#dc2626' }}>{error}</p>}
      </div>
    );
  }

  return (
    <div style={wrapperStyle}>
      <small>Color de cliente: {clientColor} (cambia al recargar la página, no al usar el botón)</small>

      <p data-testid="enrollment-status">
        {enrolled ? 'Estás inscripto en esta actividad.' : 'No estás inscripto en esta actividad.'}
      </p>

      <form onSubmit={(e) => { e.preventDefault(); toggle(); }}>
        <button type="submit" disabled={busy}>
          {busy ? 'Procesando...' : enrolled ? 'Cancelar inscripción' : 'Inscribirme'}
        </button>
      </form>

      {error && <p style={{ color: '#dc2626' }}>{error}</p>}
    </div>
  );
}