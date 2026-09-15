# SSM Parameter Store

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "secret_names" {
  type = list(string)
  default = [
    "DJANGO_SECRET_KEY",
    "POSTGRES_PASSWORD",
    "NPS_API_KEY",
    "RIDB_API_KEY",
    "RESEND_API_KEY",
    "ANTHROPIC_API_KEY",
    "SENTRY_DSN",
  ]
}
