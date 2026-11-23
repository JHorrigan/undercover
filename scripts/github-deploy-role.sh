#!/usr/bin/env bash
# Creates the IAM role GitHub Actions assumes, through OIDC, to deploy one stage
# with SST, and stores its ARN and region as repository variables. The dev role
# trusts only this repo's pull requests; the production role only its main
# branch. So no AWS keys live in GitHub. Run once per stage, with the stage's
# account's credentials, from inside the repo, with the gh CLI signed in.
# Usage: AWS_PROFILE=<the stage's account> scripts/github-deploy-role.sh <stage>
set -euo pipefail

stage=${1:?usage: github-deploy-role.sh <stage>}
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
role="github-deploy-${repo#*/}-${stage}"
# GitHub names the repo in its tokens by this prefix, with or without immutable IDs.
subject=$(gh api "repos/${repo}/actions/oidc/customization/sub" -q .sub_claim_prefix)
if [ "$stage" = production ]; then
  claim="${subject}:ref:refs/heads/main"
else
  claim="${subject}:pull_request"
fi
account=$(aws sts get-caller-identity --query Account --output text)
region=$(aws configure get region || true)
[ -n "$region" ] || { echo "Set a region on the AWS profile first." >&2; exit 1; }
provider="arn:aws:iam::${account}:oidc-provider/token.actions.githubusercontent.com"

if ! aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$provider" >/dev/null 2>&1; then
  aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --client-id-list sts.amazonaws.com >/dev/null
fi

trust=$(cat <<JSON
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "${provider}" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "${claim}"
      }
    }
  }]
}
JSON
)

if aws iam get-role --role-name "$role" >/dev/null 2>&1; then
  aws iam update-assume-role-policy --role-name "$role" --policy-document "$trust"
else
  aws iam create-role --role-name "$role" --assume-role-policy-document "$trust" \
    --description "GitHub Actions deploys of ${repo}, stage ${stage}" >/dev/null
fi

# SST's documented deploy policy (its IAM credentials page) allows every action, so the trust policy above is the limit.
aws iam attach-role-policy --role-name "$role" \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

arn=$(aws iam get-role --role-name "$role" --query Role.Arn --output text)
upper=$(tr '[:lower:]' '[:upper:]' <<<"$stage")
gh variable set "AWS_DEPLOY_ROLE_${upper}" --body "$arn"
gh variable set "AWS_REGION_${upper}" --body "$region"
echo "$arn"
