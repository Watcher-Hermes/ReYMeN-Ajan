# Chord: parallel tasks + callback when all complete
result = chord(
    group(process_chunk.s(chunk) for chunk in data_chunks),
    aggregate_results.s(),       # called with list of chunk results
)
result.delay()
```