#!/bin/bash
# YAGO v7.1 - TypeScript Error Fixer
# Automatically fixes common TypeScript errors

echo "🔧 Fixing TypeScript errors..."

# Fix MessageFlow.tsx
echo "📝 Fixing MessageFlow.tsx..."
sed -i '' 's/import type { AgentMessage, AgentType, MessageType, MessagePriority }/import type { AgentMessage }\nimport { AgentType, MessageType, MessagePriority }/' yago/web/frontend/src/components/MessageFlow.tsx

# Fix CollaborationDashboard.tsx
echo "📝 Fixing CollaborationDashboard.tsx..."
sed -i '' 's/import type { Agent, AgentMessage, AgentType, MessageType }/import type { Agent, AgentMessage }\nimport { AgentType, MessageType }/' yago/web/frontend/src/components/CollaborationDashboard.tsx

# Fix collaborationApi.ts
echo "📝 Fixing collaborationApi.ts..."
sed -i '' 's/import type {/import {/' yago/web/frontend/src/services/collaborationApi.ts

echo "✅ TypeScript fixes applied!"
echo "📊 Running build to check..."

cd yago/web/frontend && npm run build
