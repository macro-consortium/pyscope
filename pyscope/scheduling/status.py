import enum


class Status(enum.Enum):
    UNSCHEDULED = "unscheduled"
    EXPIRED = "expired"
    INVALID = "invalid"
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    FAILED = "failed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
