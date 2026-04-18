from deps_extraction.domain.model import Code
from deps_extraction.domain.model.document_type import CompliancePolicy


def test__default_compliance__to_be_false() -> None:
    compliance_policy = CompliancePolicy(code=Code(), read_only=None, confidential=None)

    assert compliance_policy.read_only is False
    assert compliance_policy.confidential is False


def test__compliance_creation() -> None:
    compliance_policy = CompliancePolicy(code=Code(), read_only=True, confidential=False)

    assert compliance_policy.read_only is True
    assert compliance_policy.confidential is False


def test__compliance_update__both_fields_updated() -> None:
    compliance_policy = CompliancePolicy(code=Code(), read_only=False, confidential=False)

    updated_compliance_policy = compliance_policy.create_updated(read_only=True, confidential=True)

    assert updated_compliance_policy.read_only is True
    assert updated_compliance_policy.confidential is True
    assert updated_compliance_policy.code == compliance_policy.code


def test__compliance_update__confidential_updated() -> None:
    compliance_policy = CompliancePolicy(code=Code(), read_only=False, confidential=False)

    updated_compliance_policy = compliance_policy.create_updated(confidential=True)

    assert updated_compliance_policy.read_only is False
    assert updated_compliance_policy.confidential is True
    assert updated_compliance_policy.code == compliance_policy.code


def test__compliance_update__read_only_updated() -> None:
    compliance_policy = CompliancePolicy(code=Code(), read_only=False, confidential=False)

    updated_compliance_policy = compliance_policy.create_updated(read_only=True)

    assert updated_compliance_policy.read_only is True
    assert updated_compliance_policy.confidential is False
    assert updated_compliance_policy.code == compliance_policy.code
