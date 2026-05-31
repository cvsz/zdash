# zDash High-Risk Route Policy Matrix

| Route area | Risk class | Auth | RBAC | Tenant scope | Dry-run default | Typed confirmation | Audit event | Rollback path | Status |
|---|---|---|---|---|---|---|---|---|---|
| `/api/trading/*` | trading_order | required | admin/operator | required | yes | required for real mode | required | halt/disable strategy | verify |
| `/api/ai-trader/*` | ai_trader_signal | required | operator | required | yes | required for paper/live mode | required | disable strategy | verify |
| `/api/iot/*` | iot_power | required | admin/operator | required | yes | required | required | device safe-state | verify |
| `/api/content/post` | social_publish | required | editor/admin | required | yes | required | required | delete/unpublish plan | verify |
| `/api/marketplace/*/run` | plugin_execute | required | admin | required | yes | required | required | disable plugin | verify |
| `/api/enterprise/exports` | export_bundle | required | admin | required | yes | required if data included | required | revoke/delete bundle | verify |
| `/api/developer/api-keys` | credential_issue | required | admin/developer | required | no secret display | required | required | revoke key | verify |
| `/api/billing/*` | billing_mutation | required | admin/billing | required | provider mock unless configured | required for paid provider | required | cancel/refund path | verify |
| `/api/admin/users*` | user_admin | required | admin | required | n/a | required for delete | required | restore/recreate user | verify |
| `/api/launch/docs/publish` | docs_publish | required | admin/release | required | yes | required | required | revert published docs | verify |
