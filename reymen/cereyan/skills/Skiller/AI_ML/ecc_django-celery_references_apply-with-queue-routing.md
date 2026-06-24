# Apply with queue routing
sync_contact_to_crm.apply_async(args=[contact.pk], queue='high_priority')