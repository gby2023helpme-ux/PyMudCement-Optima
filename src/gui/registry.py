"""Central registry of GUI modules.

Each entry maps a page name to a tuple of ``(icon, title, description)``
used by the sidebar navigation, the dashboard grid, and the page router.
"""

# name -> (material icon, display title, short description)
MODULE_META = {
    "Home": ("home", "Home", "Dashboard overview and module launcher."),
    "Pressure Balance": (
        "balance",
        "Pressure Balance",
        "Balance pore pressure with minimum mud weight across casing intervals.",
    ),
    "Mud Report Parser": (
        "upload_file",
        "Mud Report Parser",
        "Upload CSV mud reports and build rheological profiles.",
    ),
    "Annular Hydraulics & ECD": (
        "speed",
        "Annular Hydraulics & ECD",
        "Compute annular volume, velocity, and ECD.",
    ),
    "System Hydraulics": (
        "water",
        "System Hydraulics",
        "Non-Newtonian pressure drops through the circulating system.",
    ),
    "Cement Slurry Design": (
        "science",
        "Cement Slurry Design",
        "Design slurries with automated additive selection.",
    ),
    "Cementing Procedure Sheet": (
        "description",
        "Cementing Procedure Sheet",
        "Generate stage-by-stage job procedures.",
    ),
    "P&A Plug Design": (
        "engineering",
        "P&A Plug Design",
        "Design suspension, sidetrack, and abandonment plugs.",
    ),
}
