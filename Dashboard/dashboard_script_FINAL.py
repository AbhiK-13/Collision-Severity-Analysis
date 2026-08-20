import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Vehicle Collisions Dataset Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Font
# ---------------------------------------------------------------------------
# Swap FONT_NAME / FONT_IMPORT for any other Google Font if you'd like a
# different look - https://fonts.google.com has the import snippets.
FONT_NAME = "Space Grotesk"
FONT_IMPORT = "family=Space+Grotesk:wght@400;500;700"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?{FONT_IMPORT}&display=swap');

    html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stMetric,
    .stTabs, .stExpander, .stSelectSlider, .stSlider, table {{
        font-family: '{FONT_NAME}', sans-serif;
    }}
    </style>
    """,
    unsafe_allow_html=True,
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
        st.warning(f"Missing file: `{path}` - re-run the notebook to generate it.")


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
with st.expander("Data Cleaning"):
    st.header("Data Cleaning")

    st.subheader("Merging separate datasets", divider="blue")
    st.write(
        """When merging the datasets together, the ID variables (`collision_index` and
        `collision_ref_no`) had values stored as different Python types - the same
        issue affected the `generic_make_model` variable in the vehicles dataset.
        This matters because observations sharing the same `collision_index` would
        not have merged correctly if their key columns were stored as different
        object types. Forcing a consistent data type for these variables avoided
        creating duplicate rows or silently losing observations."""
    )

    st.subheader("Removing duplicates", divider="blue")
    st.write("There were no duplicates in the data.")

    st.subheader("Missing values: how they're coded", divider="blue")
    st.write(
        """Missing values in this dataset are coded as `-1`, but inconsistently:
        some columns store it as the integer `-1`, others as the string `"-1"`.
        Both had to be checked for separately when auditing how much data was
        missing per column, otherwise string-coded missingness would have been
        silently ignored."""
    )
    st.write(
        """Simply dropping every row with at least one missing value was tested
        as a baseline and turned out to remove a substantial share of the
        dataset - far too costly for a modelling exercise like this one, so a
        proper imputation strategy was needed instead. The one exception is the
        outcome variable, `collision_severity`: rows missing this value were
        dropped outright, since there's no sound way to impute the thing you're
        trying to predict."""
    )

    st.subheader("Feature engineering: date and time", divider="blue")
    st.write(
        """The raw `date` and `time` columns were parsed and split into more
        usable components: `year`, `month`, and `dayofweek` from the date, and
        `hour` from the time. The original `date` and `time` columns were then
        dropped to avoid duplicating the same information in two forms."""
    )

    st.subheader("Imputation: training data", divider="blue")
    st.write(
        """For the training set, missing values were imputed using **MICE**
        (Multiple Imputation with Chained Equations), via the `miceforest`
        package. MICE fits a regression model per variable and predicts each
        variable's missing values from the other variables in the dataset,
        which tends to preserve relationships between variables better than a
        simple mode/median fill. Before running MICE, high-cardinality identifier
        columns (`lsoa_of_accident_location`, `lsoa_of_casualty`,
        `lsoa_of_driver`, and the ID columns themselves) were set aside, and
        rare categories (fewer than 150 occurrences) in the remaining
        categorical columns were grouped into a single `RARE_CATEGORY` label
        to keep the imputation model manageable."""
    )

    st.subheader("Imputation: test data", divider="blue")
    st.write(
        """Running the same MICE procedure on the test set was impractical -
        it needed more memory than was available. Instead, the test set's
        numerical features were filled using the **median** from the
        (imputed) training data, and categorical features were filled using
        the **mode** from the training data. Categorical test values that
        didn't appear in the training categories were mapped to
        `RARE_CATEGORY` (or left missing if no such category existed), so the
        train and test sets always share a consistent set of category
        labels."""
    )

    st.subheader("Splitting into train / test", divider="blue")
    st.write(
        """Rather than a random split, the data was split **chronologically**:
        all collisions before 2024 form the training set, and collisions from
        2024 form the test set. This mirrors how the models would actually be
        used in practice - predicting future collisions from past data - and
        avoids leaking information from the future into training."""
    )

    st.subheader("Other", divider="blue")
    st.write(
        """Other data cleaning steps included removing irrelevant variables,
        and variables that were missing for all observations. Numeric features
        were also cast to `float32` (rather than 64-bit) to reduce memory
        usage across a dataset of this size."""
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
        ["Overall Severity", "Where", "Who", "What"]
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
            have been increasing - this could signal a shift toward riskier driving,
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
            "Percentage of collisions by severity, split by urban/rural area",
        )
        st.write(
            """"Slight" is the most common severity level in both urban and rural
            areas. Interestingly, a greater proportion of rural collisions are fatal
            - though this may simply reflect the fact that rural areas see fewer
            collisions overall, so each one carries more weight in the percentages."""
        )

    # -- Who -------------------------------------------------------------------
    with who_tab:
        st.subheader("Age of driver", divider="green")
        show_image(
            "severity_driver_age_heatmap.png",
            "Percentage of collisions by severity and driver age band, 2020-2024",
        )
        st.write(
            """Older drivers are responsible for a lower proportion of accidents
            overall - fatal accidents are mostly caused by drivers aged 26-45.
            Interestingly, the age profile of fatal accidents appears to be shifting
            younger over time: the 21-25 age group accounts for a growing share of
            fatal accidents, while the 26-35 and 36-45 groups' shares are declining."""
        )

        st.subheader("Age of casualty", divider="green")
        show_image(
            "severity_casualty_age_heatmap.png",
            "Percentage of collisions by severity and casualty age band, 2020-2024",
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
            """From 2020-2023, most collisions were caused by drivers in the
            40th-50th deprivation percentile. This may partly reflect that the most
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
            "Distribution of vehicle age by severity and year (2020-2024)",
        )

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
with st.expander("Analysis"):
    st.header("Analysis")
    st.write(
        """Several models were evaluated on their ability to predict
        `collision_severity`, and on which variables best predict severity
        ahead of time. Predictors include location, road type, speed limit,
        vehicle characteristics, and driver/casualty demographics. Continuous
        predictors were standard-scaled, and nominal categorical predictors
        (e.g. `vehicle_type`, `propulsion_code`, `road_type`) were ordinal-
        encoded, with unseen categories mapped to a dedicated "unknown" code
        rather than causing an error. High-cardinality columns
        (`generic_make_model`, `local_authority_district`) had rare
        categories grouped together first, using the same logic as the
        data-cleaning step."""
    )

    st.subheader("Class imbalance", divider="violet")
    st.write(
        """The training data is skewed heavily toward "slight" injury
        collisions: **75.9% slight**, **22.2% serious**, and only **2.0%
        fatal**. Because of this, plain accuracy can be misleading - a model
        can score well just by mostly predicting the majority ("slight")
        class. Balanced accuracy and macro-F1 are reported alongside accuracy
        throughout, since both give equal weight to each class regardless of
        its size."""
    )

    ols_tab, lasso_tab, tree_tab, mlp_tab, robust_tab, compare_tab = st.tabs(
        [
            "OLS Regression",
            "LASSO",
            "Gradient-Boosted Tree",
            "Neural Network",
            "Robustness Checks",
            "Model Comparison",
        ]
    )

    with ols_tab:
        st.write(
            """A simple OLS regression was fit as a baseline, treating
            `collision_severity` as a continuous target. Performance was
            evaluated using out-of-sample R-squared and mean squared error
            (MSE) on the chronologically held-out 2024 test set."""
        )
        col1, col2 = st.columns(2)
        col1.metric("Out-of-sample R-squared", "-0.023")
        col2.metric("MSE", "0.252")
        st.write(
            """A negative out-of-sample R-squared means OLS performs *worse*
            than simply predicting the training mean for every observation -
            a sign that treating this ordinal, heavily imbalanced outcome as
            a plain continuous target isn't a good fit for the data."""
        )

    with lasso_tab:
        st.write(
            """A LASSO regression was fit next, which shrinks less-informative
            coefficients toward zero and can be used for feature selection.
            An arbitrarily chosen penalty (alpha = 5) was large enough to
            zero out most coefficients."""
        )
        col1, col2 = st.columns(2)
        col1.metric("Test R-squared (alpha = 5)", "0.0005")
        col2.metric("Test R-squared (cross-validated alpha)", "-0.029")
        st.write(
            """Cross-validation (`LassoCV`, searching alphas from 0.0001 to
            10) was used to pick the penalty properly rather than guessing -
            but the cross-validated model still performs slightly worse than
            predicting the mean. Like OLS, LASSO's core assumption (a
            continuous, linear target) is a poor match for this outcome
            variable."""
        )

    with tree_tab:
        st.write(
            """A gradient-boosted decision tree (`HistGradientBoostingClassifier`)
            was fit next, treating `collision_severity` as a classification
            target rather than a continuous one. A grid search over learning
            rate, tree depth, and number of boosting iterations selected
            **learning_rate = 0.1, max_depth = 5, max_iter = 200** (best
            cross-validated accuracy: 76.8%)."""
        )
        col1, col2 = st.columns(2)
        col1.metric("Test accuracy (initial model)", "73.5%")
        col2.metric("Test accuracy (tuned model)", "72.8%")
        st.write(
            """Interestingly, the tuned model's raw accuracy is slightly
            *lower* than the initial untuned one - but its per-class recall
            is far more balanced. The initial model predicted "slight" for
            almost everything (99.6% recall on slight, but only 1% recall on
            fatal and 2% on serious); the tuned model trades a little overall
            accuracy for meaningfully better recall on serious collisions
            (12%, up from 2%), which matters more in practice than raw
            accuracy given how imbalanced the classes are."""
        )
        st.write(
            """**Variable importance** (via permutation importance, which
            shuffles one predictor at a time and measures the resulting drop
            in test accuracy) showed that location, casualty type, and
            vehicle type were the strongest predictors of collision severity,
            with speed limit, casualty age, and road type playing a moderate
            role."""
        )

    with mlp_tab:
        st.write(
            """As a further non-linear benchmark, a feedforward neural
            network (a Multi-Layer Perceptron, with two hidden layers of 64
            and 32 neurons) was trained via backpropagation on the
            standardised, encoded features. Early stopping (holding out 10%
            of training data to monitor validation loss) was used to guard
            against overfitting, and a small grid search was run over network
            size and L2 regularisation strength."""
        )
        col1, col2 = st.columns(2)
        col1.metric("Test accuracy (baseline)", "73.5%")
        col2.metric("Test accuracy (tuned)", "73.5%")
        st.write(
            """The grid search's best parameters (`alpha = 0.0001`,
            `hidden_layer_sizes = (64, 32)`, cross-validated accuracy 76.1%)
            turned out to match the original baseline configuration, so
            tuning didn't change the result here. Like the untuned tree, the
            MLP leans heavily on predicting "slight": 100% recall on slight
            collisions, but only 1-2% recall on fatal and serious ones."""
        )
        st.write(
            """Since neural networks don't have built-in coefficients or
            feature importances, the same permutation importance approach
            used for the gradient-boosted tree was applied here too, as a
            check on whether the two models agree on which variables matter
            most."""
        )

    with robust_tab:
        st.subheader("Checking for leakage from casualty-level variables")
        st.write(
            """`age_of_casualty`, `sex_of_casualty`, and `casualty_type`
            describe the casualty *after* the collision has happened, and
            severity may be partly bound up with casualty type by definition
            (for example, pedestrian casualties tend to have different injury
            profiles to car occupants, independent of anything about the
            collision itself). The gradient-boosted tree was refit without
            these three variables to check how much of its predictive power
            comes from them specifically."""
        )
        col1, col2 = st.columns(2)
        col1.metric("Accuracy with casualty variables", "72.8%")
        col2.metric("Accuracy without casualty variables", "72.5%")
        st.write(
            """A drop of under 0.3 percentage points is small - these
            variables don't appear to be doing an outsized share of the
            predictive work, so leakage from them looks like a minor concern
            rather than a major one for this model."""
        )

        st.subheader("K-fold cross-validation")
        st.write(
            """A single chronological train/test split can be noisy. 5-fold
            stratified cross-validation on the training data gives a sense of
            how much the accuracy estimate above might vary under a
            different split."""
        )
        st.metric("CV accuracy (gradient-boosted tree)", "76.9% +/- 0.1%")
        st.write(
            "The tight standard deviation suggests the result is fairly stable."
        )

        st.subheader("SHAP explainability")
        st.write(
            """Permutation importance shows how much each variable matters
            overall, but not the direction of its effect. SHAP values
            decompose each individual prediction into a contribution from
            each feature, and are a natural complement to the importance
            plots - useful for spotting non-linearities or interactions the
            tree has picked up on. The Fatal class was inspected here as the
            highest-stakes outcome, though the Serious and Slight classes are
            worth checking too."""
        )

    with compare_tab:
        st.write(
            """Bringing the classification models together for a final
            comparison. Accuracy alone can be misleading given the class
            imbalance noted above, so balanced accuracy and macro-F1 are
            reported alongside it. OLS and LASSO are excluded here, since
            they were fit as regressions on a continuous target rather than
            as classifiers, so accuracy-style metrics aren't a fair
            comparison for them - their out-of-sample R-squared and MSE are
            reported separately in the OLS/LASSO tabs above."""
        )
        st.dataframe(
            {
                "Model": [
                    "Gradient-Boosted Tree",
                    "Gradient-Boosted Tree (no casualty vars)",
                    "Feedforward Neural Network",
                ],
                "Accuracy": ["0.728", "0.725", "0.735"],
                "Balanced Accuracy": ["0.361", "0.346", "0.342"],
                "Macro F1": ["0.350", "0.319", "0.302"],
            },
            use_container_width=True,
            hide_index=True,
        )
        st.write(
            """On raw accuracy, the neural network narrowly comes out ahead.
            But on balanced accuracy and macro-F1 - the fairer metrics given
            how skewed the classes are - the gradient-boosted tree (with
            casualty variables included) performs best, suggesting it does a
            comparatively better job of also predicting the rarer serious and
            fatal collisions rather than just defaulting to "slight"."""
        )
