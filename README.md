# Step 5: Generate and Apply Migrations

Whenever you make changes to your models, generate a new migration script:

```shell
alembic revision --autogenerate -m "Describe your changes"
alembic upgrade head
```
