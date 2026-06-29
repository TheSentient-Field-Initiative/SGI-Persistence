# src.embeddings — System-specific embedding functions.

from . import distributed_embedding
from . import immune_embedding
from . import ant_embedding
from . import institution_embedding

# Registry of system-specific embedders
EMBEDDINGS = {
    "distributed": distributed_embedding,
    "immune": immune_embedding,
    "ant_colony": ant_embedding,
    "institution": institution_embedding,
}


def get_embedding(system_name: str):
    """Get the embedding module for a specific system.

    Args:
        system_name: One of "distributed", "immune", "ant_colony", "institution".

    Returns:
        Embedding module with embed() and validate() functions.

    Raises:
        KeyError: If system_name not found.
    """
    if system_name not in EMBEDDINGS:
        raise KeyError(
            f"Unknown system '{system_name}'. Available: {list(EMBEDDINGS.keys())}"
        )
    return EMBEDDINGS[system_name]


def embed_state(system_name: str, state: dict) -> "np.ndarray":
    """Embed a state using the system-specific embedding.

    Args:
        system_name: System name.
        state: Simulation state dictionary.

    Returns:
        8D numpy array.
    """
    module = get_embedding(system_name)
    return module.embed(state)
