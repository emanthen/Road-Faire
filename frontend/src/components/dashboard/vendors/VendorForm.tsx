"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { partnersAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { PartnerAdmin } from "@/types/admin";

const schema = z.object({
  name: z.string().min(1, "Required"),
  slug: z.string().min(1, "Required").regex(/^[a-z0-9-]+$/, "Lowercase letters, numbers, and hyphens only"),
  service_area: z.string(),
  contact_phone: z.string(),
  terms_note: z.string(),
  rating: z.string(),
  rating_count: z.string(),
  rating_source: z.string(),
  rating_url: z.string(),
  source_url: z.string(),
  is_manually_verified: z.boolean(),
  needs_verification: z.boolean(),
});

type FormValues = z.infer<typeof schema>;

export default function VendorForm({ vendor }: { vendor?: PartnerAdmin }) {
  const router = useRouter();
  const createMutation = partnersAdminHooks.useCreate();
  const updateMutation = partnersAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: vendor?.name ?? "",
      slug: vendor?.slug ?? "",
      service_area: vendor?.service_area ?? "",
      contact_phone: vendor?.contact_phone ?? "",
      terms_note: vendor?.terms_note ?? "",
      rating: vendor?.rating ?? "",
      rating_count: vendor?.rating_count != null ? String(vendor.rating_count) : "",
      rating_source: vendor?.rating_source ?? "",
      rating_url: vendor?.rating_url ?? "",
      source_url: vendor?.source_url ?? "",
      is_manually_verified: vendor?.is_manually_verified ?? false,
      needs_verification: vendor?.needs_verification ?? false,
    },
  });

  async function onSubmit(values: FormValues) {
    const payload = {
      ...values,
      rating_count: values.rating_count === "" ? null : Number(values.rating_count),
    };
    try {
      if (vendor) {
        await updateMutation.mutateAsync({ id: vendor.slug, payload });
        toast.success("Vendor updated.");
      } else {
        const created = await createMutation.mutateAsync(payload);
        toast.success("Vendor created.");
        router.push(`/dashboard/vendors/${created.slug}`);
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? String(error.detail) : "Something went wrong.");
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="max-w-2xl space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="slug"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Slug</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="service_area"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Service area</FormLabel>
              <FormControl>
                <Input placeholder="e.g. Chicago, IL" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="contact_phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Contact phone</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="terms_note"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Terms note</FormLabel>
              <FormControl>
                <Textarea rows={2} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="rounded-md border border-border p-4">
          <h2 className="font-medium">Rating</h2>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <FormField
              control={form.control}
              name="rating"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Rating (e.g. 4.5)</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="rating_count"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Rating count</FormLabel>
                  <FormControl>
                    <Input type="number" {...field} value={field.value ?? ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="rating_source"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Rating source</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g. Yelp" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="rating_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Rating URL</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        <div className="rounded-md border border-border p-4">
          <h2 className="font-medium">Verification</h2>
          <div className="mt-4 space-y-4">
            <FormField
              control={form.control}
              name="source_url"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Source URL</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="is_manually_verified"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Manually verified</FormLabel>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="needs_verification"
              render={({ field }) => (
                <FormItem className="flex items-center justify-between">
                  <FormLabel>Needs verification</FormLabel>
                  <FormControl>
                    <Switch checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                </FormItem>
              )}
            />
          </div>
        </div>

        <Button type="submit" disabled={isPending}>
          {vendor ? "Save changes" : "Create vendor"}
        </Button>
      </form>
    </Form>
  );
}
