"""Known bot/crawler User-Agent signatures.

Used by apps.partners.views.go to flag Click rows rather than drop them — a bot hit is
still worth keeping in the audit trail, it just shouldn't count toward affiliate
click-through analytics.
"""

import re

# ponytail: a substring/regex list, not a maintained bot database (e.g. isbot/crawler-
# user-agents) — good enough to keep obvious crawlers and HTTP libraries out of the
# numbers; add a real bot-list dependency if false negatives start mattering.
BOT_USER_AGENT_PATTERN = re.compile(
    r"bot|crawl|spider|slurp|facebookexternalhit|preview|headless"
    r"|curl|wget|python-requests|python-urllib|go-http-client|axios"
    r"|libwww-perl|scrapy|monitor|pingdom|uptimerobot|ahrefs|semrush|mj12bot|petalbot",
    re.IGNORECASE,
)


def is_bot_user_agent(user_agent: str) -> bool:
    return bool(BOT_USER_AGENT_PATTERN.search(user_agent or ""))
