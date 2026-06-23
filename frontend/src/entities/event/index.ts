export type EventCategory = {
  name: string;
  slug: string;
};

export type EventLocation = {
  country: string;
  city: string;
  venue: string;
  latitude: string | null;
  longitude: string | null;
};

export type EventSource = {
  source_title: string;
  source_url: string;
  is_official: boolean;
  retrieved_at: string;
};

export type EventRegistrationStatus =
  | "registered"
  | "cancelled"
  | "waitlisted"
  | "attended";

export type EventPriceType = "free" | "paid" | "external" | "unknown";

export type EventModerationStatus =
  | "draft"
  | "pending_review"
  | "published"
  | "rejected"
  | "cancelled"
  | "archived";

export type EventDetails = {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  category: EventCategory;
  organizer_name: string;
  location: EventLocation;
  is_online: boolean;
  online_url: string;
  format: "online" | "offline" | "hybrid";
  start_at: string;
  end_at: string | null;
  registration_deadline: string | null;
  capacity: number | null;
  registration_count: number;
  spots_left: number | null;
  price_type: EventPriceType;
  price_amount: string | null;
  currency: string;
  status: "published";
  visibility: "public";
  cover_image_url: string;
  language: string;
  eligibility: string;
  scholarship_available: boolean;
  source: EventSource;
  registration_status: EventRegistrationStatus | null;
};

export type EventRegistration = {
  id: number;
  event: EventDetails;
  status: EventRegistrationStatus;
  payment_status: "not_required" | "pending" | "paid" | "waived";
  registration_data: Record<string, unknown>;
  contact_snapshot: Record<string, string>;
  created_at: string;
  updated_at: string;
};

export type PaginatedResponse<Item> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Item[];
};

export type EventFilters = {
  search?: string;
  category?: string;
  country?: string;
  city?: string;
  price_type?: string;
  format?: string;
};

export type OrganizerEvent = {
  id: number;
  title: string;
  slug: string;
  short_description: string;
  description: string;
  category: EventCategory;
  organizer_name: string;
  organizer_email: string;
  format: "online" | "offline" | "hybrid";
  is_online: boolean;
  online_url: string;
  start_at: string;
  end_at: string | null;
  registration_deadline: string | null;
  capacity: number | null;
  price_type: EventPriceType;
  price_amount: string | null;
  currency: string;
  visibility: "public" | "private";
  cover_image_url: string;
  language: string;
  eligibility: string;
  scholarship_available: boolean;
  location: EventLocation;
  source: EventSource;
  status: EventModerationStatus;
  moderation_note: string;
  can_edit: boolean;
  can_submit: boolean;
  can_view_participants: boolean;
  created_at: string;
  updated_at: string;
};

export type OrganizerEventInput = {
  title: string;
  short_description: string;
  description: string;
  category_slug: string;
  organizer_name: string;
  format: OrganizerEvent["format"];
  is_online: boolean;
  online_url: string;
  start_at: string;
  end_at: string | null;
  registration_deadline: string | null;
  capacity: number | null;
  price_type: EventPriceType;
  price_amount: string | null;
  currency: string;
  visibility: OrganizerEvent["visibility"];
  cover_image_url: string;
  language: string;
  eligibility: string;
  location: Omit<EventLocation, "latitude" | "longitude"> & {
    latitude: null;
    longitude: null;
  };
  source: {
    source_title: string;
    source_url: string;
    is_official: boolean;
  };
};

export type OrganizerParticipant = {
  id: number;
  full_name: string;
  email: string;
  telegram_username: string;
  status: EventRegistrationStatus;
  payment_status: EventRegistration["payment_status"];
  created_at: string;
};

export type EventModerationLog = {
  id: number;
  previous_status: EventModerationStatus;
  new_status: EventModerationStatus;
  note: string;
  moderator_email: string;
  created_at: string;
};

export { EventCard } from "./ui/event-card";
export { EventMapPreview } from "./ui/event-map-preview";
export { ModerationStatusBadge } from "./ui/moderation-status-badge";
