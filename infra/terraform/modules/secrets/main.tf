# SSM Parameter Store secrets
#
# Placeholder values only — never hardcode a real secret in Terraform state. Fill in
# real values after apply with, e.g.:
#   aws ssm put-parameter --name /roadfare/staging/DJANGO_SECRET_KEY --type SecureString \
#     --value "..." --overwrite

resource "aws_ssm_parameter" "this" {
  for_each = toset(var.secret_names)

  name  = "/${var.project}/${var.environment}/${each.value}"
  type  = "SecureString"
  value = "REPLACE_ME"

  lifecycle {
    ignore_changes = [value]
  }

  tags = { Name = "${var.project}-${var.environment}-${each.value}" }
}
