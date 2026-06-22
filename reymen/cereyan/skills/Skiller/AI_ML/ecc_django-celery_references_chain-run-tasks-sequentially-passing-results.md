# Chain: run tasks sequentially, passing results
pipeline = chain(
    fetch_data.s(source_id),
    transform_data.s(),          # receives fetch_data result as first arg
    load_to_warehouse.s(),
)
pipeline.delay()