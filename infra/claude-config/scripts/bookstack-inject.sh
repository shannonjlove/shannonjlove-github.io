#!/usr/bin/env bash
# SessionStart hook — fetches BookStack books and injects them into Claude's context

RESULT=$(curl -sf \
  -H "Authorization: Token ${BOOKSTACK_TOKEN_ID}:${BOOKSTACK_TOKEN_SECRET}" \
  "${BOOKSTACK_URL}/api/books?count=50" 2>/dev/null) || exit 0

[ -z "$RESULT" ] && exit 0

echo "$RESULT" | jq -r '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: (
      "=== SJL BookStack Knowledge Base ===\n" +
      "URL: \(env.BOOKSTACK_URL)\n" +
      "Auth: Token \(env.BOOKSTACK_TOKEN_ID):\(env.BOOKSTACK_TOKEN_SECRET)\n\n" +
      "Books:\n" +
      ([.data[] | "  - \(.name) [id:\(.id)]"] | join("\n")) +
      "\n\nTo fetch a book'\''s chapters: GET \(env.BOOKSTACK_URL)/api/books/{id}\n" +
      "To fetch a page: GET \(env.BOOKSTACK_URL)/api/pages/{id}\n" +
      "To search: GET \(env.BOOKSTACK_URL)/api/search?query={term}"
    )
  }
}'
