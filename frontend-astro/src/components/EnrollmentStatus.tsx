import { useState, useEffect } from 'react';

interface Enrollment {
  activity_id: string;
  participant_id: string;
  enrolled_at: string;
}

interface Props {
  activityId: string;
  apiBase: string;
}

export default function EnrollmentStatus({ activityId, apiBase }: Props) {
  const [enrolled, setEnrolled] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const participantId = 'test-participant-1';

  useEffect(() => {
    async function checkEnrollment() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiBase}/api/v1/me/enrollments`, {
          headers: { 'X-Demo-Participant-Id': participantId },
        });
        if (!res.ok) throw new Error(`Error ${res.status}`);
        const enrollments: Enrollment[] = await res.json();
        const isEnrolled = enrollments.some((e) => e.activity_id === activityId);
        setEnrolled(isEnrolled);
      } catch (e) {
        setError('No se pudieron consultar las inscripciones.');
      } finally {
        setLoading(false);
      }
    }
    checkEnrollment();
  }, [activityId, apiBase]);

  async function handleEnroll() {
    setActionLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/me/enrollments/${activityId}`, {
        method: 'PUT',
        headers: { 'X-Demo-Participant-Id': participantId },
      });
      if (res.status === 201 || res.status === 200) {
        setEnrolled(true);
      } else if (res.status === 409) {
        setError('No quedan cupos disponibles.');
      } else if (res.status === 400) {
        setError('Identidad de demostración inválida.');
      } else {
        setError(`Error inesperado: ${res.status}`);
      }
    } catch {
      setError('Error de red al intentar inscribirse.');
    } finally {
      setActionLoading(false);
    }
  }

  async function handleUnenroll() {
    setActionLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiBase}/api/v1/me/enrollments/${activityId}`, {
        method: 'DELETE',
        headers: { 'X-Demo-Participant-Id': participantId },
      });
      if (res.status === 204) {
        setEnrolled(false);
      } else if (res.status === 400) {
        setError('Identidad de demostración inválida.');
      } else {
        setError(`Error inesperado: ${res.status}`);
      }
    } catch {
      setError('Error de red al cancelar inscripción.');
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return <p style={{ color: '#888' }}>Cargando estado de inscripción...</p>;
  }

  return (
    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
      {enrolled ? (
        <>
          <p style={{ color: '#16a34a', fontWeight: 'bold' }}>Estás inscripto en esta actividad.</p>
          <button
            onClick={handleUnenroll}
            disabled={actionLoading}
            style={{
              marginTop: '0.5rem',
              padding: '0.5rem 1rem',
              background: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: actionLoading ? 'not-allowed' : 'pointer',
              opacity: actionLoading ? 0.6 : 1,
            }}
          >
            {actionLoading ? 'Cancelando...' : 'Cancelar inscripción'}
          </button>
        </>
      ) : (
        <>
          <p>No estás inscripto en esta actividad.</p>
          <button
            onClick={handleEnroll}
            disabled={actionLoading}
            style={{
              marginTop: '0.5rem',
              padding: '0.5rem 1rem',
              background: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: actionLoading ? 'not-allowed' : 'pointer',
              opacity: actionLoading ? 0.6 : 1,
            }}
          >
            {actionLoading ? 'Inscribiendo...' : 'Inscribirme'}
          </button>
        </>
      )}

      {error && (
        <p style={{ marginTop: '0.5rem', color: '#dc2626' }}>{error}</p>
      )}
    </div>
  );
}
