def create_login_history_partition(target, connection, **kwargs):
    create_partition_sql_january = """
        CREATE TABLE login_history_january PARTITION OF auth.login_history
        FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
    """
    connection.execute(create_partition_sql_january)

    create_partition_sql_february = """
        CREATE TABLE login_history_february PARTITION OF auth.login_history
        FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
    """
    connection.execute(create_partition_sql_february)

    create_partition_sql_march = """
        CREATE TABLE login_history_march PARTITION OF auth.login_history
        FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');
    """
    connection.execute(create_partition_sql_march)

    create_partition_sql_april = """
        CREATE TABLE login_history_april PARTITION OF auth.login_history
        FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
    """
    connection.execute(create_partition_sql_april)
