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
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { photosAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { PhotoAdmin } from "@/types/admin";

const schema = z.object({
  s3_key: z.string().min(1, "Required"),
  source: z.string().min(1, "Required"),
  credit: z.string(),
  license: z.string(),
  alt_text: z.string(),
  caption: z.string(),
  is_primary: z.boolean(),
  sort_order: z.string(),
});

type FormValues = z.infer<typeof schema>;

interface PhotoFormDialogProps {
  spotId: number;
  photo?: PhotoAdmin;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function PhotoFormDialog({ spotId, photo, open, onOpenChange }: PhotoFormDialogProps) {
  const createMutation = photosAdminHooks.useCreate();
  const updateMutation = photosAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      s3_key: "", source: "", credit: "", license: "", alt_text: "", caption: "",
      is_primary: false, sort_order: "0",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        s3_key: photo?.s3_key ?? "",
        source: photo?.source ?? "",
        credit: photo?.credit ?? "",
        license: photo?.license ?? "",
        alt_text: photo?.alt_text ?? "",
        caption: photo?.caption ?? "",
        is_primary: photo?.is_primary ?? false,
        sort_order: String(photo?.sort_order ?? 0),
      });
    }
  }, [open, photo, form]);

  async function onSubmit(values: FormValues) {
    const payload = { ...values, sort_order: Number(values.sort_order) || 0 };
    try {
      if (photo) {
        await updateMutation.mutateAsync({ id: photo.id, payload });
        toast.success("Photo updated.");
      } else {
        await createMutation.mutateAsync({ ...payload, spot: spotId });
        toast.success("Photo added.");
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
          <DialogTitle>{photo ? "Edit photo" : "New photo"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField control={form.control} name="s3_key" render={({ field }) => (
              <FormItem>
                <FormLabel>Image path / URL</FormLabel>
                <FormControl><Input placeholder="/images/parks/example.jpg" {...field} /></FormControl>
                <FormDescription>No upload yet — paste a path or URL the site can already serve.</FormDescription>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="source" render={({ field }) => (
              <FormItem><FormLabel>Source</FormLabel><FormControl><Input placeholder="nps.gov" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="credit" render={({ field }) => (
              <FormItem><FormLabel>Credit</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="license" render={({ field }) => (
              <FormItem><FormLabel>License</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="alt_text" render={({ field }) => (
              <FormItem><FormLabel>Alt text</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="caption" render={({ field }) => (
              <FormItem><FormLabel>Caption</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="sort_order" render={({ field }) => (
                <FormItem><FormLabel>Sort order</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="is_primary" render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Primary photo</FormLabel>
                  <FormControl><Switch checked={field.value} onCheckedChange={field.onChange} /></FormControl>
                </FormItem>
              )} />
            </div>
            <DialogFooter>
              <Button type="submit" disabled={isPending}>{photo ? "Save changes" : "Add photo"}</Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
