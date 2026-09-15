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
import { offersAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { OfferAdmin } from "@/types/admin";

const CATEGORIES = [
  "campervan", "car", "hotel", "campsite", "activity", "insurance", "bicycle", "camping_gear",
] as const;

const schema = z.object({
  category: z.enum(CATEGORIES),
  base_url: z.string().min(1, "Required"),
  description: z.string(),
  price_note: z.string(),
  commission_note: z.string(),
});

type FormValues = z.infer<typeof schema>;

interface OfferFormDialogProps {
  partnerId: number;
  offer?: OfferAdmin;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function OfferFormDialog({ partnerId, offer, open, onOpenChange }: OfferFormDialogProps) {
  const createMutation = offersAdminHooks.useCreate();
  const updateMutation = offersAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      category: "campervan",
      base_url: "",
      description: "",
      price_note: "",
      commission_note: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        category: offer?.category ?? "campervan",
        base_url: offer?.base_url ?? "",
        description: offer?.description ?? "",
        price_note: offer?.price_note ?? "",
        commission_note: offer?.commission_note ?? "",
      });
    }
  }, [open, offer, form]);

  async function onSubmit(values: FormValues) {
    try {
      if (offer) {
        await updateMutation.mutateAsync({ id: offer.id, payload: values });
        toast.success("Offer updated.");
      } else {
        await createMutation.mutateAsync({ ...values, partner: partnerId, tracking_params: {} });
        toast.success("Offer created.");
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
          <DialogTitle>{offer ? "Edit offer" : "New offer"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Category</FormLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {CATEGORIES.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="base_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Base URL</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="price_note"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Price note</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. From $99/day" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="commission_note"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Commission note</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={isPending}>
                {offer ? "Save changes" : "Create offer"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
