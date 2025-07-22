from core.models import Tenant

def create_tenant(work_item_type='ticket'):
    tenant = Tenant.objects.create(
        work_item_type=work_item_type
        )
    tenant.save()
    return tenant