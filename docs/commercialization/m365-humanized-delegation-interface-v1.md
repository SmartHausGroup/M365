# M365 Humanized Delegation Interface v1

## Purpose

Define the bounded interface that lets operators target named digital employees with natural
phrases instead of raw agent IDs.

## Supported Requests

- `Talk to Elena Rodriguez`
- `Have Elena Rodriguez handle this`
- `Route this to Marcus in Operations`
- `Ask Elena Rodriguez to prepare the homepage draft`
- `Delegate this to Sarah Williams`

## Deterministic Rules

1. Parse the request against the machine-readable pattern registry.
2. Extract the persona target phrase and optional task hint.
3. Resolve the target against the authoritative persona registry.
4. If a department hint is present, require the resolved persona to match it.
5. If the target phrase is ambiguous, fail closed.

## Output Contract

The runtime returns:

- `canonical_agent`
- `persona`
- `matched_pattern`
- `normalized_target`
- `task_hint`

## No-Go Conditions

- natural-language delegation can resolve a non-authoritative overflow agent
- ambiguous short-name targeting silently picks one persona
- department hints are ignored
- task hints are dropped for supported `ask ... to ...` requests
