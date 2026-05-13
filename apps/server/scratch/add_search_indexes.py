import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    async with engine.begin() as conn:
        print("Enabling pg_trgm extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        
        print("Creating GIN indexes for hybrid search...")
        # Index for posts table (title and content)
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_posts_fts ON posts USING gin (title gin_trgm_ops, content gin_trgm_ops);"))
        
        # Index for post_embeddings table (content chunks)
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_post_embeddings_fts ON post_embeddings USING gin (content gin_trgm_ops);"))
        
        print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
