"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/lib/auth";
import type { AdminListResponse } from "@/types/admin";

interface AdminCrudClient<T, TPayload> {
  list(token: string, query?: Record<string, string | number>): Promise<AdminListResponse<T>>;
  fetch(token: string, id: string | number): Promise<T>;
  create(token: string, payload: TPayload): Promise<T>;
  update(token: string, id: string | number, payload: TPayload): Promise<T>;
  remove(token: string, id: string | number): Promise<void>;
}

/** Builds the useXList/useX/useCreateX/useUpdateX/useDeleteX hooks for one admin
 * resource on top of its adminApi CRUD client — every resource in src/hooks/admin/
 * follows this exact shape, so the pattern lives here once. */
export function createAdminResourceHooks<T, TPayload>(
  key: string,
  client: AdminCrudClient<T, TPayload>
) {
  function useList(query?: Record<string, string | number>) {
    const { token } = useAuth();
    return useQuery({
      queryKey: [key, "list", query],
      queryFn: () => client.list(token as string, query),
      enabled: Boolean(token),
    });
  }

  function useDetail(id: string | number | undefined) {
    const { token } = useAuth();
    return useQuery({
      queryKey: [key, "detail", id],
      queryFn: () => client.fetch(token as string, id as string | number),
      enabled: Boolean(token) && id !== undefined,
    });
  }

  function useCreate() {
    const { token } = useAuth();
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: (payload: TPayload) => client.create(token as string, payload),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: [key, "list"] }),
    });
  }

  function useUpdate() {
    const { token } = useAuth();
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: ({ id, payload }: { id: string | number; payload: TPayload }) =>
        client.update(token as string, id, payload),
      onSuccess: (_data, variables) => {
        queryClient.invalidateQueries({ queryKey: [key, "list"] });
        queryClient.invalidateQueries({ queryKey: [key, "detail", variables.id] });
      },
    });
  }

  function useDelete() {
    const { token } = useAuth();
    const queryClient = useQueryClient();
    return useMutation({
      mutationFn: (id: string | number) => client.remove(token as string, id),
      onSuccess: () => queryClient.invalidateQueries({ queryKey: [key, "list"] }),
    });
  }

  return { useList, useDetail, useCreate, useUpdate, useDelete };
}
