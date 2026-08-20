import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Vehicle Collisions Dataset Dashboard",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
# Folder containing the PNGs exported from 03_visualisations.ipynb.
# Update this if your Visualisations folder lives somewhere else relative
# to this script.
VIZ_DIR = Path("Visualisations")


def show_image(filename: str, caption: str = "", **kwargs):
    """Safely display an image, warning instead of crashing if it's missing."""
    path = VIZ_DIR / filename
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True, **kwargs)
    else:
        st.warning(f"Missing file: `{path}` — re-run the notebook to generate it.")


st.title("Vehicle Collisions Dataset Dashboard")

# ---------------------------------------------------------------------------
# About the dataset
# ---------------------------------------------------------------------------
with st.expander("About the Road Safety Open Dataset", expanded=True):
    st.header("About the Road Safety Open Dataset")
    st.write(
        """The Road Safety Open Dataset provides separate data for collisions, vehicles,
        and casualties for accidents. The data relates to personal injury collisions on
        public roads that have been reported to the police, and is released annually
        in late September. The ONS provides data as far back as 1979, providing the
        opportunity to conduct a rich exploration of the different predictors of
        various accidents."""
    )
    st.write("You can visit the Road Safety Open Dataset by clicking the button below.")
    data_url = "https://www.gov.uk/government/statistical-data-sets/road-safety-open-data"
    st.link_button("Visit the Road Safety Open Dataset page", data_url)

    col1, col2 = st.columns(2)
    col1.metric("Observations", "1,221,287")
    col2.metric("Variables", "93")

# ---------------------------------------------------------------------------
# Data cleaning
# ---------------------------------------------------------------------------
with st.expander("🧹 Data Cleaning"):
    st.header("Data Cleaning")

    st.subheader("Merging separate datasets", divider="blue")
    st.write(
        """When merging the datasets together, the ID variables (`collision_index` and
        `collision_ref_no`) had values stored as different Python types — the same
        issue affected the `generic_make_model` variable in the vehicles dataset.
        This matters because observations sharing the same `collision_index` would
        not have merged correctly if their key columns were stored as different
        object types. Forcing a consistent data type for these variables avoided
        creating duplicate rows or silently losing observations."""
    )

    st.subheader("Removing duplicates", divider="blue")
    st.write("There were no duplicates in the data.")

    st.subheader("Data imputation", divider="blue")
    st.write(
        """There are several ways to deal with missing data. Simply dropping
        observations with missing values was not a suitable option here, as it
        would have removed a substantial proportion of the dataset. Another
        common approach is filling missing values with the mode/median of each
        variable."""
    )
    st.write(
        """For this analysis, **MICE (Multiple Imputation with Chained Equations)**
        was used instead. This method fits a regression model per variable and predicts
        the missing values using information from the other variables in the
        dataset, which preserves relationships between variables better
        than simple mode/median imputation. This is especially important because simple mean/median imputation,
        whilst simple, can result in distributions that are more heavily skewed towards the mean/median, resulting
        in misguided visualisations and therefore misinformative recommendations."""
    )

    st.subheader("Recoding variables", divider="blue")
    st.write(
        """Categorical codes (e.g. severity, sex, age band, propulsion type) were
        mapped to human-readable labels for the purposes of analysis and
        visualisation. Temporal variables (such as day and time of accident) were 
        converted to a date-time format, where they were split into further variables 
        to allow for more comprehensive analysis of the timing of accidents."""
    )

    st.subheader("Other", divider="blue")
    st.write(
        """Other data cleaning steps included removing irrelevant variables, and removing
        variables that were missing for all observations."""
    )

# ---------------------------------------------------------------------------
# Exploratory Data Analysis
# ---------------------------------------------------------------------------
with st.expander("Exploratory Data Analysis", expanded=True):
    st.header("Exploratory Data Analysis")
    st.write(
        """This EDA investigates key questions relating to collisions and their
        severity, and how these trends have evolved over time:"""
    )
    st.markdown(
        """
- **WHERE** do they happen? e.g. urban vs rural areas
- **WHO** is involved? e.g. age, sex, and deprivation of drivers and casualties
- **WHAT** is involved? e.g. vehicle type and vehicle age
        """
    )

    overall_tab, where_tab, who_tab, what_tab = st.tabs(
        ["Overall Severity", " WHERE?" , " WHO? ", "WHAT?"]
    )

    # -- Overall severity ---------------------------------------------------
    with overall_tab:
        st.subheader("Distribution of collision severity", divider="green")
        col1, col2 = st.columns(2)
        with col1:
            show_image(
                "severity_distribution_across_time.png",
                "Collision counts by severity, by year",
            )
        with col2:
            show_image(
                "severity_trends_across_time.png",
                "Trend of collision severity over time",
            )
        st.write(
            """Most collisions are only slightly severe. Over time, the number of
            slightly severe collisions has been decreasing, while serious collisions
            have been increasing — this could signal a shift toward riskier driving,
            or a return to pre-COVID traffic and driving patterns."""
        )

        with st.expander("View each severity level individually"):
            c1, c2, c3 = st.columns(3)
            with c1:
                show_image("fatal_collisions_across_time.png", "Fatal collisions")
            with c2:
                show_image("serious_collisions_across_time.png", "Serious collisions")
            with c3:
                show_image("slight_collisions_across_time.png", "Slight collisions")

    # -- Where ---------------------------------------------------------------
    with where_tab:
        st.subheader("Urban vs. rural areas", divider="green")
        show_image(
            "severity_rural_urban_heatmap.png",
            "% of collisions by severity, split by urban/rural area",
        )
        st.write(
            """"Slight" is the most common severity level in both urban and rural
            areas. Interestingly, a greater proportion of rural collisions are fatal
            — though this may simply reflect the fact that rural areas see fewer
            collisions overall, so each one carries more weight in the percentages."""
        )

    # -- Who -------------------------------------------------------------------
    with who_tab:
        st.subheader("Age of driver", divider="green")
        show_image(
            "severity_driver_age_heatmap.png",
            "% of collisions by severity and driver age band, 2020–2024",
        )
        st.write(
            """Older drivers are responsible for a lower proportion of accidents
            overall — fatal accidents are mostly caused by drivers aged 26–45.
            Interestingly, the age profile of fatal accidents appears to be shifting
            younger over time: the 21–25 age group accounts for a growing share of
            fatal accidents, while the 26–35 and 36–45 groups' shares are declining."""
        )

        st.subheader("Age of casualty", divider="green")
        show_image(
            "severity_casualty_age_heatmap.png",
            "% of collisions by severity and casualty age band, 2020–2024",
        )

        st.subheader("Driver deprivation", divider="green")
        dep_year = st.select_slider(
            "Select year", options=[2020, 2021, 2022, 2023, 2024], key="dep_year"
        )
        show_image(
            f"severity_deprivation_pie_{dep_year}.png",
            f"Driver deprivation decile distribution, {dep_year}",
        )
        st.write(
            """From 2020–2023, most collisions were caused by drivers in the
            40th–50th deprivation percentile. This may partly reflect that the most
            deprived individuals are less likely to own a car, or may drive more
            cautiously, while the least deprived 10% simply make up a smaller
            share of drivers on the road."""
        )

        st.subheader("Sex of driver", divider="green")
        sex_all, sex_fatal, sex_serious, sex_slight = st.tabs(
            ["All", "Fatal", "Serious", "Slight"]
        )
        with sex_all:
            show_image("collision_sex.png", "All collisions by driver sex")
        with sex_fatal:
            show_image("collision_sex_fatal.png", "Fatal collisions by driver sex")
        with sex_serious:
            show_image("collision_sex_serious.png", "Serious collisions by driver sex")
        with sex_slight:
            show_image("collision_sex_slightly.png", "Slight collisions by driver sex")
        st.write(
            "Men have been responsible for more collisions in total from 2020 to 2024."
        )

    # -- What ------------------------------------------------------------------
    with what_tab:
        st.subheader("Vehicle propulsion type", divider="green")
        veh_year = st.select_slider(
            "Select year", options=[2020, 2021, 2022, 2023, 2024], key="veh_year"
        )
        show_image(
            f"vehicle_type_dist_{veh_year}.png",
            f"Distribution of vehicle propulsion types, {veh_year}",
        )

        st.subheader("Vehicle age", divider="green")
        show_image(
            "collision_vehicle_age_dist.png",
            "Distribution of vehicle age by severity and year (2020–2024)",
        )

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
with st.expander("Analysis"):
    st.header("Analysis")
    st.write(
        """This section will summarise the modelling approaches used to predict
        collision severity."""
    )
    with st.expander("OLS Regression"):
        st.write("_Add OLS regression results and discussion here._")
    with st.expander("LASSO model"):
        st.write("_Add LASSO model results and discussion here._")
    with st.expander("Gradient Boosted Decision Tree"):
        st.write("_Add gradient boosted tree results and discussion here._")