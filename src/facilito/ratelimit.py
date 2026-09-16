from pydantic import BaseModel, ConfigDict, Field, model_validator


class RateLimitSettings(BaseModel):
    """Validated configuration for rate-limiting prevention."""

    model_config = ConfigDict(extra="forbid")

    request_delay: float = Field(default=0.0, ge=0.0, le=600.0)
    request_jitter: float = Field(default=0.0, ge=0.0, le=600.0)
    download_delay: float = Field(default=0.0, ge=0.0, le=600.0)
    retry_enabled: bool = True
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_base_delay: float = Field(default=1.0, ge=0.1, le=60.0)
    retry_max_delay: float = Field(default=30.0, ge=0.1, le=300.0)
    retry_after_max: float = Field(default=60.0, ge=1.0, le=600.0)
    block_detection_enabled: bool = True

    @model_validator(mode="after")
    def _check_bounds(self):
        if self.retry_max_delay < self.retry_base_delay:
            raise ValueError(
                "retry_max_delay must be greater or equal to retry_base_delay"
            )

        return self
