from typing import NamedTuple

from deps_message_flow.messaging.common import IMessage
from deps_message_flow.messaging.producer import IMessageProducer

__all__ = ["FakeMessageProducer", "Command"]


class Command(NamedTuple):
    destination: str
    message: IMessage


class FakeMessageProducer(IMessageProducer):
    def __init__(self, message_queue: list[Command]) -> None:
        self._producer_messages = message_queue

    @property
    def sent(self) -> list[Command]:
        return self._producer_messages

    def send(self, destination: str, message: IMessage) -> None:
        self._producer_messages.append(Command(destination=destination, message=message))
