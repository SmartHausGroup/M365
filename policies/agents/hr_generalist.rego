package agents.hr_generalist

default allow_actions = {}
default approval_required = {}

allow_actions = {
  "employee.onboard",
  "employee.update_info",
  "employee.offboard",
}

approval_required = {"employee.offboard"}
