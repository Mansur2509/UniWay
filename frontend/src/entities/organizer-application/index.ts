export type OrganizerApplicationStatus = "pending" | "approved" | "rejected";

export type OrganizerApplicationInput = {
  first_name: string;
  last_name: string;
  email: string;
  telegram_username: string;
  description: string;
  project_link?: string;
  motivation: string;
  experience?: string;
};

export type OrganizerApplication = {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  telegram_username: string;
  description: string;
  project_link: string;
  motivation: string;
  experience: string;
  status: OrganizerApplicationStatus;
  created_at: string;
};

export type OrganizerApplicationStatusSummary = {
  id: number;
  status: OrganizerApplicationStatus;
  created_at: string;
  reviewed_at: string | null;
};
