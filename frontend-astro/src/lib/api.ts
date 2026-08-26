const API_BASE = import.meta.env.PUBLIC_API_BASE;

export interface Activity {
  id: string;
  title: string;
  starts_at: string;
  capacity: number;
  available_slots: number;
}

export async function getActivities(): Promise<Activity[]> {
  const res = await fetch(`${API_BASE}/api/v1/activities`);
  if (!res.ok) throw new Error(`Error ${res.status} al listar actividades`);
  return res.json();
}

export async function getActivity(id: string): Promise<Activity> {
  const res = await fetch(`${API_BASE}/api/v1/activities/${id}`);
  if (!res.ok) throw new Error(`Error ${res.status} al consultar la actividad ${id}`);
  return res.json();
}