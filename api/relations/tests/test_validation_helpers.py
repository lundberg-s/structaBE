from django.test import TestCase
from django.core.exceptions import ValidationError
from relations.utilities.validation_helpers import (
    TenantValidatorMixin,
    validate_tenant_consistency,
)
from relations.tests.factory import create_tenant, create_person, create_organization
from core.models import Tenant


class TestTenantValidatorMixin(TestCase):
    """Test the TenantValidatorMixin."""
    
    def setUp(self):
        self.validator = TenantValidatorMixin()
        self.tenant1 = create_tenant()
        self.tenant2 = create_tenant()
        self.person1 = create_person(tenant=self.tenant1, first_name='John', last_name='Doe')
        self.person2 = create_person(tenant=self.tenant2, first_name='Jane', last_name='Smith')

    def test_validate_tenant_consistency_success(self):
        """Test successful tenant consistency validation."""
        self.assertTrue(self.validator.validate_tenant_consistency(self.tenant1, self.person1))

    def test_validate_tenant_consistency_failure(self):
        """Test tenant consistency validation failure."""
        with self.assertRaises(ValidationError):
            self.validator.validate_tenant_consistency(self.tenant1, self.person2)

    def test_validate_tenant_consistency_with_none(self):
        """Test tenant consistency validation with None values."""
        self.assertTrue(self.validator.validate_tenant_consistency(self.tenant1, self.person1, None))

    def test_validate_tenant_consistency_no_tenant_attr(self):
        """Test tenant consistency validation with object without tenant attribute."""
        obj_without_tenant = type('TestObj', (), {})()
        self.assertTrue(self.validator.validate_tenant_consistency(self.tenant1, obj_without_tenant))


class TestValidateTenantConsistencyFunction(TestCase):
    """Test the standalone validate_tenant_consistency function."""
    
    def setUp(self):
        self.tenant1 = create_tenant()
        self.tenant2 = create_tenant()
        self.person1 = create_person(tenant=self.tenant1, first_name='John', last_name='Doe')
        self.person2 = create_person(tenant=self.tenant2, first_name='Jane', last_name='Smith')

    def test_validate_tenant_consistency_success(self):
        """Test successful tenant consistency validation."""
        self.assertTrue(validate_tenant_consistency(self.tenant1, self.person1))

    def test_validate_tenant_consistency_failure(self):
        """Test tenant consistency validation failure."""
        with self.assertRaises(ValidationError):
            validate_tenant_consistency(self.tenant1, self.person2)

    def test_validate_tenant_consistency_with_none(self):
        """Test tenant consistency validation with None values."""
        self.assertTrue(validate_tenant_consistency(self.tenant1, self.person1, None))

    def test_validate_tenant_consistency_no_tenant_attr(self):
        """Test tenant consistency validation with object without tenant attribute."""
        obj_without_tenant = type('TestObj', (), {})()
        self.assertTrue(validate_tenant_consistency(self.tenant1, obj_without_tenant))


class TestValidationHelpersCoverage(TestCase):
    """Test to ensure all validation helper functions are covered."""
    
    def test_tenant_validator_mixin_success(self):
        """Test TenantValidatorMixin success path."""
        tenant = create_tenant()
        person = create_person(tenant=tenant, first_name='John', last_name='Doe')
        mixin = TenantValidatorMixin()
        self.assertTrue(mixin.validate_tenant_consistency(tenant, person))

    def test_validate_tenant_consistency_function_success(self):
        """Test standalone validate_tenant_consistency function success path."""
        tenant = create_tenant()
        person = create_person(tenant=tenant, first_name='John', last_name='Doe')
        self.assertTrue(validate_tenant_consistency(tenant, person)) 