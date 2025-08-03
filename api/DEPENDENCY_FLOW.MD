Core Layer (Zero Dependencies)
├── AuditModel ✅
├── Tenant ✅
├── Role ✅
├── BaseOption ✅
└── AuditLog ✅

Authentication Layer (Minimal Dependencies)
└── User ✅ (only Django auth dependencies)

Business Layer (Clean Dependencies)
├── Partner (inherits AuditModel  + links to User) ✅
├── Person (inherits Partner) ✅
└── Organization (inherits Partner) ✅

Relationship Layer (Clean Dependencies)
├── Relation (inherits AuditModel) ✅
└── Assignment (inherits AuditModel) ✅

Work Management Layer (Clean Dependencies)
├── WorkItem (inherits AuditModel) ✅
├── Ticket/Case/Job (inherit WorkItem) ✅
├── Comment (inherits AuditModel) ✅
└── Attachment (inherits AuditModel) ✅