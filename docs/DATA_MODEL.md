# Data Model

This document describes PatchHive's complete data model and database schema.

## Entity Relationship Diagram

```
┌──────────┐
│   User   │
└──────────┘
     │ 1
     │
     │ *
┌──────────┐      *   ┌──────────────┐   *      ┌────────┐
│   Rack   ├─────────>│ RackModule   ├<─────────┤ Module │
└──────────┘          └──────────────┘          └────────┘
     │ *                                              ▲
     │                                                │
     │ 1                                              │ *
┌──────────┐                                    ┌────────┐
│   Case   │                                    │  Case  │
└──────────┘                                    └────────┘
     │
     │ *
┌──────────┐
│  Patch   │
└──────────┘
     │ *
     ├────> Vote
     └────> Comment
```

## Entities

### User

Represents a registered user account.

**Table**: `users`

| Column       | Type         | Constraints                    | Description                      |
|--------------|--------------|--------------------------------|----------------------------------|
| id           | Integer      | PK, Auto                       | Unique identifier                |
| username     | String(50)   | Unique, Not Null, Indexed      | Username for login               |
| email        | String(255)  | Unique, Not Null, Indexed      | Email address                    |
| password_hash| String(255)  | Not Null                       | Bcrypt hashed password           |
| avatar_url   | String(500)  | Nullable                       | URL to profile avatar            |
| bio          | Text         | Nullable                       | User bio/description             |
| created_at   | DateTime     | Not Null, Default: UTC now     | Account creation timestamp       |
| updated_at   | DateTime     | Not Null, Default: UTC now     | Last update timestamp            |

**Relationships**:
- Has many `Rack` (via `user_id`)
- Has many `Vote` (via `user_id`)
- Has many `Comment` (via `user_id`)

---

### Module

Represents a Eurorack module with full specifications.

**Table**: `modules`

| Column           | Type         | Constraints                | Description                          |
|------------------|--------------|----------------------------|--------------------------------------|
| id               | Integer      | PK, Auto                   | Unique identifier                    |
| brand            | String(100)  | Not Null, Indexed          | Manufacturer brand                   |
| name             | String(200)  | Not Null, Indexed          | Module name                          |
| hp               | Integer      | Not Null                   | Width in HP units                    |
| module_type      | String(50)   | Not Null, Indexed          | VCO/VCF/VCA/ENV/LFO/SEQ/etc.         |
| power_12v_ma     | Integer      | Nullable                   | +12V power draw in mA                |
| power_neg12v_ma  | Integer      | Nullable                   | -12V power draw in mA                |
| power_5v_ma      | Integer      | Nullable                   | +5V power draw in mA                 |
| io_ports         | JSON         | Not Null, Default: []      | Array of I/O port specs              |
| tags             | JSON         | Not Null, Default: []      | Array of tags                        |
| description      | Text         | Nullable                   | Module description                   |
| manufacturer_url | String(500)  | Nullable                   | URL to manufacturer page             |
| source           | String(50)   | Not Null                   | Data source (Manual/CSV/ModularGrid) |
| source_reference | String(500)  | Nullable                   | Source reference (URL/filename)      |
| imported_at      | DateTime     | Not Null, Default: UTC now | Import timestamp                     |
| created_at       | DateTime     | Not Null, Default: UTC now | Creation timestamp                   |
| updated_at       | DateTime     | Not Null, Default: UTC now | Last update timestamp                |

**I/O Ports JSON Format**:
```json
[
  {
    "name": "CV In 1",
    "type": "cv_in"
  },
  {
    "name": "Audio Out",
    "type": "audio_out"
  }
]
```

**Port Types**: `audio_in`, `audio_out`, `cv_in`, `cv_out`, `gate_in`, `gate_out`, `clock_in`, `clock_out`

**Relationships**:
- Has many `RackModule` (via `module_id`)

---

### Case

Represents a Eurorack case with power and layout specifications.

**Table**: `cases`

| Column           | Type         | Constraints                | Description                     |
|------------------|--------------|----------------------------|---------------------------------|
| id               | Integer      | PK, Auto                   | Unique identifier               |
| brand            | String(100)  | Not Null, Indexed          | Manufacturer brand              |
| name             | String(200)  | Not Null, Indexed          | Case name                       |
| total_hp         | Integer      | Not Null                   | Total width in HP               |
| rows             | Integer      | Not Null, Default: 1       | Number of rows                  |
| hp_per_row       | JSON         | Not Null, Default: []      | HP per row (e.g., [84, 84])     |
| power_12v_ma     | Integer      | Nullable                   | +12V rail capacity in mA        |
| power_neg12v_ma  | Integer      | Nullable                   | -12V rail capacity in mA        |
| power_5v_ma      | Integer      | Nullable                   | +5V rail capacity in mA         |
| description      | Text         | Nullable                   | Case description                |
| manufacturer_url | String(500)  | Nullable                   | URL to manufacturer page        |
| meta             | JSON         | Nullable                   | Additional metadata             |
| source           | String(50)   | Not Null                   | Data source                     |
| source_reference | String(500)  | Nullable                   | Source reference                |
| created_at       | DateTime     | Not Null, Default: UTC now | Creation timestamp              |
| updated_at       | DateTime     | Not Null, Default: UTC now | Last update timestamp           |

**Relationships**:
- Has many `Rack` (via `case_id`)

---

### Rack

Represents a user's rack configuration (case + modules).

**Table**: `racks`

| Column          | Type         | Constraints                | Description                        |
|-----------------|--------------|----------------------------|------------------------------------|
| id              | Integer      | PK, Auto                   | Unique identifier                  |
| user_id         | Integer      | FK → users.id, Indexed     | Owner user                         |
| case_id         | Integer      | FK → cases.id, Indexed     | Associated case                    |
| name            | String(200)  | Not Null                   | Rack name (auto-generated or user) |
| description     | Text         | Nullable                   | Rack description                   |
| tags            | JSON         | Not Null, Default: []      | Array of tags                      |
| is_public       | Boolean      | Not Null, Default: False   | Public sharing flag                |
| generation_seed | Integer      | Nullable                   | Seed used for naming               |
| created_at      | DateTime     | Not Null, Default: UTC now | Creation timestamp                 |
| updated_at      | DateTime     | Not Null, Default: UTC now | Last update timestamp              |

**Relationships**:
- Belongs to `User` (via `user_id`)
- Belongs to `Case` (via `case_id`)
- Has many `RackModule` (via `rack_id`)
- Has many `Patch` (via `rack_id`)
- Has many `Vote` (via `rack_id`)
- Has many `Comment` (via `rack_id`)

---

### RackModule

Join table representing a module placed in a specific position within a rack.

**Table**: `rack_modules`

| Column     | Type    | Constraints                | Description                    |
|------------|---------|----------------------------|--------------------------------|
| id         | Integer | PK, Auto                   | Unique identifier              |
| rack_id    | Integer | FK → racks.id, Indexed     | Rack this module belongs to    |
| module_id  | Integer | FK → modules.id, Indexed   | Module being placed            |
| row_index  | Integer | Not Null                   | Row index (0-based)            |
| start_hp   | Integer | Not Null                   | Starting HP position (0-based) |

**Relationships**:
- Belongs to `Rack` (via `rack_id`)
- Belongs to `Module` (via `module_id`)

**Constraints**:
- No overlapping modules (validated in application logic)
- Module must fit within row HP capacity

---

### Patch

Represents a patch configuration (connection graph between modules).

**Table**: `patches`

| Column              | Type         | Constraints                | Description                           |
|---------------------|--------------|----------------------------|---------------------------------------|
| id                  | Integer      | PK, Auto                   | Unique identifier                     |
| rack_id             | Integer      | FK → racks.id, Indexed     | Rack this patch belongs to            |
| name                | String(200)  | Not Null                   | Patch name (auto-generated)           |
| category            | String(50)   | Not Null, Indexed          | Voice/Modulation/Clock-Rhythm/Generative/Utility/Performance Macro/Texture-FX/Study/Experimental-Feedback |
| description         | Text         | Nullable                   | Patch description                     |
| connections         | JSON         | Not Null, Default: []      | Connection graph                      |
| generation_seed     | Integer      | Not Null                   | Seed used for generation              |
| generation_version  | String(20)   | Not Null                   | Patch engine version                  |
| engine_config       | JSON         | Nullable                   | Engine configuration used             |
| waveform_svg_path   | String(500)  | Nullable                   | Path to waveform SVG                  |
| waveform_params     | JSON         | Nullable                   | Parameters for waveform generation    |
| is_public           | Boolean      | Not Null, Default: False   | Public sharing flag                   |
| created_at          | DateTime     | Not Null, Default: UTC now | Creation timestamp                    |
| updated_at          | DateTime     | Not Null, Default: UTC now | Last update timestamp                 |

**Connections JSON Format**:
```json
[
  {
    "from_module_id": 1,
    "from_port": "Audio Out",
    "to_module_id": 2,
    "to_port": "Audio In",
    "cable_type": "audio"
  }
]
```

**Cable Types**: `audio`, `cv`, `gate`, `clock`

**Relationships**:
- Belongs to `Rack` (via `rack_id`)
- Has many `Vote` (via `patch_id`)
- Has many `Comment` (via `patch_id`)

---

### Vote

Represents a vote/like on a rack or patch.

**Table**: `votes`

| Column     | Type     | Constraints                              | Description                |
|------------|----------|------------------------------------------|----------------------------|
| id         | Integer  | PK, Auto                                 | Unique identifier          |
| user_id    | Integer  | FK → users.id, Not Null                  | User who voted             |
| rack_id    | Integer  | FK → racks.id, Nullable                  | Rack being voted on        |
| patch_id   | Integer  | FK → patches.id, Nullable                | Patch being voted on       |
| created_at | DateTime | Not Null, Default: UTC now               | Vote timestamp             |

**Constraints**:
- Unique constraint: (`user_id`, `rack_id`)
- Unique constraint: (`user_id`, `patch_id`)
- Either `rack_id` OR `patch_id` must be set (not both)

**Relationships**:
- Belongs to `User` (via `user_id`)
- Belongs to `Rack` (via `rack_id`, optional)
- Belongs to `Patch` (via `patch_id`, optional)

---

### Comment

Represents a comment on a rack or patch.

**Table**: `comments`

| Column     | Type     | Constraints                | Description                |
|------------|----------|----------------------------|----------------------------|
| id         | Integer  | PK, Auto                   | Unique identifier          |
| user_id    | Integer  | FK → users.id, Not Null    | User who commented         |
| rack_id    | Integer  | FK → racks.id, Nullable    | Rack being commented on    |
| patch_id   | Integer  | FK → patches.id, Nullable  | Patch being commented on   |
| content    | Text     | Not Null                   | Comment text               |
| created_at | DateTime | Not Null, Default: UTC now | Creation timestamp         |
| updated_at | DateTime | Not Null, Default: UTC now | Last update timestamp      |

**Constraints**:
- Either `rack_id` OR `patch_id` must be set (not both)

**Relationships**:
- Belongs to `User` (via `user_id`)
- Belongs to `Rack` (via `rack_id`, optional)
- Belongs to `Patch` (via `patch_id`, optional)

---

## Indexes

For optimal query performance, the following indexes are created:

| Table        | Column(s)                 | Type    |
|--------------|---------------------------|---------|
| users        | username                  | Unique  |
| users        | email                     | Unique  |
| modules      | brand                     | Index   |
| modules      | name                      | Index   |
| modules      | module_type               | Index   |
| cases        | brand                     | Index   |
| cases        | name                      | Index   |
| racks        | user_id                   | Index   |
| racks        | case_id                   | Index   |
| rack_modules | rack_id                   | Index   |
| rack_modules | module_id                 | Index   |
| patches      | rack_id                   | Index   |
| patches      | category                  | Index   |
| votes        | (user_id, rack_id)        | Unique  |
| votes        | (user_id, patch_id)       | Unique  |

---

## Data Integrity

### Cascading Deletes

When a parent entity is deleted:
- **User deleted** → All owned racks, votes, comments deleted
- **Rack deleted** → All rack modules and patches deleted
- **Module deleted** → All rack module placements removed
- **Case deleted** → All racks using that case deleted
- **Patch deleted** → All votes and comments deleted

Configured via SQLAlchemy `ondelete="CASCADE"`.

### Application-Level Validation

- **Rack validation**: HP and power constraints checked before saving
- **Module placement**: Overlap detection and row capacity validation
- **Votes**: One vote per user per item (enforced by unique constraint)
- **Comments**: Content required, not empty

---

## Migrations

Database schema is managed using **Alembic**.

Migration files location: `backend/alembic/versions/`

### Creating Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
```

### Applying Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## Example Queries

### Get all modules in a rack with details

```sql
SELECT m.*, rm.row_index, rm.start_hp
FROM modules m
JOIN rack_modules rm ON m.id = rm.module_id
WHERE rm.rack_id = ?
ORDER BY rm.row_index, rm.start_hp
```

### Get public feed items (racks + patches)

```sql
SELECT 'rack' as type, r.id, r.name, r.created_at, u.username
FROM racks r
JOIN users u ON r.user_id = u.id
WHERE r.is_public = TRUE

UNION ALL

SELECT 'patch' as type, p.id, p.name, p.created_at, u.username
FROM patches p
JOIN racks r ON p.rack_id = r.id
JOIN users u ON r.user_id = u.id
WHERE p.is_public = TRUE

ORDER BY created_at DESC
```

### Get vote count for a rack

```sql
SELECT COUNT(*) FROM votes WHERE rack_id = ?
```
