# Group: run tasks in parallel
parallel = group(
    send_welcome_email.s(user_id)
    for user_id in new_user_ids
)
parallel.delay()