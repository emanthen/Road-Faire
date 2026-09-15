"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { vehicleLimitsAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { VehicleLimitAdmin } from "@/types/admin";

const schema = z.object({
  max_length_ft: z.string(),
  max_height_ft: z.string(),
  max_weight_lb: z.string(),
  effective_from: z.string(),
  applies_to_roads_text: z.string(),
});

type FormValues = z.infer<typeof schema>;

interface VehicleLimitFormDialogProps {
  spotId: number;
  limit?: VehicleLimitAdmin;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function VehicleLimitFormDialog({
  spotId, limit, open, onOpenChange,
}: VehicleLimitFormDialogProps) {
  const createMutation = vehicleLimitsAdminHooks.useCreate();
  const updateMutation = vehicleLimitsAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      max_length_ft: "", max_height_ft: "", max_weight_lb: "", effective_from: "",
      applies_to_roads_text: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        max_length_ft: limit?.max_length_ft ?? "",
        max_height_ft: limit?.max_height_ft ?? "",
        max_weight_lb: limit?.max_weight_lb ? String(limit.max_weight_lb) : "",
        effective_from: limit?.effective_from ?? "",
        applies_to_roads_text: limit?.applies_to_roads?.join(", ") ?? "",
      });
    }
  }, [open, limit, form]);

  async function onSubmit(values: FormValues) {
    const payload = {
      max_length_ft: values.max_length_ft || null,
      max_height_ft: values.max_height_ft || null,
      max_weight_lb: values.max_weight_lb ? Number(values.max_weight_lb) : null,
      effective_from: values.effective_from || null,
      applies_to_roads: values.applies_to_roads_text.split(",").map((s) => s.trim()).filter(Boolean),
    };
    try {
      if (limit) {
        await updateMutation.mutateAsync({ id: limit.id, payload });
        toast.success("Vehicle limit updated.");
      } else {
        await createMutation.mutateAsync({ ...payload, spot: spotId });
        toast.success("Vehicle limit created.");
      }
      onOpenChange(false);
    } catch (error) {
      toast.error(error instanceof ApiError ? String(error.detail) : "Something went wrong.");
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{limit ? "Edit vehicle limit" : "New vehicle limit"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="max_length_ft" render={({ field }) => (
                <FormItem><FormLabel>Max length (ft)</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="max_height_ft" render={({ field }) => (
                <FormItem><FormLabel>Max height (ft)</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </div>
            <FormField control={form.control} name="max_weight_lb" render={({ field }) => (
              <FormItem><FormLabel>Max weight (lb)</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="effective_from" render={({ field }) => (
              <FormItem><FormLabel>Effective from</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="applies_to_roads_text" render={({ field }) => (
              <FormItem><FormLabel>Applies to roads</FormLabel><FormControl><Input placeholder="Going-to-the-Sun Road" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <DialogFooter>
              <Button type="submit" disabled={isPending}>{limit ? "Save changes" : "Create limit"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
