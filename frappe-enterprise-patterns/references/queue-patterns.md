```markdown
# Queue Patterns Reference

## Overview
Background job and queue patterns for enterprise Frappe applications.

## Basic Enqueueing

### Simple Job
```python
import frappe

def send_notification(user, message):
    """Function to run in background"""
    frappe.sendmail(
        recipients=user,
        subject="Notification",
        message=message
    )

# Enqueue the job
frappe.enqueue(
    send_notification,
    user="user@example.com",
    message="Hello!"
)
```

### With Options
```python
frappe.enqueue(
    "my_app.tasks.process_data",
    queue="long",           # short, default, long
    timeout=600,            # seconds
    is_async=True,          # default True
    now=False,              # Run synchronously if True
    job_name="unique_name", # For deduplication
    at_front=False,         # Priority
    deduplicate=True,       # Prevent duplicate jobs
    enqueue_after_commit=True,  # Wait for transaction commit
    
    # Job arguments
    data_id="123",
    option="value"
)
```

## Queue Types

### Queue Selection
```python
# Short queue - quick tasks (< 5 minutes)
frappe.enqueue(send_email, queue="short")

# Default queue - standard tasks (5-30 minutes)
frappe.enqueue(process_batch, queue="default")

# Long queue - heavy tasks (> 30 minutes)
frappe.enqueue(generate_report, queue="long")
```

### Custom Queues
```python
# In hooks.py
scheduler_events = {
    "all": [
        "my_app.tasks.process_custom_queue"
    ]
}

# In tasks.py
def process_custom_queue():
    """Process jobs from custom queue"""
    from frappe.utils.background_jobs import get_queue
    
    queue = get_queue("my_custom_queue")
    job = queue.dequeue()
    
    if job:
        job.perform()
```

## Scheduled Jobs

### hooks.py Configuration
```python
scheduler_events = {
    # Every minute
    "all": [
        "my_app.tasks.process_queue"
    ],
    
    # Hourly
    "hourly": [
        "my_app.tasks.hourly_cleanup"
    ],
    
    # Daily at midnight
    "daily": [
        "my_app.tasks.daily_report"
    ],
    
    # Weekly on Monday
    "weekly": [
        "my_app.tasks.weekly_summary"
    ],
    
    # Monthly on 1st
    "monthly": [
        "my_app.tasks.monthly_archive"
    ],
    
    # Cron expression
    "cron": {
        "0 9 * * *": [  # Every day at 9 AM
            "my_app.tasks.morning_task"
        ],
        "*/15 * * * *": [  # Every 15 minutes
            "my_app.tasks.frequent_check"
        ]
    }
}
```

## Job Patterns

### Batch Processing
```python
def process_large_dataset():
    """Process data in batches"""
    batch_size = 100
    offset = 0
    
    while True:
        records = frappe.get_all("My DocType",
            filters={"status": "Pending"},
            limit_start=offset,
            limit_page_length=batch_size
        )
        
        if not records:
            break
        
        for record in records:
            process_single_record(record.name)
        
        offset += batch_size
        frappe.db.commit()  # Commit each batch
```

### Chunked Enqueueing
```python
def enqueue_bulk_operation(items):
    """Split large job into chunks"""
    chunk_size = 50
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        frappe.enqueue(
            process_chunk,
            items=chunk,
            chunk_number=i // chunk_size,
            queue="long",
            deduplicate=True,
            job_name=f"bulk_op_chunk_{i}"
        )

def process_chunk(items, chunk_number):
    """Process a chunk of items"""
    for item in items:
        process_item(item)
    
    frappe.db.commit()
    frappe.publish_realtime("bulk_progress", {
        "chunk": chunk_number,
        "completed": len(items)
    })
```

### Job Chaining
```python
def job_step_1(data_id):
    """First step of multi-step job"""
    result = perform_step_1(data_id)
    
    # Chain to next step
    frappe.enqueue(
        job_step_2,
        data_id=data_id,
        step_1_result=result,
        queue="default"
    )

def job_step_2(data_id, step_1_result):
    """Second step"""
    result = perform_step_2(data_id, step_1_result)
    
    frappe.enqueue(
        job_step_3,
        data_id=data_id,
        step_2_result=result,
        queue="default"
    )
```

## Error Handling

### Retry Pattern
```python
def job_with_retry(data_id, retry_count=0, max_retries=3):
    """Job with automatic retry"""
    try:
        process_data(data_id)
    except Exception as e:
        if retry_count < max_retries:
            # Exponential backoff
            delay = 2 ** retry_count * 60  # 1, 2, 4 minutes
            
            frappe.enqueue(
                job_with_retry,
                data_id=data_id,
                retry_count=retry_count + 1,
                max_retries=max_retries,
                queue="default",
                enqueue_after_commit=True
            )
        else:
            # Log failure
            log_job_failure(data_id, str(e))
            raise
```

### Error Notification
```python
def safe_background_job(func):
    """Decorator for jobs with error notification"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            frappe.log_error(
                title=f"Background Job Failed: {func.__name__}",
                message=frappe.get_traceback()
            )
            
            # Notify admin
            frappe.sendmail(
                recipients=frappe.db.get_single_value("System Settings", "admin_email"),
                subject=f"Job Failed: {func.__name__}",
                message=f"Error: {str(e)}\n\nArgs: {args}\nKwargs: {kwargs}"
            )
            raise
    return wrapper

@safe_background_job
def critical_job(data):
    """Critical job with error handling"""
    process_critical_data(data)
```

## Progress Tracking

### Job Progress
```python
def long_running_job(items):
    """Track progress of long job"""
    total = len(items)
    job_id = frappe.local.job.id if hasattr(frappe.local, 'job') else None
    
    for i, item in enumerate(items):
        process_item(item)
        
        # Update progress
        progress = (i + 1) / total * 100
        frappe.publish_progress(
            percent=progress,
            title="Processing Items",
            description=f"Processing {i + 1} of {total}"
        )
        
        # Commit periodically
        if (i + 1) % 100 == 0:
            frappe.db.commit()
    
    frappe.db.commit()
```

### Job Status Tracking
```python
# Create job status record
def create_job_status(job_type, total_items):
    return frappe.get_doc({
        "doctype": "Job Status",
        "job_type": job_type,
        "total_items": total_items,
        "processed_items": 0,
        "status": "In Progress",
        "started_at": frappe.utils.now_datetime()
    }).insert()

def update_job_status(job_status_name, processed, status=None):
    frappe.db.set_value("Job Status", job_status_name, {
        "processed_items": processed,
        "status": status or "In Progress",
        "last_updated": frappe.utils.now_datetime()
    })
```

## Distributed Locking

### Prevent Concurrent Execution
```python
import frappe
from frappe.utils.redis_wrapper import RedisWrapper

def run_with_lock(lock_name, timeout=300):
    """Decorator for jobs requiring exclusive access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            redis = frappe.cache()
            lock_key = f"lock:{lock_name}"
            
            # Try to acquire lock
            acquired = redis.set(lock_key, "1", ex=timeout, nx=True)
            
            if not acquired:
                frappe.log_error(f"Could not acquire lock: {lock_name}")
                return None
            
            try:
                return func(*args, **kwargs)
            finally:
                redis.delete(lock_key)
        return wrapper
    return decorator

@run_with_lock("sync_inventory")
def sync_inventory():
    """Only one instance runs at a time"""
    perform_sync()
```

## Rate Limiting Jobs

### Throttled Processing
```python
import time

def throttled_job(items, rate_per_minute=60):
    """Process items with rate limiting"""
    interval = 60 / rate_per_minute
    
    for item in items:
        start = time.time()
        
        process_item(item)
        
        elapsed = time.time() - start
        if elapsed < interval:
            time.sleep(interval - elapsed)
```

## Monitoring

### Job Statistics
```python
def get_queue_stats():
    """Get queue statistics"""
    from rq import Queue
    from frappe.utils.background_jobs import get_queue
    
    stats = {}
    for queue_name in ["short", "default", "long"]:
        q = get_queue(queue_name)
        stats[queue_name] = {
            "pending": len(q),
            "failed": len(q.failed_job_registry),
            "scheduled": len(q.scheduled_job_registry)
        }
    
    return stats
```

Sources: Frappe Background Jobs, RQ (Redis Queue), Python-RQ
```