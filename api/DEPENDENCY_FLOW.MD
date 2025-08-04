Core Layer (Zero Dependencies)
├── AuditModel ✅
├── Tenant ✅
├── Role ✅
├── BaseOption ✅
└── AuditLog ✅

User (Authentication) Layer (Tenant)
└── User ✅ (only Django auth dependencies)

Partner Layer (Audit, Tenant, Role, User)
├── Partner (inherits AuditModel, FK to User) ✅
├── Person (inherits Partner) ✅
└── Organization (inherits Partner) ✅

Engagements Layer (Audit, Tenant, BaseOption)
├── WorkItem (inherits AuditModel) ✅
├── Ticket/Case/Job (inherit WorkItem) ✅
├── Comment (inherits AuditModel, FK to WorkItem) ✅
└── Attachment (inherits AuditModel, FK to WorkItem) ✅

Relationship Layer (Audit, Tenant, Role, Partner, Engagements)
├── Relation (inherits AuditModel, FK to WorkItem + Partner) ✅
└── Assignment (inherits AuditModel, FK to Relation) ✅