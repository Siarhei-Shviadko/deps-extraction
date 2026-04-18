from typing import Optional

from ..shared import Code, Guard, ImmutableCheck

__all__ = ["CompliancePolicy"]


class CompliancePolicy:
    code = Guard[Code](Code, ImmutableCheck())
    read_only = Guard[bool](bool, ImmutableCheck())
    confidential = Guard[bool](bool, ImmutableCheck())

    def __init__(
        self,
        code: Code,
        read_only: Optional[bool],
        confidential: Optional[bool],
    ) -> None:
        self.code = code
        self.read_only = read_only or False
        self.confidential = confidential or False

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CompliancePolicy)
            and other.code == self.code
            and other.read_only == self.read_only
            and other.confidential == self.confidential
        )

    def create_updated(
        self,
        read_only: Optional[bool] = None,
        confidential: Optional[bool] = None,
    ) -> "CompliancePolicy":
        return CompliancePolicy(
            code=self.code,
            read_only=read_only if read_only is not None else self.read_only,
            confidential=confidential if confidential is not None else self.confidential,
        )
