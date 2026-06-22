# Read permissions allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True