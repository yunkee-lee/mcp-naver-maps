from pydantic import BaseModel, Field
from typing import List


class Meta(BaseModel):
  totalCount: int = Field(description="Total number of results")
  page: int = Field(description="Current page number")
  count: int = Field(description="Number of results on the current page")


class Address(BaseModel):
  roadAddress: str = Field(description="Street address")
  jibunAddress: str = Field(description="Land-lot address")
  englishAddress: str = Field(description="Street address in English")
  x: str = Field(description="Longitude")
  y: str = Field(description="Latitude")
  distance: float = Field(description="Distance in meters from the center coordinate")


class GeocodeResponse(BaseModel):
  status: str = Field(description="Status of the request")
  meta: Meta = Field(description="Metadata of the response")
  addresses: List[Address] = Field(description="List of matching addresses")
  errorMessage: str = Field(description="Error message (only present for HTTP 500 errors)")


class LocalItem(BaseModel):
  title: str = Field(description="Name of the place")
  link: str = Field(description="URL of the place")
  category: str = Field(description="Category of the place")
  description: str = Field(description="Brief description of the place")
  address: str = Field(description="Land-lot address")
  roadAddress: str = Field(description="Street address")


class LocalSearchResponse(BaseModel):
  total: int = Field(description="Total number of results")
  start: int = Field(description="Starting index of results")
  display: int = Field(description="Number of results displayed in the response")
  items: List[LocalItem] = Field(description="List of search result items")
