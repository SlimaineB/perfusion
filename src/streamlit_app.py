import os
import streamlit as st
import plotly.express as px
import pandas as pd
import optuna
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK
import yaml
import importlib

from optimizer.optuna_optimizer import OptunaOptimizer
from optimizer.hyperopt_optimizer import HyperoptOptimizer
from optimizer.allcombination_optimizer import AllCombinationOptimizer
from scenarios.matrix_operation_scenario import MatrixOperationScenario



def get_class_by_name(class_name, module_name):
    try:
        # Browse all Python files in the folder
        module_path = os.path.join(os.path.dirname(__file__), module_name)
        for file in os.listdir(module_path):
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"{module_name}.{file[:-3]}")
                if hasattr(module, class_name):
                    return getattr(module, class_name)
        raise ValueError(f"Class '{class_name}' not found in module '{module_name}'.")
    except Exception as e:
        raise ValueError(f"Error while loading class '{class_name}': {e}")


def test_optimization(scenario_class, optimizer_class, config_file, n_trials=10, max_evals=10):
    # Load configuration
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    # Initialize scenario
    scenario = scenario_class()

    # Optimizer
    optimizer = optimizer_class(scenario.run, config)
    if(optimizer_class == OptunaOptimizer):
        optimizer.optimize(n_trials=n_trials, direction="minimize")
    elif(optimizer_class == HyperoptOptimizer):
        optimizer.optimize(max_evals=max_evals)
    elif(optimizer_class == AllCombinationOptimizer):
        optimizer.optimize()

    print(f"Best parameters of {scenario_class.__name__} with {optimizer_class.__name__}: {optimizer.get_best_params()}")

    df = optimizer.trials_to_dataframe()



    return df



# Streamlit Interface
st.title("Visualize and Create Study")

# Section to create a new Optuna study
st.header("Launch Study")
optimizer_name = st.selectbox("Optimizer", ["OptunaOptimizer", "HyperoptOptimizer", "AllCombinationOptimizer"])
scenario_name = st.selectbox("Scenario", ["MatrixOperationScenario", "SleepScenario", "SparkFileFormatScenario"])
#n_trials_optuna = st.number_input("Number of Optuna trials", min_value=1, max_value=1000, value=50, step=1)


if st.button("Create and Optimize Study"):
    try:
        optimizer_class = get_class_by_name(optimizer_name,module_name="optimizer")
        scenario_class= get_class_by_name(scenario_name,module_name="scenarios")
        df = test_optimization(scenario_class, optimizer_class, "config_matrix.yaml")
        st.success(f"Study with '{optimizer_name}' created and optimized successfully!")
        st.write("Trials data:")
        st.dataframe(df)
        
        # Create a Plotly chart
        if not df.empty:
            fig = px.scatter(
                df,
                x="trial_number",
                y="score",
                color="trial_number",
                hover_data=df.columns,
                title="Optuna Trials Scores",
                labels={"trial_number": "Trial Number", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("No trials found in the study.")


    except ValueError as e:
        st.error(f"Error: {e}")
    except Exception as e:
        st.error(f"Error while creating the study: {e}")

# Section to visualize an existing Optuna study
st.header("Visualize an existing study")
#study_name = st.text_input("Name of the Optuna study to visualize", "example_study")

if st.button("Load and display Optuna trials"):
    try:

        # Display the DataFrame
        st.write("Trials data:")
        st.dataframe(df)

        # Create a Plotly chart
        if not df.empty:
            fig = px.scatter(
                df,
                x="trial_number",
                y="score",
                color="trial_number",
                hover_data=df.columns,
                title="Optuna Trials Scores",
                labels={"trial_number": "Trial Number", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("No trials found in the study.")
    except Exception as e:
        st.error(f"Error while loading the study: {e}")

