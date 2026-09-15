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
import { Textarea } from "@/components/ui/textarea";
import { faqsAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { FAQAdmin } from "@/types/admin";

const schema = z.object({
  question: z.string().min(1, "Required"),
  answer: z.string().min(1, "Required"),
  order: z.string(),
});

type FormValues = z.infer<typeof schema>;

interface FAQFormDialogProps {
  faq?: FAQAdmin;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function FAQFormDialog({ faq, open, onOpenChange }: FAQFormDialogProps) {
  const createMutation = faqsAdminHooks.useCreate();
  const updateMutation = faqsAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { question: "", answer: "", order: "0" },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        question: faq?.question ?? "",
        answer: faq?.answer ?? "",
        order: String(faq?.order ?? 0),
      });
    }
  }, [open, faq, form]);

  async function onSubmit(values: FormValues) {
    const payload = { ...values, order: Number(values.order) || 0 };
    try {
      if (faq) {
        await updateMutation.mutateAsync({ id: faq.id, payload });
        toast.success("FAQ updated.");
      } else {
        await createMutation.mutateAsync(payload);
        toast.success("FAQ created.");
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
          <DialogTitle>{faq ? "Edit FAQ" : "New FAQ"}</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="question"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Question</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="answer"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Answer</FormLabel>
                  <FormControl>
                    <Textarea rows={4} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="order"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Order</FormLabel>
                  <FormControl>
                    <Input type="number" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter>
              <Button type="submit" disabled={isPending}>
                {faq ? "Save changes" : "Create FAQ"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
