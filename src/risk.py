def confidence_label(probability: float, sample_size: int):
    if sample_size < 30:
        return "INSUFICIENTE"
    if probability >= 0.75:
        return "ALTA"
    if probability >= 0.65:
        return "MEDIA"
    return "BAJA"


def should_show_signal(probability: float, edge: float, sample_size: int, min_sample=30, min_probability=0.60, min_edge=0.03):
    return (
        sample_size >= min_sample
        and probability >= min_probability
        and edge >= min_edge
    )
