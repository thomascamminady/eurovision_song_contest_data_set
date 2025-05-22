import polars as pl
from bs4 import BeautifulSoup

from eurovision_song_contest_data_set.utils.logger import logger


def country_mapping(code: str) -> str:
    return {
        "al": "Albania",
        "am": "Armenia",
        "at": "Austria",
        "az": "Azerbaijan",
        "by": "Belarus",
        "be": "Belgium",
        "ba": "Bosnia and Herzegovina",
        "bg": "Bulgaria",
        "hr": "Croatia",
        "cy": "Cyprus",
        "dk": "Denmark",
        "ee": "Estonia",
        "fi": "Finland",
        "fr": "France",
        "ge": "Georgia",
        "de": "Germany",
        "gr": "Greece",
        "hu": "Hungary",
        "is": "Iceland",
        "il": "Israel",
        "it": "Italy",
        "lv": "Latvia",
        "lt": "Lithuania",
        "mt": "Malta",
        "md": "Moldova",
        "me": "Montenegro",
        "nl": "Netherlands",
        "mk": "North Macedonia",
        "no": "Norway",
        "pl": "Poland",
        "ru": "Russia",
        "rs": "Serbia",
        "si": "Slovenia",
        "es": "Spain",
        "se": "Sweden",
        "ch": "Switzerland",
        "ua": "Ukraine",
        "gb": "United Kingdom",
        "au": "Australia",
        "sm": "San Marino",
        "cz": "Czech Republic",
        "ie": "Ireland",
        "pt": "Portugal",
        "ro": "Romania",
        "wld": "Worldwide",
        "lu": "Luxembourg",
    }[code]


def parse_scoreboard_html(file: str) -> pl.DataFrame:
    with open(file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table", class_="scoreboard_table")

    # Extract countries that gave points (from the header row)
    header_cells = table.find("thead").find_all("td")  # type: ignore
    country_givers = [
        td.get("data-from")  # type: ignore
        for td in header_cells
        if td.has_attr("data-from")  # type: ignore
    ]

    rows = table.find("tbody").find_all("tr")  # type: ignore
    data = []

    for row in rows:
        cells = row.find_all("td")  # type: ignore
        if not cells or len(cells) < 4:
            continue

        country_receives = row.get("id", "").replace("tr_", "")  # type: ignore
        for i, td in enumerate(cells[4 : 4 + len(country_givers)]):
            country_gives = country_givers[i]
            text = td.get_text(strip=True)
            if text.isdigit():
                data.append(
                    {
                        "country_gives": country_gives,
                        "country_receives": country_receives,
                        "number_points": int(text),
                        "filename": file,
                    }
                )

    return pl.DataFrame(data)


def parse_all_scoreboard_html() -> pl.DataFrame:
    df_list = []
    for year in range(2016, 2026):
        if year == 2020:
            continue  # COVID-19
        logger.info(f"Parsing {year} scoreboard")
        for which in ["jury", "public"]:
            file = f"../data/{year}/{which}.html"
            df_list.append(
                parse_scoreboard_html(file).with_columns(
                    year=pl.lit(year),
                    which=pl.lit(which),
                )
            )
    df = pl.concat(df_list)

    return df.with_columns(
        country_gives_full=pl.col("country_gives").map_elements(
            country_mapping, return_dtype=pl.Utf8
        ),
        country_receives_full=pl.col("country_receives").map_elements(
            country_mapping, return_dtype=pl.Utf8
        ),
    )
