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


# Charger l’étude Optuna
def load_study(study_name, storage_url):
    return optuna.load_study(study_name=study_name, storage=storage_url)

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
    df.show()

    return optimizer.trials_to_dataframe()


def get_class_by_name(class_name, module_name):
    try:
        # Parcourir tous les fichiers Python dans le dossier
        module_path = os.path.join(os.path.dirname(__file__), module_name)
        for file in os.listdir(module_path):
            if file.endswith(".py") and not file.startswith("__"):
                module = importlib.import_module(f"{module_name}.{file[:-3]}")
                if hasattr(module, class_name):
                    return getattr(module, class_name)
        raise ValueError(f"Classe '{class_name}' introuvable dans le module '{module_name}'.")
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement de la classe '{class_name}': {e}")

# Interface Streamlit
st.title("Visualisation et Création d’études")

# Section pour créer une nouvelle étude Optuna
st.header("Créer une nouvelle étude Optuna")
new_study_name = st.text_input("Nom de la nouvelle étude", "new_study")
storage_url = st.text_input("URL de stockage Optuna", "sqlite:///example.db")
optimizer_name = st.selectbox("Optimizer", ["OptunaOptimizer", "HyperoptOptimizer", "AllCombinationOptimizer"])
scenario_name = st.selectbox("Scenario", ["MatrixOperationScenario", "SleepScenario", "SparkFileFormatScenario"])
n_trials_optuna = st.number_input("Nombre d’essais Optuna", min_value=1, max_value=1000, value=50, step=1)
df = pd.DataFrame()


if st.button("Créer et optimiser une étude"):
    try:
        optimizer_class = get_class_by_name(optimizer_name,module_name="optimizer")
        scenario_class= get_class_by_name(scenario_name,module_name="scenarios")
        df = test_optimization(scenario_class, optimizer_class, "config_matrix.yaml")
        st.success(f"Étude avec '{optimizer_name}' créée et optimisée avec succès !")
    except ValueError as e:
        st.error(f"Erreur : {e}")
    except Exception as e:
        st.error(f"Erreur lors de la création de l’étude : {e}")

# Section pour visualiser une étude Optuna existante
st.header("Visualiser une étude existante")
#study_name = st.text_input("Nom de l’étude Optuna à visualiser", "example_study")

if st.button("Charger et afficher les essais Optuna"):
    try:

        # Afficher le DataFrame
        st.write("Données des essais Optuna :")
        st.dataframe(df)

        # Créer un graphique Plotly
        if not df.empty:
            fig = px.scatter(
                df,
                x="trial_number",
                y="score",
                color="trial_number",
                hover_data=df.columns,
                title="Scores des essais Optuna",
                labels={"trial_number": "Numéro d’essai", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("Aucun essai trouvé dans l’étude.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l’étude : {e}")

# Section pour créer une nouvelle étude Hyperopt
st.header("Créer une nouvelle étude Hyperopt")
n_trials_hyperopt = st.number_input("Nombre d’essais Hyperopt", min_value=1, max_value=1000, value=50, step=1)

if st.button("Créer et optimiser une étude Hyperopt"):
    try:
        # Définir l’espace de recherche
        space = {
            "x": hp.uniform("x", -10, 10),
            "y": hp.uniform("y", -10, 10),
        }

        # Lancer l’optimisation
        trials = Trials()
        best = fmin(
            fn=hyperopt_objective,
            space=space,
            algo=tpe.suggest,
            max_evals=n_trials_hyperopt,
            trials=trials,
        )

        # Convertir les résultats en DataFrame
        df = trials_to_dataframe_hyperopt(trials)

        # Afficher les résultats
        st.write("Meilleurs paramètres :", best)
        st.write("Données des essais Hyperopt :")
        st.dataframe(df)

        # Créer un graphique Plotly
        if not df.empty:
            fig = px.scatter(
                df,
                x="trial_number",
                y="score",
                color="trial_number",
                hover_data=df.columns,
                title="Scores des essais Hyperopt",
                labels={"trial_number": "Numéro d’essai", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("Aucun essai trouvé.")
    except Exception as e:
        st.error(f"Erreur lors de l’optimisation : {e}")