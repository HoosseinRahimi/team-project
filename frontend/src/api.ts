import type { Activity, ActivityInput, Project, User } from "./types";

const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "http://localhost:8000";

async function parseError(response: Response): Promise<Error> {
  try {
    const body = (await response.json()) as { detail?: string; error?: string };
    return new Error(body.detail ?? body.error ?? `Request failed with ${response.status}.`);
  } catch {
    return new Error(`Request failed with ${response.status}.`);
  }
}

async function getCollection<T>(name: string): Promise<T[]> {
  const response = await fetch(`${API_BASE_URL}/api/${name}`);
  if (!response.ok) throw await parseError(response);
  return (await response.json()) as T[];
}

export const getUsers = (): Promise<User[]> => getCollection<User>("users");
export const getActivities = (): Promise<Activity[]> => getCollection<Activity>("activities");
export const getProjects = (): Promise<Project[]> => getCollection<Project>("projects");

export async function createActivity(payload: ActivityInput): Promise<Activity> {
  const response = await fetch(`${API_BASE_URL}/api/activities`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw await parseError(response);
  return (await response.json()) as Activity;
}

export async function updateActivity(id: string, payload: ActivityInput): Promise<Activity> {
  const response = await fetch(`${API_BASE_URL}/api/activities/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw await parseError(response);
  return (await response.json()) as Activity;
}

export async function deleteActivity(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/activities/${id}`, { method: "DELETE" });
  if (!response.ok) throw await parseError(response);
}
