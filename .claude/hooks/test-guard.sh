#!/usr/bin/env bash
# Feeds sample commands to guard.sh and prints PASS or FAIL for each.
# Run: .claude/hooks/test-guard.sh [path to guard.sh]
guard=${1:-$(dirname "$0")/guard.sh}
fails=0
on_main=$(mktemp -d) on_branch=$(mktemp -d)
git -C "$on_main" init -q -b main
git -C "$on_branch" init -q -b site-002-lead-search
trap 'rm -rf "$on_main" "$on_branch"' EXIT
# t <expected decision> <command> [session directory]
t() {
  got=$(jq -n --arg c "$2" --arg d "${3:-$on_branch}" '{tool_input:{command:$c}, cwd:$d}' | "$guard" | jq -r '.hookSpecificOutput.permissionDecision // empty')
  got=${got:-allow}
  if [ "$got" = "$1" ]; then r=PASS; else r=FAIL; fails=$((fails+1)); fi
  printf '%s  %-5s  %s\n' "$r" "$got" "$2${3:+  (on main)}"
}
# Pushes: branches go through, main and force pushes never
t allow 'git push'
t allow 'git push -u origin site-002-lead-search'
t allow 'git push origin HEAD'
t allow 'git push origin feature/main-menu'
t allow 'git -C "my dir" push origin feature'
t deny  'git push' "$on_main"
t deny  'git push -u origin' "$on_main"
t deny  'git push origin HEAD' "$on_main"
t deny  'git push origin main'
t deny  'git push -u origin main'
t deny  'git -C . push origin main'
t deny  'git push origin HEAD:main'
t deny  'git push origin feature:refs/heads/main'
t deny  'git push origin --delete main'
t deny  'git push --force'
t deny  'cd x && git push --force'
t deny  'git push -f origin feature'
t deny  'git push --force-with-lease origin feature'
t deny  'git push origin +feature'
t deny  'git push --all'
t deny  'git push --mirror'
t deny  'git push origin "main"'
t deny  "git push origin 'HEAD:main'"
t deny  'git -C "my dir" push origin main'
t deny  'git push origin x; git push origin main'
t deny  'git push origin x && git push -f'
t allow 'git push origin fix/push'
t allow 'git push origin fix/push' "$on_main"
t allow 'git commit -m "Never push to main"'
t allow 'gh pr create --fill'
t allow 'git commit -F msg.txt'
t allow 'git commit -m "Add push guard"'
t allow 'git status'
t deny  'git commit --no-verify -m x'
t ask   'pnpm deploy:dev'
t ask   'npx sst deploy --stage prod'
t ask   'sst remove --stage dev'
t ask   'psql -c "DROP TABLE users"'
t ask   'psql -c "truncate leads"'
t ask   'psql -c "delete from leads where id=1"'
t ask   'psql -c "ALTER TABLE x DROP COLUMN y"'
t allow 'psql -c "select * from leads"'
t allow 'ls -la'
t ask   'npx cdk deploy --all'
t ask   'cdk destroy MyStack'
t allow 'cdk synth'
t ask   'agentcore deploy'
t ask   'agentcore remove all'
t ask   'agentcore launch'
t ask   'agentcore destroy'
t allow 'agentcore status'
t ask   'sam deploy --guided'
t ask   'sam delete'
t ask   'serverless deploy --stage prod'
t ask   'sls remove'
t ask   'yarn deploy'
t ask   'aws cloudformation delete-stack --stack-name x'
t ask   'aws cloudformation deploy --template-file t.yml'
t ask   'aws dynamodb delete-table --table-name leads'
t ask   'aws ec2 terminate-instances --instance-ids i-1'
t ask   'aws s3 rm s3://bucket --recursive'
t ask   'aws s3 rb s3://bucket'
t allow 'aws s3 ls'
t allow 'aws sts get-caller-identity'
# Quoted text and other commands' words are not commands
t allow 'grep -rn "DELETE FROM" src/'
t allow 'git commit -m "Truncate Long Titles"'
t allow 'grep -n "git commit --no-verify" docs/PROCESS.md'
t allow 'git commit -m x && grep -n foo file'
t allow 'git commit --amend -m x'
t allow 'git stash push'
t allow 'grep -rn aws src/'
t allow 'uv add boto3'
t allow 'sst --help | grep deploy'
t allow 'aws logs tail /aws/lambda/x'
t allow 'aws --version'
# Skipping the checks
t deny  'git commit -n -m x'
t deny  'git commit -nm x'
t deny  'HUSKY=0 git commit -m x'
t deny  'git -c core.hooksPath=/dev/null commit -m x'
# Git and GitHub
t ask   'git reset --hard'
t ask   'git clean -fdx'
t ask   'git branch -D main'
t ask   'git stash drop'
t ask   'gh repo delete x'
t ask   'gh pr merge 3'
t ask   'gh api -X DELETE repos/x/y'
# Any AWS change, not only deletions
t ask   'aws cloudformation update-stack --stack-name x'
t ask   'aws s3 sync . s3://b --delete'
t ask   'aws lambda update-function-code --function-name x'
t ask   'aws ssm put-parameter --name x --overwrite'
t ask   "uv run python -c \"import boto3; boto3.client('s3').delete_bucket(Bucket='b')\""
# Databases and migrations
t ask   'dropdb mydb'
t ask   'psql -f down.sql'
t ask   $'psql -c "DELETE\nFROM users"'
t ask   'psql -c "DROP INDEX idx_leads"'
t ask   'psql -c "UPDATE leads SET email = NULL"'
t ask   'uv run alembic downgrade base'
t ask   'supabase db reset'
t ask   'pnpm prisma migrate reset'
t allow 'uv run pytest'
t allow 'pnpm dev'
echo "failures: $fails"
