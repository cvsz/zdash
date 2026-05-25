from dataclasses import dataclass, field
from datetime import datetime, timezone
class PluginStatus: approved='approved'
@dataclass
class PluginManifest: id:str; name:str; slug:str; version:str; description:str; author:str; category:str; status:str='approved'; required_features:list[str]=field(default_factory=list); required_permissions:list[str]=field(default_factory=list); config_schema:dict=field(default_factory=dict); default_config:dict=field(default_factory=dict); entrypoint:str=''; safety_level:str='safe'; metadata:dict=field(default_factory=dict); created_at:datetime=field(default_factory=lambda:datetime.now(timezone.utc)); updated_at:datetime=field(default_factory=lambda:datetime.now(timezone.utc))
