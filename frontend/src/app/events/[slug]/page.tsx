import { EventDetailScreen } from "@/screens/events/event-detail";

export default async function Page({
  params
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <EventDetailScreen slug={slug} />;
}

