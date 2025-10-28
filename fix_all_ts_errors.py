#!/usr/bin/env python3
"""
YAGO v7.1 - Automatic TypeScript Error Fixer
Fixes all common TypeScript errors in the frontend
"""

import re
from pathlib import Path

def fix_file(filepath: Path, fixes: list):
    """Apply fixes to a file"""
    content = filepath.read_text()
    original = content

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if content != original:
        filepath.write_text(content)
        print(f"✅ Fixed: {filepath.name}")
        return True
    return False

def main():
    frontend_dir = Path("yago/web/frontend/src")

    # Common fixes for all files
    common_fixes = [
        # Remove unused projectId from destructuring
        (r'({[^}]*)\s*projectId,\s*([^}]*})', r'\1\2'),
        # Fix import type for enums
        (r'import type \{([^}]*)(AgentType|MessageType|MessagePriority|AgentStatus|ConflictStatus|ConflictType|BenchmarkStatus|BenchmarkType)([^}]*)\}',
         r'import type {\1\3}\nimport { \2 }'),
    ]

    # Specific file fixes
    specific_fixes = {
        "services/collaborationApi.ts": [
            (r'import type \{', r'import {'),
        ],
        "components/CollaborationDashboard.tsx": [
            (r'import type \{ Agent, AgentMessage, AgentType, MessageType \}',
             r'import type { Agent, AgentMessage }\nimport { AgentType, MessageType }'),
        ],
        "components/BenchmarkDashboard.tsx": [
            (r'intervalId: NodeJS\.Timeout', r'intervalId: number'),
        ],
    }

    # Fix Cost types - add missing properties
    cost_types_file = frontend_dir / "types" / "cost.ts"
    if cost_types_file.exists():
        content = cost_types_file.read_text()

        # Add has_budget and other missing properties to BudgetStatus
        if 'export interface BudgetStatus' in content:
            budget_status = '''export interface BudgetStatus {
  has_budget: boolean;
  budget_limit: number;
  current_spent: number;
  percentage_used: number;
  remaining: number;
  projected_total: number;
  days_remaining: number;
  estimated_completion_date: string;
  is_over_budget: boolean;
  will_exceed_budget: boolean;
}'''
            content = re.sub(
                r'export interface BudgetStatus \{[^}]*\}',
                budget_status,
                content,
                flags=re.DOTALL
            )
            cost_types_file.write_text(content)
            print("✅ Fixed: cost.ts BudgetStatus interface")

    # Process all TypeScript files
    for ts_file in frontend_dir.rglob("*.ts*"):
        if ts_file.suffix in ['.ts', '.tsx'] and 'node_modules' not in str(ts_file):
            # Apply common fixes
            fixed = fix_file(ts_file, common_fixes)

            # Apply specific fixes
            rel_path = str(ts_file.relative_to(frontend_dir))
            if rel_path in specific_fixes:
                fix_file(ts_file, specific_fixes[rel_path])

    print("\n✅ All TypeScript errors fixed!")
    print("📊 Run 'npm run build' to verify")

if __name__ == "__main__":
    main()
