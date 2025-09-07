"""pytest module for stringprocessing."""

from stringprocessing import (
    clean_number_from_couple,
    cleanevfrom_dtv_tsh_entry,
    cleanevfromentry,
    correcttitleposition,
)


def test_correcttitleposition() -> None:
    """Moves title to correct position."""
    assert (  # nosec B101
        correcttitleposition("Ebeling, Bastian Dr. / Schmidt, Claudia")
        == "Ebeling, Dr. Bastian / Schmidt, Claudia"
    )


def test_cleanevfromentry() -> None:
    """Remove e.V. oder e. V. from association."""
    assert (  # nosec B101
        cleanevfromentry("TSA im VfL Pinneberg e. V.")
        == "TSA im VfL Pinneberg"
    )
    assert (  # nosec B101
        cleanevfromentry("TSA im VfL Pinneberg e.V.") == "TSA im VfL Pinneberg"
    )


def test_cleanevfrom_dtv_tsh_entry() -> None:
    """Remove e.V. oder e. V. from association."""
    assert (  # nosec B101
        cleanevfrom_dtv_tsh_entry("TSA im VfL Pinneberg e. V.")
        == "TSA im VfL Pinneberg"
    )
    assert (  # nosec B101
        cleanevfrom_dtv_tsh_entry("TSA im VfL Pinneberg e.V.")
        == "TSA im VfL Pinneberg"
    )
    assert (  # nosec B101
        cleanevfrom_dtv_tsh_entry("Rhythm & Dance e.V., Börnsen – TSH (3768)")
        == "Rhythm & Dance, Börnsen"
    )
    assert (  # nosec B101
        cleanevfrom_dtv_tsh_entry(
            "Tanzsportclub Rhythmus e.V., Bamberg – Bayern (3766)"
        )
        == "Tanzsportclub Rhythmus, Bamberg – Bayern (3766)"
    )


def test_clean_number_from_couple() -> None:
    """Remove starting number from couples entry in result list."""
    assert (
        clean_number_from_couple("Herr / Dame (1)") == "Herr / Dame"
    )  # nosec B101
    assert (
        clean_number_from_couple("Herr / Dame(1)") == "Herr / Dame"
    )  # nosec B101
