# BAD — reinstalls every activation
[hook]
on-activate = """
  pip install -r requirements.txt
"""