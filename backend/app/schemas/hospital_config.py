from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ConfigBase(BaseModel):
    config_type: str
    config_key: str
    config_value: Any
    is_active: bool = True

class ConfigCreate(ConfigBase):
    pass

class ConfigUpdate(BaseModel):
    config_value: Optional[Any] = None
    is_active: Optional[bool] = None

class ConfigResponse(ConfigBase):
    id: int
    hospital_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
