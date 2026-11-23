from datetime import datetime
from typing import Any
from pydantic import BaseModel


class MetricSnapshotResponse(BaseModel):
    metric_name: str
    metric_value: float
    dimensions: dict[str, Any] | None
    captured_at: datetime
    model_config = {"from_attributes": True}
