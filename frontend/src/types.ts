export type ActivityStatus = "planned" | "in-progress" | "completed";

export interface User {
  id: string;
  name: string;
  role: string;
}

export interface Activity {
  id: string;
  userId: string;
  date: string;
  title: string;
  status: ActivityStatus;
  projectId: string | null;
}

export interface ActivityInput {
  userId: string;
  date: string;
  title: string;
  status: ActivityStatus;
  projectId: string | null;
}

export interface Project {
  id: string;
  userId: string;
  name: string;
  description: string;
  technology: string[];
  status: string;
}
