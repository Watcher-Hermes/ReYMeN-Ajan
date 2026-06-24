# 2. Run as non-root
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app