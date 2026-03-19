package agents.m365_administrator

default allow_actions = {}
default approval_required = {}

allow_actions = {
  "users.read",
  "users.create",
  "users.update",
  "users.disable",
  "groups.create",
  "groups.add_member",
  "teams.create",
  "teams.add_channel",
  "sites.provision",
  "licenses.assign",
}

approval_required = {"users.disable"}
