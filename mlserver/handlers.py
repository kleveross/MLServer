import uuid

from .settings import Settings
from .repository import ModelRepository
from .types import (
    MetadataModelResponse,
    MetadataServerResponse,
    InferenceRequest,
    InferenceResponse,
)


class DataPlane:
    """
    Internal implementation of handlers, used by both the gRPC and REST
    servers.
    """

    def __init__(self, settings: Settings, model_repository: ModelRepository):
        self._settings = settings
        self._model_repository = model_repository

    async def live(self) -> bool:
        return True

    async def ready(self) -> bool:
        models = await self._model_repository.get_models()
        return all([model.ready for model in models])

    async def model_ready(self, name: str, version: str = None) -> bool:
        model = await self._model_repository.get_model(name, version)
        return model.ready

    async def metadata(self) -> MetadataServerResponse:
        return MetadataServerResponse(
            name=self._settings.server_name,
            version=self._settings.server_version,
            extensions=self._settings.extensions,
        )

    async def model_metadata(
        self, name: str, version: str = None
    ) -> MetadataModelResponse:
        model = await self._model_repository.get_model(name, version)
        # TODO: Make await optional for sync methods
        return await model.metadata()

    async def infer(
        self, payload: InferenceRequest, name: str, version: str = None
    ) -> InferenceResponse:
        if payload.id is None:
            payload.id = str(uuid.uuid4())

        model = await self._model_repository.get_model(name, version)
        # TODO: Make await optional for sync methods
        prediction = await model.predict(payload)

        # Ensure ID matches
        prediction.id = payload.id

        return prediction
