"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { spotsAdminHooks, statesAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { SpotAdmin } from "@/types/admin";

const SPOT_TYPES = ["national_park", "state_park", "monument", "forest", "other"] as const;

const schema = z.object({
  name: z.string().min(1, "Required"),
  slug: z.string().min(1, "Required").regex(/^[a-z0-9-]+$/, "Lowercase letters, numbers, and hyphens only"),
  state: z.string().min(1, "Required"),
  type: z.enum(SPOT_TYPES),
  min_days: z.string(),
  vibe_tags_text: z.string(),
  blurb: z.string(),
  highlights: z.string(),
  elevation_ft: z.string(),
  best_time_to_visit: z.string(),
  meta_title: z.string().max(70, "70 characters max"),
  meta_description: z.string().max(160, "160 characters max"),
  latitude: z.string(),
  longitude: z.string(),
  nearest_airports_text: z.string(),
  contact_phone: z.string(),
  source_url: z.string(),
  verified_at: z.string(),
  is_manually_verified: z.boolean(),
  needs_verification: z.boolean(),
});

type FormValues = z.infer<typeof schema>;

export default function SpotForm({ spot }: { spot?: SpotAdmin }) {
  const router = useRouter();
  const { data: states } = statesAdminHooks.useList();
  const createMutation = spotsAdminHooks.useCreate();
  const updateMutation = spotsAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: spot?.name ?? "",
      slug: spot?.slug ?? "",
      state: spot?.state ? String(spot.state) : "",
      type: spot?.type ?? "national_park",
      min_days: String(spot?.min_days ?? 2),
      vibe_tags_text: spot?.vibe_tags?.join(", ") ?? "",
      blurb: spot?.blurb ?? "",
      highlights: spot?.highlights ?? "",
      elevation_ft: spot?.elevation_ft != null ? String(spot.elevation_ft) : "",
      best_time_to_visit: spot?.best_time_to_visit ?? "",
      meta_title: spot?.meta_title ?? "",
      meta_description: spot?.meta_description ?? "",
      latitude: spot?.latitude != null ? String(spot.latitude) : "",
      longitude: spot?.longitude != null ? String(spot.longitude) : "",
      nearest_airports_text: spot?.nearest_airports?.join(", ") ?? "",
      contact_phone: spot?.contact_phone ?? "",
      source_url: spot?.source_url ?? "",
      verified_at: spot?.verified_at ?? "",
      is_manually_verified: spot?.is_manually_verified ?? false,
      needs_verification: spot?.needs_verification ?? false,
    },
  });

  async function onSubmit(values: FormValues) {
    const payload = {
      name: values.name,
      slug: values.slug,
      state: Number(values.state),
      type: values.type as SpotAdmin["type"],
      min_days: Number(values.min_days) || 1,
      vibe_tags: values.vibe_tags_text.split(",").map((s) => s.trim()).filter(Boolean),
      blurb: values.blurb,
      highlights: values.highlights,
      elevation_ft: values.elevation_ft === "" ? null : Number(values.elevation_ft),
      best_time_to_visit: values.best_time_to_visit,
      meta_title: values.meta_title,
      meta_description: values.meta_description,
      latitude: Number(values.latitude),
      longitude: Number(values.longitude),
      nearest_airports: values.nearest_airports_text
        .split(",")
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean),
      contact_phone: values.contact_phone,
      source_url: values.source_url,
      verified_at: values.verified_at === "" ? null : values.verified_at,
      is_manually_verified: values.is_manually_verified,
      needs_verification: values.needs_verification,
    };

    try {
      if (spot) {
        await updateMutation.mutateAsync({ id: spot.slug, payload });
        toast.success("Spot updated.");
      } else {
        const created = await createMutation.mutateAsync(payload);
        toast.success("Spot created.");
        router.push(`/dashboard/spots/${created.slug}`);
      }
    } catch (error) {
      toast.error(error instanceof ApiError ? String(error.detail) : "Something went wrong.");
    }
  }

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="max-w-2xl space-y-6">
        <Tabs defaultValue="basic">
          <TabsList>
            <TabsTrigger value="basic">Basic</TabsTrigger>
            <TabsTrigger value="content">Content</TabsTrigger>
            <TabsTrigger value="seo">SEO</TabsTrigger>
            <TabsTrigger value="location">Location</TabsTrigger>
            <TabsTrigger value="verification">Verification</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-4">
            <FormField control={form.control} name="name" render={({ field }) => (
              <FormItem><FormLabel>Name</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="slug" render={({ field }) => (
              <FormItem><FormLabel>Slug</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="state" render={({ field }) => (
              <FormItem>
                <FormLabel>State</FormLabel>
                <Select value={field.value} onValueChange={field.onChange}>
                  <FormControl><SelectTrigger><SelectValue placeholder="Select a state" /></SelectTrigger></FormControl>
                  <SelectContent>
                    {states?.results.map((state) => (
                      <SelectItem key={state.id} value={String(state.id)}>{state.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="type" render={({ field }) => (
              <FormItem>
                <FormLabel>Type</FormLabel>
                <Select value={field.value} onValueChange={field.onChange}>
                  <FormControl><SelectTrigger><SelectValue /></SelectTrigger></FormControl>
                  <SelectContent>
                    {SPOT_TYPES.map((type) => (
                      <SelectItem key={type} value={type}>{type.replace("_", " ")}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="min_days" render={({ field }) => (
              <FormItem><FormLabel>Minimum days</FormLabel><FormControl><Input type="number" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="vibe_tags_text" render={({ field }) => (
              <FormItem>
                <FormLabel>Vibe tags</FormLabel>
                <FormControl><Input placeholder="scenic, family-friendly, remote" {...field} /></FormControl>
                <FormDescription>Comma-separated.</FormDescription>
                <FormMessage />
              </FormItem>
            )} />
          </TabsContent>

          <TabsContent value="content" className="space-y-4">
            <FormField control={form.control} name="blurb" render={({ field }) => (
              <FormItem><FormLabel>Blurb</FormLabel><FormControl><Textarea rows={4} {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="highlights" render={({ field }) => (
              <FormItem><FormLabel>Highlights</FormLabel><FormControl><Textarea rows={4} {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="elevation_ft" render={({ field }) => (
              <FormItem><FormLabel>Elevation (ft)</FormLabel><FormControl><Input type="number" {...field} value={field.value ?? ""} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="best_time_to_visit" render={({ field }) => (
              <FormItem><FormLabel>Best time to visit</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
          </TabsContent>

          <TabsContent value="seo" className="space-y-4">
            <FormField control={form.control} name="meta_title" render={({ field }) => (
              <FormItem>
                <FormLabel>Meta title</FormLabel>
                <FormControl><Input {...field} /></FormControl>
                <FormDescription>{field.value.length}/70 characters</FormDescription>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="meta_description" render={({ field }) => (
              <FormItem>
                <FormLabel>Meta description</FormLabel>
                <FormControl><Textarea rows={3} {...field} /></FormControl>
                <FormDescription>{field.value.length}/160 characters</FormDescription>
                <FormMessage />
              </FormItem>
            )} />
          </TabsContent>

          <TabsContent value="location" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <FormField control={form.control} name="latitude" render={({ field }) => (
                <FormItem><FormLabel>Latitude</FormLabel><FormControl><Input type="number" step="any" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
              <FormField control={form.control} name="longitude" render={({ field }) => (
                <FormItem><FormLabel>Longitude</FormLabel><FormControl><Input type="number" step="any" {...field} /></FormControl><FormMessage /></FormItem>
              )} />
            </div>
            <FormField control={form.control} name="nearest_airports_text" render={({ field }) => (
              <FormItem>
                <FormLabel>Nearest airports</FormLabel>
                <FormControl><Input placeholder="JAC, SLC" {...field} /></FormControl>
                <FormDescription>Comma-separated IATA codes.</FormDescription>
                <FormMessage />
              </FormItem>
            )} />
            <FormField control={form.control} name="contact_phone" render={({ field }) => (
              <FormItem><FormLabel>Contact phone</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
          </TabsContent>

          <TabsContent value="verification" className="space-y-4">
            <FormField control={form.control} name="source_url" render={({ field }) => (
              <FormItem><FormLabel>Source URL</FormLabel><FormControl><Input {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="verified_at" render={({ field }) => (
              <FormItem><FormLabel>Verified at</FormLabel><FormControl><Input type="date" {...field} /></FormControl><FormMessage /></FormItem>
            )} />
            <FormField control={form.control} name="is_manually_verified" render={({ field }) => (
              <FormItem className="flex items-center justify-between">
                <FormLabel>Manually verified</FormLabel>
                <FormControl><Switch checked={field.value} onCheckedChange={field.onChange} /></FormControl>
              </FormItem>
            )} />
            <FormField control={form.control} name="needs_verification" render={({ field }) => (
              <FormItem className="flex items-center justify-between">
                <FormLabel>Needs verification</FormLabel>
                <FormControl><Switch checked={field.value} onCheckedChange={field.onChange} /></FormControl>
              </FormItem>
            )} />
          </TabsContent>
        </Tabs>

        <Button type="submit" disabled={isPending}>
          {spot ? "Save changes" : "Create spot"}
        </Button>
      </form>
    </Form>
  );
}
