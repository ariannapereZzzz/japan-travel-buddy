import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addExpense,
  addShopping,
  deleteExpense,
  deleteShopping,
  fetchTrip,
  resetItinerary,
  resetPacking,
  tripQueryKey,
  updatePacking,
  updateShopping,
  updateTask,
} from "@/lib/api";
import type { ExpenseInput, Trip } from "@/features/trip/lib/types";

function useSaveTrip<TVariables>(
  mutationFn: (variables: TVariables) => Promise<Trip>,
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: (trip) => {
      queryClient.setQueryData(tripQueryKey, trip);
    },
  });
}

export function useTrip() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: tripQueryKey, queryFn: fetchTrip });
  const taskMutation = useSaveTrip(
    ({ id, checked }: { id: string; checked: boolean }) =>
      updateTask(id, checked),
  );
  const packingMutation = useSaveTrip(
    ({ id, checked }: { id: string; checked: boolean }) =>
      updatePacking(id, checked),
  );
  const shoppingMutation = useSaveTrip(
    ({ id, done }: { id: string; done: boolean }) => updateShopping(id, done),
  );
  const resetItineraryMutation = useSaveTrip(async () => resetItinerary());
  const resetPackingMutation = useSaveTrip(async () => resetPacking());
  const addShoppingMutation = useSaveTrip((text: string) => addShopping(text));
  const deleteShoppingMutation = useSaveTrip((id: string) =>
    deleteShopping(id),
  );
  const addExpenseMutation = useSaveTrip((input: ExpenseInput) =>
    addExpense(input),
  );
  const deleteExpenseMutation = useSaveTrip((id: string) => deleteExpense(id));

  function patchTrip(recipe: (trip: Trip) => Trip) {
    const current = queryClient.getQueryData<Trip>(tripQueryKey);
    if (!current) return current;
    queryClient.setQueryData(tripQueryKey, recipe(current));
    return current;
  }

  const saveError = [
    taskMutation,
    packingMutation,
    shoppingMutation,
    resetItineraryMutation,
    resetPackingMutation,
    addShoppingMutation,
    deleteShoppingMutation,
    addExpenseMutation,
    deleteExpenseMutation,
  ].some((mutation) => mutation.isError);

  return {
    trip: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    refetch: () => {
      void query.refetch();
    },
    saveError,
    toggleTask: (id: string, checked: boolean) => {
      const previous = patchTrip((trip) => ({
        ...trip,
        days: trip.days.map((day) => ({
          ...day,
          tasks: day.tasks.map((item) =>
            item.id === id ? { ...item, checked } : item,
          ),
        })),
      }));
      taskMutation.mutate(
        { id, checked },
        { onError: () => queryClient.setQueryData(tripQueryKey, previous) },
      );
    },
    resetItinerary: () => resetItineraryMutation.mutate(),
    togglePacking: (id: string, checked: boolean) => {
      const previous = patchTrip((trip) => ({
        ...trip,
        packing: trip.packing.map((section) => ({
          ...section,
          items: section.items.map((item) =>
            item.id === id ? { ...item, checked } : item,
          ),
        })),
      }));
      packingMutation.mutate(
        { id, checked },
        { onError: () => queryClient.setQueryData(tripQueryKey, previous) },
      );
    },
    resetPacking: () => resetPackingMutation.mutate(),
    addShopping: (text: string) => addShoppingMutation.mutate(text),
    toggleShopping: (id: string, done: boolean) => {
      const previous = patchTrip((trip) => ({
        ...trip,
        shopping: trip.shopping.map((item) =>
          item.id === id ? { ...item, done } : item,
        ),
      }));
      shoppingMutation.mutate(
        { id, done },
        { onError: () => queryClient.setQueryData(tripQueryKey, previous) },
      );
    },
    deleteShopping: (id: string) => deleteShoppingMutation.mutate(id),
    addExpense: (input: ExpenseInput) => addExpenseMutation.mutate(input),
    deleteExpense: (id: string) => deleteExpenseMutation.mutate(id),
  };
}
