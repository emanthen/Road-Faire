from apps.content.models import Page


def sitemap_entries() -> list[dict]:
    return [
        {"path": f"/guides/{page.slug}", "lastmod": page.updated_at.date().isoformat()}
        for page in Page.objects.filter(published=True)
    ]
