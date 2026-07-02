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

export type EventFormFieldType =
  | "short_text"
  | "long_text"
  | "single_choice"
  | "multiple_choice"
  | "number"
  | "date"
  | "email"
  | "phone"
  | "telegram"
  | "url";

export type EventFormField = {
  id: number;
  field_type: EventFormFieldType;
  label: string;
  help_text: string;
  is_required: boolean;
  order: number;
  choices: string[];
  validation: Record<string, unknown>;
};

export type EventTicketStatus = "active" | "cancelled" | "checked_in" | "expired";

export type EventTicket = {
  code: string;
  status: EventTicketStatus;
  created_at: string;
  checked_in_at: string | null;
  expires_at: string | null;
};

export type EventRegistrationAnswer = {
  field_id: number;
  field_label: string;
  field_type: EventFormFieldType;
  value: string | string[] | null;
  created_at: string;
};

export type ParticipationRecord = {
  id: number;
  event_title: string;
  event_slug: string;
  organizer_name: string;
  attendance_status: "checked_in" | "no_show";
  participation_type: "attendee" | "speaker" | "volunteer";
  verification_status: "verified" | "revoked";
  verified_at: string;
  record_id: string;
  public_verification_code: string;
  starts_at: string;
  created_at: string;
};

export type EventNotificationType =
  | "registration_confirmed"
  | "registration_cancelled"
  | "event_approved"
  | "event_rejected"
  | "organizer_new_registration"
  | "event_reminder_pending"
  | "check_in_confirmed"
  | "participation_verified";

export type EventNotification = {
  id: number;
  notification_type: EventNotificationType;
  channel: "internal" | "telegram";
  status: "pending" | "skipped" | "failed";
  payload: Record<string, unknown>;
  event_title: string;
  event_slug: string;
  created_at: string;
};

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
  registration_form_fields: EventFormField[];
  registration_ticket: EventTicket | null;
};

export type EventRegistration = {
  id: number;
  event: EventDetails;
  status: EventRegistrationStatus;
  payment_status: "not_required" | "pending" | "paid" | "waived";
  registration_data: Record<string, unknown>;
  contact_snapshot: Record<string, string>;
  ticket: EventTicket | null;
  answers: EventRegistrationAnswer[];
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
  ticket_status: EventTicketStatus | "";
  checked_in_at: string | null;
  participation_verified: boolean;
  answers: EventRegistrationAnswer[];
  created_at: string;
};

export type OrganizerEventForm = {
  event: string;
  can_edit: boolean;
  fields: EventFormField[];
};

export type OrganizerEventAnalytics = {
  total_events: number;
  draft_count: number;
  pending_count: number;
  published_count: number;
  rejected_count: number;
  cancelled_count: number;
  archived_count: number;
  total_registrations: number;
  checked_in_count: number;
  attendance_rate: number | null;
  capacity_fill_percentage: number | null;
  registrations_by_event: Array<{
    slug: string;
    title: string;
    registration_count: number;
    checked_in_count: number;
  }>;
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
