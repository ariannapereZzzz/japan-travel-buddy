import type { ExpenseInput, Trip } from "@/features/trip/lib/types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8200";
export const TRIP_SLUG = "japan-2026";
export const tripQueryKey = ["trip", TRIP_SLUG] as const;

async function request(path: string, init?: RequestInit): Promise<Trip> {
  const response = await fetch(`${API_URL}/api/v1/trips/${TRIP_SLUG}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error("Request failed");
  }
  return response.json() as Promise<Trip>;
}

export function fetchTrip() {
  return request("");
}

export function updateTask(taskId: string, checked: boolean) {
  return request(`/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify({ checked }),
  });
}

export function resetItinerary() {
  return request("/itinerary/reset", { method: "POST" });
}

export function updatePacking(itemId: string, checked: boolean) {
  return request(`/packing/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ checked }),
  });
}

export function resetPacking() {
  return request("/packing/reset", { method: "POST" });
}

export function addShopping(text: string) {
  return request("/shopping", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function updateShopping(itemId: string, done: boolean) {
  return request(`/shopping/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ done }),
  });
}

export function deleteShopping(itemId: string) {
  return request(`/shopping/${itemId}`, { method: "DELETE" });
}

export function addExpense(input: ExpenseInput) {
  return request("/expenses", { method: "POST", body: JSON.stringify(input) });
}

export function deleteExpense(expenseId: string) {
  return request(`/expenses/${expenseId}`, { method: "DELETE" });
}
