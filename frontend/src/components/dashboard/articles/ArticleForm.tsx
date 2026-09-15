"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { pagesAdminHooks } from "@/hooks/admin";
import { ApiError } from "@/lib/api";
import type { PageAdmin } from "@/types/admin";

const schema = z.object({
  title: z.string().min(1, "Required"),
  slug: z
    .string()
    .min(1, "Required")
    .regex(/^[a-z0-9-]+$/, "Lowercase letters, numbers, and hyphens only"),
  body: z.string(),
  published: z.boolean(),
  meta_title: z.string().max(70, "70 characters max"),
  meta_description: z.string().max(160, "160 characters max"),
});

type FormValues = z.infer<typeof schema>;

export default function ArticleForm({ article }: { article?: PageAdmin }) {
  const router = useRouter();
  const createMutation = pagesAdminHooks.useCreate();
  const updateMutation = pagesAdminHooks.useUpdate();

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: article?.title ?? "",
      slug: article?.slug ?? "",
      body: article?.body ?? "",
      published: article?.published ?? false,
      meta_title: article?.meta_title ?? "",
      meta_description: article?.meta_description ?? "",
    },
  });

  async function onSubmit(values: FormValues) {
    try {
      if (article) {
        await updateMutation.mutateAsync({ id: article.slug, payload: values });
        toast.success("Article updated.");
      } else {
        await createMutation.mutateAsync(values);
        toast.success("Article created.");
        router.push("/dashboard/articles");
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
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Title</FormLabel>
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
              <FormDescription>Used in the URL, e.g. /guides/{field.value || "slug"}</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="body"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Body</FormLabel>
              <FormControl>
                <Textarea rows={12} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="published"
          render={({ field }) => (
            <FormItem className="flex items-center justify-between rounded-md border border-border p-3">
              <div>
                <FormLabel>Published</FormLabel>
                <FormDescription>Visible on the public site when on.</FormDescription>
              </div>
              <FormControl>
                <Switch checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="rounded-md border border-border p-4">
          <h2 className="font-medium">SEO</h2>
          <div className="mt-4 space-y-4">
            <FormField
              control={form.control}
              name="meta_title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Meta title</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>{field.value.length}/70 characters</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="meta_description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Meta description</FormLabel>
                  <FormControl>
                    <Textarea rows={3} {...field} />
                  </FormControl>
                  <FormDescription>{field.value.length}/160 characters</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>

        <Button type="submit" disabled={isPending}>
          {article ? "Save changes" : "Create article"}
        </Button>
      </form>
    </Form>
  );
}
