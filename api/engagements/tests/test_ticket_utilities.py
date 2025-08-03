from django.test import TestCase
from engagements.utilities.ticket_utilities import generate_ticket_number, is_valid_ticket_number
from engagements.tests.factory import TestDataFactory
from relations.tests.factory import create_tenant, create_user


class TestTicketUtilities(TestCase):
    """Test the ticket utilities functions."""
    
    def setUp(self):
        self.tenant = create_tenant()
        self.user = create_user(tenant=self.tenant)
        self.factory = TestDataFactory(self.tenant, self.user)
    
    def test_generate_ticket_number_first_ticket(self):
        """Test generating ticket number for the first ticket."""
        ticket_number = generate_ticket_number(self.tenant)
        
        # Should be 7 digits starting with 1000000
        self.assertEqual(len(ticket_number), 7)
        self.assertEqual(ticket_number, "1000000")
        self.assertTrue(ticket_number.isdigit())
    
    def test_generate_ticket_number_sequential(self):
        """Test generating sequential ticket numbers."""
        # Create first ticket
        ticket1 = self.factory.create_ticket(ticket_number="1000000")
        
        # Generate next ticket number
        ticket_number = generate_ticket_number(self.tenant)
        self.assertEqual(ticket_number, "1000001")
        
        # Create second ticket
        ticket2 = self.factory.create_ticket(ticket_number="1000001")
        
        # Generate next ticket number
        ticket_number = generate_ticket_number(self.tenant)
        self.assertEqual(ticket_number, "1000002")
    
    def test_generate_ticket_number_with_gaps(self):
        """Test generating ticket number when there are gaps in the sequence."""
        # Create tickets with gaps
        ticket1 = self.factory.create_ticket(ticket_number="1000000")
        ticket2 = self.factory.create_ticket(ticket_number="1000002")  # Gap at 1000001
        
        # Should generate the next available number
        ticket_number = generate_ticket_number(self.tenant)
        self.assertEqual(ticket_number, "1000003")
    
    def test_generate_ticket_number_ignores_non_7_digit_numbers(self):
        """Test that non-7-digit ticket numbers are ignored."""
        # Create tickets with non-7-digit numbers
        ticket1 = self.factory.create_ticket(ticket_number="12345")  # 5 digits
        ticket2 = self.factory.create_ticket(ticket_number="12345678")  # 8 digits
        ticket3 = self.factory.create_ticket(ticket_number="1000000")  # 7 digits
        
        # Should generate based on the 7-digit number only
        ticket_number = generate_ticket_number(self.tenant)
        self.assertEqual(ticket_number, "1000001")
    
    def test_generate_ticket_number_race_condition_handling(self):
        """Test handling of race conditions when generating ticket numbers."""
        # Create a ticket with a high number
        ticket = self.factory.create_ticket(ticket_number="1000005")
        
        # Generate next ticket number
        ticket_number = generate_ticket_number(self.tenant)
        self.assertEqual(ticket_number, "1000006")
    
    def test_generate_ticket_number_different_tenants(self):
        """Test that ticket numbers are independent across tenants."""
        tenant2 = create_tenant()
        user2 = create_user(tenant=tenant2)
        factory2 = TestDataFactory(tenant2, user2)
        
        # Create tickets in first tenant
        ticket1 = self.factory.create_ticket(ticket_number="1000000")
        ticket2 = self.factory.create_ticket(ticket_number="1000001")
        
        # Generate ticket number for second tenant
        ticket_number = generate_ticket_number(tenant2)
        self.assertEqual(ticket_number, "1000000")  # Should start from beginning
    
    def test_is_valid_ticket_number_valid_7_digit(self):
        """Test validation of valid 7-digit ticket numbers."""
        valid_numbers = ["1000000", "1234567", "9999999"]
        
        for number in valid_numbers:
            self.assertTrue(is_valid_ticket_number(number))
    
    def test_is_valid_ticket_number_invalid_formats(self):
        """Test validation of invalid ticket number formats."""
        invalid_numbers = [
            None,  # None
            "",    # Empty string
            "123456",   # 6 digits
            "12345678", # 8 digits
            "abcdefg",  # Non-numeric
            "123456a",  # Mixed alphanumeric
            " 1000000", # Leading space
            "1000000 ", # Trailing space
        ]
        
        for number in invalid_numbers:
            self.assertFalse(is_valid_ticket_number(number))
    
    def test_is_valid_ticket_number_edge_cases(self):
        """Test validation of edge cases."""
        # Zero-padded numbers
        self.assertTrue(is_valid_ticket_number("0000001"))
        
        # Maximum 7-digit number
        self.assertTrue(is_valid_ticket_number("9999999"))
        
        # Minimum 7-digit number
        self.assertTrue(is_valid_ticket_number("0000000"))
    
    def test_is_valid_ticket_number_integer_input(self):
        """Test validation with integer input."""
        # Should convert integer to string and validate
        self.assertTrue(is_valid_ticket_number(1000000))
        self.assertTrue(is_valid_ticket_number(1234567))
        
        # Invalid integers
        self.assertFalse(is_valid_ticket_number(123456))  # 6 digits
        self.assertFalse(is_valid_ticket_number(12345678))  # 8 digits 