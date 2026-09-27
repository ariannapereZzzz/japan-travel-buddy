import { createFileRoute } from "@tanstack/react-router";
import { TripPage } from "@/features/trip/pages/TripPage";

export const Route = createFileRoute("/")({
  component: TripPage,
});
