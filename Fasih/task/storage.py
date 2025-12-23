from storages.backends.s3boto3 import S3Boto3Storage

class TaskExecutionStorage(S3Boto3Storage):
    bucket_name = "fasih-task-executions"
    file_overwrite = False
