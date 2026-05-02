from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.di import InfrastructureContainer
from app.domain.di import DomainContainer
from app.application.di import ApplicationContainer

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    infrastructure = providers.Container(
        InfrastructureContainer,
        db_session=db_session,
    )
    
    domain = providers.Container(
        DomainContainer,
    )
    
    application = providers.Container(
        ApplicationContainer,
        infrastructure=infrastructure,
        domain=domain,
    )

container = Container()

def get_container():
    return container

def wire_container(modules: list[str]) -> None:
    container.wire(modules=modules)

def reset_container() -> None:
    container.reset_singletons()
