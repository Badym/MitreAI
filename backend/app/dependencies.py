from typing import Annotated

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

from app.repositories.health_repository import HealthRepository
from app.services.health_service import HealthService

# Konfiguracja i baza


def get_database(request: Request) -> AsyncDatabase:
    return request.app.state.database


DatabaseDep = Annotated[AsyncDatabase, Depends(get_database)]

# Repozytoria


def get_health_repository(database: DatabaseDep) -> HealthRepository:
    return HealthRepository(database)


HealthRepositoryDep = Annotated[HealthRepository, Depends(get_health_repository)]

# Serwisy


def get_health_service(repository: HealthRepositoryDep) -> HealthService:
    return HealthService(repository)


HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
