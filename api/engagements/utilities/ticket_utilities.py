from django.db import transaction
from django.db.models import Max
from django.apps import apps


def generate_ticket_number(tenant):
    """
    Generate a unique 7-digit ticket number for the given tenant.
    Uses a counter-based approach to ensure uniqueness.
    """
    Ticket = apps.get_model('engagements', 'Ticket')
    
    with transaction.atomic():
        # Get the highest ticket number for this tenant
        max_ticket = Ticket.objects.filter(
            tenant=tenant,
            ticket_number__isnull=False,
            ticket_number__regex=r'^\d{7}$'  # Only consider 7-digit numbers
        ).aggregate(
            max_number=Max('ticket_number')
        )['max_number']
        
        if max_ticket:
            # Extract the numeric part and increment
            next_number = int(max_ticket) + 1
        else:
            # Start with 1000000 (7 digits)
            next_number = 1000000
        
        # Format as 7-digit string
        ticket_number = f"{next_number:07d}"
        
        # Double-check uniqueness (in case of race conditions)
        while Ticket.objects.filter(tenant=tenant, ticket_number=ticket_number).exists():
            next_number += 1
            ticket_number = f"{next_number:07d}"
        
        return ticket_number


def is_valid_ticket_number(ticket_number):
    """
    Validate if a ticket number is in the correct format (7 digits).
    """
    if not ticket_number:
        return False
    return len(str(ticket_number)) == 7 and str(ticket_number).isdigit() 