import json
from uuid import uuid4

from deps_message_flow.sagas.orchestration import ISagaInstanceRepository, SagaInstance

__all__ = ["FakeSagaInstanceRepository"]


class FakeSagaInstanceRepository(ISagaInstanceRepository):
    def __init__(self) -> None:
        self._saga_table = {}  # type: ignore
        self._entity_saga_pair_table = {}  # type: ignore

    def save(self, saga_instance: SagaInstance) -> SagaInstance:
        saga_instance.saga_id = uuid4().hex
        self._saga_table[saga_instance.saga_id] = saga_instance

        entity_id = json.loads(saga_instance.serialized_saga_data.saga_data_json).get("entity_id")
        if entity_id:
            self._entity_saga_pair_table[entity_id] = saga_instance.saga_id

        return saga_instance

    def find(self, saga_id: str) -> SagaInstance:
        return self._saga_table[saga_id]

    def find_for_entity(self, entity_id: str) -> SagaInstance:
        saga_id = self._entity_saga_pair_table[entity_id]
        return self._saga_table[saga_id]

    def update(self, saga_instance: SagaInstance) -> SagaInstance:
        self._saga_table[saga_instance.saga_id] = saga_instance
        return saga_instance
