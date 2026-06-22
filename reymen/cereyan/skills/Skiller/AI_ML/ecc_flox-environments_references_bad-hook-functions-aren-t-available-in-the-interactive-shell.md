# BAD — hook functions aren't available in the interactive shell
[hook]
on-activate = """
  deploy() { kubectl apply -f k8s/; }
"""