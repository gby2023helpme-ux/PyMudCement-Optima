"""Google Material Symbols icon helpers.

Icons are rendered with the Material Symbols Rounded webfont (loaded in
``theme.py``) as inline ``<span>`` elements so they can be embedded inside
Streamlit HTML labels (buttons, heroes, cards, footers, etc.).
"""

ICON_FONT_VARIATIONS = "'FILL' {fill}, 'wght' {weight}, 'GRAD' 0, 'opsz' 40"


def material_icon(
    name: str,
    size: str = "1.4rem",
    fill: bool = True,
    weight: int = 500,
    color: str | None = None,
    extra_style: str = "",
) -> str:
    """Return an HTML snippet for a Google Material Symbols icon.

    Args:
        name: Material Symbols ligature name, e.g. ``"home"``, ``"balance"``.
        size: CSS font-size, e.g. ``"2rem"``.
        fill: Whether to render the filled (solid) glyph variant.
        weight: Icon stroke weight (100-700).
        color: Optional CSS color override.
        extra_style: Additional inline CSS rules appended to the style attr.

    Returns:
        A ``<span class="material-symbols-rounded">`` HTML string.
    """
    style = f"font-size:{size};font-variation-settings:{ICON_FONT_VARIATIONS.format(fill=1 if fill else 0, weight=weight)};"
    if color:
        style += f"color:{color};"
    if extra_style:
        style += extra_style
    return f'<span class="material-symbols-rounded" style="{style}">{name}</span>'
