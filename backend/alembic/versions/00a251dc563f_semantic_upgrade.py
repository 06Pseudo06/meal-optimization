"""semantic_upgrade

Revision ID: 00a251dc563f
Revises: 0098dca6dc9e
Create Date: 2026-05-06 12:03:51.049445

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '00a251dc563f'
down_revision: Union[str, Sequence[str], None] = '0098dca6dc9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add fields to recipes
    op.add_column('recipes', sa.Column('slug', sa.String(), nullable=True))
    op.create_unique_constraint('uq_recipes_slug', 'recipes', ['slug'])
    op.add_column('recipes', sa.Column('description', sa.String(), nullable=True))
    op.add_column('recipes', sa.Column('prep_time', sa.Integer(), nullable=True))
    op.add_column('recipes', sa.Column('difficulty', sa.String(), nullable=True))
    op.add_column('recipes', sa.Column('health_score', sa.Float(), nullable=True))
    op.add_column('recipes', sa.Column('meal_type', sa.String(), nullable=True))
    op.add_column('recipes', sa.Column('cuisine', sa.String(), nullable=True))
    op.add_column('recipes', sa.Column('protein_density', sa.Float(), nullable=True))
    op.add_column('recipes', sa.Column('calorie_density', sa.Float(), nullable=True))
    op.add_column('recipes', sa.Column('is_quick', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('recipes', sa.Column('is_gym_friendly', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('recipes', sa.Column('is_budget_friendly', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('recipes', sa.Column('spice_level', sa.String(), nullable=True))
    op.add_column('recipes', sa.Column('created_at', sa.BigInteger(), server_default='0', nullable=False))
    
    # 2. Add fields to ingredients
    op.add_column('ingredients', sa.Column('category', sa.String(), nullable=True))
    op.add_column('ingredients', sa.Column('aliases', postgresql.JSONB(), nullable=True))
    op.add_column('ingredients', sa.Column('protein_per_100g', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('calories_per_100g', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('is_allergen', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('ingredients', sa.Column('created_at', sa.BigInteger(), server_default='0', nullable=False))
    op.add_column('ingredients', sa.Column('updated_at', sa.BigInteger(), server_default='0', nullable=False))

    # 3. Tags Conversion logic
    op.execute("""
        ALTER TABLE recipes
        ALTER COLUMN tags TYPE JSONB
        USING (
        CASE
            WHEN tags IS NULL OR trim(tags) = '' THEN '[]'::jsonb
            WHEN tags ~ '^\s*\[.*\]\s*$' THEN tags::jsonb
            ELSE to_jsonb(string_to_array(tags, ','))
        END
        );
    """)

    # 4. GIN Indexes
    op.create_index("idx_recipe_tags_gin", "recipes", ["tags"], postgresql_using="gin")

    # 5. Constraints
    op.create_check_constraint("ck_recipe_health_score", "recipes", "health_score >= 0 AND health_score <= 1")
    op.create_check_constraint("ck_recipe_prep_time", "recipes", "prep_time >= 0")


def downgrade() -> None:
    # 1. Drop constraints
    op.drop_constraint("ck_recipe_prep_time", "recipes", type_="check")
    op.drop_constraint("ck_recipe_health_score", "recipes", type_="check")

    # 2. Drop index
    op.drop_index("idx_recipe_tags_gin", table_name="recipes", postgresql_using="gin")

    # 3. Revert Tags
    op.execute("""
        ALTER TABLE recipes
        ALTER COLUMN tags TYPE VARCHAR
        USING tags::text;
    """)

    # 4. Drop ingredient columns
    op.drop_column('ingredients', 'updated_at')
    op.drop_column('ingredients', 'created_at')
    op.drop_column('ingredients', 'is_allergen')
    op.drop_column('ingredients', 'calories_per_100g')
    op.drop_column('ingredients', 'protein_per_100g')
    op.drop_column('ingredients', 'aliases')
    op.drop_column('ingredients', 'category')

    # 5. Drop recipe columns
    op.drop_column('recipes', 'created_at')
    op.drop_column('recipes', 'spice_level')
    op.drop_column('recipes', 'is_budget_friendly')
    op.drop_column('recipes', 'is_gym_friendly')
    op.drop_column('recipes', 'is_quick')
    op.drop_column('recipes', 'calorie_density')
    op.drop_column('recipes', 'protein_density')
    op.drop_column('recipes', 'cuisine')
    op.drop_column('recipes', 'meal_type')
    op.drop_column('recipes', 'health_score')
    op.drop_column('recipes', 'difficulty')
    op.drop_column('recipes', 'prep_time')
    op.drop_column('recipes', 'description')
    op.drop_constraint('uq_recipes_slug', 'recipes', type_='unique')
    op.drop_column('recipes', 'slug')
