package agents.website_manager

default allow_actions = {}
default approval_required = {}

allow_actions = {
  "sites.list",
  "sites.get",
  "lists.list",
  "lists.get",
  "lists.items",
  "lists.create_item",
  "files.list",
  "files.get",
  "files.search",
  "files.create_folder",
  "files.upload",
  "files.share",
}
