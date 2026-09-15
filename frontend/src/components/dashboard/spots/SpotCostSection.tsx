"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { spotCostsAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";

const schema = z.object({
  entry_vehicle: z.string(),
  entry_person: z.string(),
  parking: z.string(),
  campsite_low: z.string(),
  campsite_high: z.string(),
  shuttle: z.string(),
});

type FormValues = z.infer<typeof schema>;

const MONEY_FIELDS: { name: keyof FormValues; label: string }[] = [
  { name: "entry_vehicle", label: "Entry (per vehicle)" },
  { name: "entry_person", label: "Entry (per person)" },
  { name: "parking", label: "Parking" },
  { name: "campsite_low", label: "Campsite (low)" },
  { name: "campsite_high", label: "Campsite (high)" },
  { name: "shuttle", label: "Shuttle" },
];

export default function SpotCostSection({ spotId }: { spotId: number }) {
  const { data, isLoading } = spotCostsAdminHooks.useList({ spot: spotId });
  const createMutation = spotCostsAdminHooks.useCreate();
  const updateMutation = spotCostsAdminHooks.useUpdate();
  const existing = data?.results[0];

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: {
      entry_vehicle: existing?.entry_vehicle ?? "",
      entry_person: existing?.entry_person ?? "",
      parking: existing?.parking ?? "",
      campsite_low: existing?.campsite_low ?? "",
      campsite_high: existing?.campsite_high ?? "",
      shuttle: existing?.shuttle ?? "",
    },
  });

  async function onSubmit(values: FormValues) {
    const payload = Object.fromEntries(
      Object.entries(values).map(([key, value]) => [key, value === "" ? null : value])
    );
    try {
      if (existing) {
        await updateMutation.mutateAsync({ id: existing.id, payload });
      } else {
        await createMutation.mutateAsync({ ...payload, spot: spotId });
      }
      toast.success("Cost saved.");
    } catch (error) {
      toast.error(error instanceof ApiError ? String(error.detail) : "Something went wrong.");
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  if (isLoading) return <p className="text-muted-foreground">Loading…</p>;

  return (
    <div className="rounded-md border border-border p-4">
      <h2 className="font-medium">Cost</h2>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="mt-4 grid grid-cols-2 gap-4">
          {MONEY_FIELDS.map(({ name, label }) => (
            <FormField
              key={name}
              control={form.control}
              name={name}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{label}</FormLabel>
                  <FormControl>
                    <Input placeholder="0.00" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          ))}
          <Button type="submit" disabled={isPending} className="col-span-2 w-fit">
            Save cost
          </Button>
        </form>
      </Form>
    </div>
  );
}
