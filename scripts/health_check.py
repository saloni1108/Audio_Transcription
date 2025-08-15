import os
import psycopg2
import redis
import boto3


def check_health():
    status = {"postgres": False, "redis": False, "s3": False}

    # Postgres
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.cursor().execute("SELECT 1")
        conn.close()
        status["postgres"] = True
    except Exception as e:
        status["postgres"] = str(e)

    # Redis
    try:
        r = redis.Redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        status["redis"] = True
    except Exception as e:
        status["redis"] = str(e)

    # S3
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION"),
        )
        s3.list_buckets()
        status["s3"] = True
    except Exception as e:
        status["s3"] = str(e)

    return status


if __name__ == "__main__":
    from pprint import pprint
    pprint(check_health())
