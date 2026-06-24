# BAD: Calling tasks synchronously in production views
result = generate_report.apply()      # Blocks the request thread