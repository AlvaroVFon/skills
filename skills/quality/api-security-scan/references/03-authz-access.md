# 03 — Authorization and Access (API1, API3, API5:2023 · A01:2025)

## Definition

An authenticated caller can read or change objects, properties, or functions that belong to someone else or to a higher role.

## Signals

| Signal                     | Probe                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------- |
| BOLA / IDOR (API1)         | `findById(req.params.id)` with no owner/tenant filter; ownership checked on read but not on update            |
| Tenant leak                | Query missing `tenantId`/`companyId`; filter built from a value the client controls                           |
| Mass assignment (API3)     | `Model.create(req.body)`, `Object.assign(doc, req.body)`, `$set: req.body`, spread into DTO without whitelist |
| Writable privileged fields | `role`, `isAdmin`, `ownerId`, `balance`, `verified`, `status` accepted from the body                          |
| BFLA (API5)                | Admin route without role check; role checked in UI only; `PUT`/`DELETE` lacks the check `GET` has             |
| Client-trusted identity    | `userId` taken from body/query/header instead of the verified token                                           |
| CSRF (A01)                 | Cookie-authenticated state-changing routes without CSRF token or `SameSite` (CWE-352)                         |
| Nested/indirect objects    | `/orders/:orderId/items/:itemId` checks the order but not that the item belongs to it                         |

## Mongoose / NestJS Traps

- `findOneAndUpdate({ _id: id }, req.body)` — both BOLA and mass assignment.
- Schemas without `strict` or DTOs without `whitelist: true, forbidNonWhitelisted: true` in `ValidationPipe`.
- `@Roles()` decorator present but `RolesGuard` not registered.

## Test to Confirm

Seed two users (A, B) with fixtures. As A, request B's object or send a body with a privileged field; assert 403/404 or that the field is ignored. A 2xx with B's data, or the field persisted, is the exploit.

## False-Positive Traps

- Ownership enforced in the repository/service layer or by a query scope plugin.
- Ids are unguessable **and** the route is still checked (unguessable alone is not a control — report as Low).
- The field is whitelisted by the DTO/serializer before reaching storage.
