# PostgreSQL Bootstrapping

This decoment describes setting up a PostgreSQL database and tables. TBA.

## Database Schema

Apply schema from `backend/schema.sql`:

```bash
psql "$DATABASE_URL" -f backend/schema.sql
```
