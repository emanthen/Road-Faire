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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { reservationRulesAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { ReservationRuleAdmin } from "@/types/admin";

const KINDS = ["timed_entry", "vehicle", "permit", "shuttle", "lottery"] as const;

const schema = z.object({
  kind: z.enum(KINDS),
  season_start: z.string(),
  season_end: z.string(),
  booking_url: z.string(),
  processing_fee: z.string(),
  notes: z.string(),
});

type FormValues = z.infer<typeof schema>;

interface ReservationRuleFormDialogProps {
  spotId: number;
  rule?: ReservationRuleAdmin;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function ReservationRuleFormDialog({
  spotId, rule, open, onOpenChange,
}: ReservationRuleFormDialogProps) {
  const createMutation = reservationRulesAdminHooks.useCreate();
  const updateMutation = reservationRulesAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      kind: "timed_entry", season_start: "", season_end: "", booking_url: "",
      processing_fee: "", notes: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        kind: rule?.kind ?? "timed_entry",
        season_start: rule?.season_start ?? "",
        season_end: rule?.season_end ?? "",
        booking_url: rule?.booking_url ?? "",
        processing_fee: rule?.processing_fee ?? "",
        notes: rule?.notes ?? "",
      });
    }
  }, [open, rule, form]);

  async function onSubmit(values: FormValues) {
    const payload = {
      ...values,
      season_start: values.season_start || null,
      season_end: values.season_end || null,
      processing_fee: values.processing_fee || null,
    };
    try {
      if (rule) {
        await updateMutation.mutateAsync({ id: rule.id, payload });
        toast.success("Reservation rule updated.");
      } else {
        await createMutation.mutateAsync({ ...payload, spot: spotId });
        toast.success("Reservation rule created.");
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
          <DialogTitle>{rule ? "Edit reservation rule" : "New reservation rule"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="kind" render={({ field }) => (
              <FormItem>
                <FormLabel>Kind</FormLabel>
                <Select value={field.value} onValueChange={field.onChange}>
                  <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                  <SelectContent>
                    {KINDS.map((kind) => <SelectItem key={kind} value={kind}>{kind.replace("_", " ")}</SelectItem>)}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="season_start" render={({ field }) => (
                <FormItem><FormLabel>Season start</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="season_end" render={({ field }) => (
                <FormItem><FormLabel>Season end</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </div>
            <FormField control={form.control} name="booking_url" render={({ field }) => (
              <FormItem><FormLabel>Booking URL</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="processing_fee" render={({ field }) => (
              <FormItem><FormLabel>Processing fee</FormLabel><FormControl><Input placeholder="0.00" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="notes" render={({ field }) => (
              <FormItem><FormLabel>Notes</FormLabel><FormControl><Textarea rows={3} {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <DialogFooter>
              <Button type="submit" disabled={isPending}>{rule ? "Save changes" : "Create rule"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
