# Persist to dead-letter table for manual review
            FailedCharge.objects.create(
                order_id=order_id,
                error=str(exc),
                task_id=self.request.id,
            )
            return  # Don't raise — task is permanently failed
        raise self.retry(exc=exc)
```