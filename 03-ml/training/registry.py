# Algorithm registry — maps config 'algorithm' keys to their module paths.
# To add a new algorithm: import its module under training/ and add an entry here.
# The module must expose a walk_forward(df, config, horizon) function.

ALGORITHM_REGISTRY = {
    "random_forest": "training.random_forest",
}
