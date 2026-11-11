from pydantic import BaseModel, ConfigDict


class CountryRead(BaseModel):
    id: int
    name: str
    continent_id: int

    model_config = ConfigDict(from_attributes=True)


class SpecializationRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class SkillRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class IndustryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
