"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { siteSettingsAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { SiteSettingsAdmin } from "@/types/admin";

const schema = z.object({
  site_name: z.string().min(1, "Required"),
  tagline: z.string(),
  logo_url: z.string(),
  twitter_url: z.string(),
  instagram_url: z.string(),
  contact_email: z.string(),
});

type FormValues = z.infer<typeof schema>;

export default function SiteSettingsForm({ settings }: { settings?: SiteSettingsAdmin }) {
  const createMutation = siteSettingsAdminHooks.useCreate();
  const updateMutation = siteSettingsAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      site_name: settings?.site_name ?? "Roadfare",
      tagline: settings?.tagline ?? "",
      logo_url: settings?.logo_url ?? "",
      twitter_url: settings?.twitter_url ?? "",
      instagram_url: settings?.instagram_url ?? "",
      contact_email: settings?.contact_email ?? "",
    },
  });

  async function onSubmit(values: FormValues) {
    try {
      if (settings) {
        await updateMutation.mutateAsync({ id: settings.id, payload: values });
      } else {
        await createMutation.mutateAsync(values);
      }
      toast.success("Site settings saved.");
    } catch (error) {
      toast.error(error instanceof ApiError ? String(error.detail) : "Something went wrong.");
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  const fields: { name: keyof FormValues; label: string }[] = [
    { name: "site_name", label: "Site name" },
    { name: "tagline", label: "Tagline" },
    { name: "logo_url", label: "Logo URL" },
    { name: "twitter_url", label: "Twitter URL" },
    { name: "instagram_url", label: "Instagram URL" },
    { name: "contact_email", label: "Contact email" },
  ];

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="max-w-xl space-y-4">
        {fields.map(({ name, label }) => (
          <FormField
            key={name}
            control={form.control}
            name={name}
            render={({ field }) => (
              <FormItem>
                <FormLabel>{label}</FormLabel>
                <FormControl>
                  <Input {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        ))}
        <Button type="submit" disabled={isPending}>
          Save
        </Button>
      </form>
    </Form>
  );
}
