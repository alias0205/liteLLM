from dotenv import dotenv_values
import psycopg

settings = dotenv_values('.env')
with psycopg.connect(settings['DIRECT_URL'], connect_timeout=10, autocommit=True) as connection:
    rows = connection.execute(
        "SELECT a.pid, a.state, a.wait_event_type, a.wait_event, "
        "extract(epoch FROM now() - a.xact_start)::int, l.granted "
        "FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid "
        "WHERE l.locktype = 'advisory'"
    ).fetchall()
    print('Advisory lock sessions:', rows)
    print('Migration table exists:', connection.execute(
        "SELECT to_regclass('public._prisma_migrations') IS NOT NULL"
    ).fetchone()[0])
    print('Incomplete migrations:', connection.execute(
        'SELECT migration_name, applied_steps_count FROM "_prisma_migrations" '
        'WHERE finished_at IS NULL AND rolled_back_at IS NULL'
    ).fetchall())
    print('Completed migrations:', connection.execute(
        'SELECT count(*) FROM "_prisma_migrations" WHERE finished_at IS NOT NULL'
    ).fetchone()[0])
    print('MCP columns:', connection.execute(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = 'LiteLLM_MCPServerTable'"
    ).fetchall())
