package agents.website_manager

default allow_actions = {}
default approval_required = {}

allow_actions = {
  "deployment.preview",
  "deployment.production",
  "content.update",
  "content.create",
  "analytics.read",
  "seo.update",
}

approval_required = {"deployment.production"}
