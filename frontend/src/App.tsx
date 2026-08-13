import { useEffect, useState } from 'react'
import './App.css'

interface Activity {
  id: number
  title: string
  starts_at: string
  capacity: number
}

async function fetchActivities(): Promise<Activity[]> {
  const response = await fetch('/api/activities/')
  if (!response.ok) {
    throw new Error('Error al obtener las actividades')
  }
  const payload = await response.json()
  return payload.data
}

function App() {
  return (
    <main>
      <h1>Vite + React + TypeScript</h1>
      <p>Frontend conectado con Django a través de useEffect.</p>
      <ActivitiesList />
    </main>
  )
}

function ActivitiesList() {
  const [activities, setActivities] = useState<Activity[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    fetchActivities()
      .then((data) => {
        if (!cancelled) setActivities(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Error desconocido')
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (error) {
    return <p>Error: {error}</p>
  }

  if (activities === null) {
    return <p>Cargando actividades...</p>
  }

  if (activities.length === 0) {
    return <p>No hay actividades cargadas.</p>
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">Título</th>
            <th scope="col">Comienza</th>
            <th scope="col">Capacidad</th>
          </tr>
        </thead>
        <tbody>
          {activities.map((activity) => (
            <tr key={activity.id}>
              <td><code>{activity.id}</code></td>
              <td>{activity.title}</td>
              <td>
                <time dateTime={activity.starts_at}>
                  {new Date(activity.starts_at).toLocaleString()}
                </time>
              </td>
              <td>{activity.capacity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App