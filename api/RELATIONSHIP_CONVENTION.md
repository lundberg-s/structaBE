# Relationship Model Convention

## Design Principle: Source → Role → Target

The `Relation` model follows a consistent convention to eliminate ambiguity in relationship direction.

### Core Rules:

1. **Source**: The entity that "owns" or "initiates" the relationship
2. **Role**: Describes the relationship FROM the source's perspective TO the target
3. **Target**: The entity that the relationship is "to"

### Key Principle:
**The role reflects the SOURCE's perspective** - think "What is the source's role in relation to the target?"

## Examples

### Person → Organization Relationships

| Source | Role | Target | Meaning |
|--------|------|--------|---------|
| Person | "Employee Of" | Organization | Person's perspective: "I am an employee of this org" |
| Person | "Contact For" | Organization | Person's perspective: "I am a contact for this org" |
| Person | "Decision Maker For" | Organization | Person's perspective: "I am a decision maker for this org" |
| Person | "Technical Contact For" | Organization | Person's perspective: "I am the technical contact for this org" |

### Person → Person Relationships

| Source | Role | Target | Meaning |
|--------|------|--------|---------|
| Person | "Reports To" | Person | Source's perspective: "I report to this person" |
| Person | "Manages" | Person | Source's perspective: "I manage this person" |
| Person | "Colleague Of" | Person | Source's perspective: "I am a colleague of this person" |

### Person → WorkItem Relationships

| Source | Role | Target | Meaning |
|--------|------|--------|---------|
| Person | "Assigned To" | WorkItem | Person's perspective: "I am assigned to this work item" |
| Person | "Reviewer Of" | WorkItem | Person's perspective: "I am a reviewer of this work item" |
| Person | "Stakeholder For" | WorkItem | Person's perspective: "I am a stakeholder for this work item" |

### WorkItem → WorkItem Relationships

| Source | Role | Target | Meaning |
|--------|------|--------|---------|
| WorkItem | "Depends On" | WorkItem | Source's perspective: "I depend on this other work item" |
| WorkItem | "Blocks" | WorkItem | Source's perspective: "I block this other work item" |
| WorkItem | "Related To" | WorkItem | Source's perspective: "I am related to this other work item" |
| WorkItem | "Duplicate Of" | WorkItem | Source's perspective: "I am a duplicate of this other work item" |

### Organization → Organization Relationships

| Source | Role | Target | Meaning |
|--------|------|--------|---------|
| Organization | "Parent Of" | Organization | Source's perspective: "I am the parent of this org" |
| Organization | "Subsidiary Of" | Organization | Source's perspective: "I am a subsidiary of this org" |
| Organization | "Partner Of" | Organization | Source's perspective: "I am a partner of this org" |

## Role Naming Guidelines

### ✅ Good Role Names (Source's Perspective)
- "Employee Of" (not "Employer Of")
- "Contact For" (not "Contact Of")
- "Assigned To" (not "Assigned From")
- "Depends On" (not "Required By")
- "Reports To" (not "Manager Of")
- "Parent Of" (not "Child Of")

### ❌ Avoid These Patterns
- "Contact" (ambiguous - whose perspective?)
- "Manager" (ambiguous - who manages whom?)
- "Related" (too vague)
- "Connected" (too vague)

## Implementation in Code

```python
# Creating a relationship
relation = Relation.objects.create(
    tenant=tenant,
    source_type='partner',
    source_partner=person,  # Sandi Lundberg
    target_type='partner', 
    target_partner=organization,  # My Company
    role=role,  # "Employee Of"
)

# Reading the relationship
print(relation.get_relationship_description())
# Output: "Sandi Lundberg is Employee Of My Company"

print(relation)
# Output: "Sandi Lundberg → Employee Of → My Company"
```

## Querying Relationships

```python
# Find all people who are employees of an organization
employees = Relation.objects.filter(
    source_type='partner',
    target_type='partner',
    target_partner=organization,
    role__label='Employee Of'
)

# Find all work items that depend on a specific work item
dependencies = Relation.objects.filter(
    source_type='workitem',
    target_type='workitem',
    target_workitem=work_item,
    role__label='Depends On'
)

# Find all relationships where a person is the source
person_relationships = Relation.objects.filter(
    source_type='partner',
    source_partner=person
)
```

## Benefits of This Convention

1. **No Ambiguity**: Clear direction from source to target
2. **Consistent**: Same pattern for all relationship types
3. **Intuitive**: Role describes what the source "is" in relation to the target
4. **Queryable**: Easy to find relationships from any entity's perspective
5. **Extensible**: New role types can be added without changing the model structure

## Migration Strategy

When migrating existing data or creating new relationships:

1. **Identify the source**: Who "owns" or "initiates" this relationship?
2. **Identify the target**: Who is this relationship "to"?
3. **Choose the role**: What is the source's role in relation to the target?
4. **Use the source's perspective**: Frame the role from the source's point of view 