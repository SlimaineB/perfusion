import streamlit as st
import plotly.express as px
import pandas as pd
import optuna
from hyperopt import fmin, tpe, hp, Trials, STATUS_OK

# Charger l'étude Optuna
def load_study(study_name, storage_url):
    return optuna.load_study(study_name=study_name, storage=storage_url)

# Convertir les essais Optuna en DataFrame
def trials_to_dataframe(study):
    trials = study.trials
    data = []
    for trial in trials:
        trial_data = trial.params
        trial_data['score'] = trial.value
        trial_data['trial_number'] = trial.number
        data.append(trial_data)
    return pd.DataFrame(data)

# Fonction objective pour Optuna
def objective(trial):
    x = trial.suggest_float("x", -10, 10)
    y = trial.suggest_float("y", -10, 10)
    return (x - 2) ** 2 + (y + 3) ** 2

# Fonction objective pour Hyperopt
def hyperopt_objective(params):
    x = params["x"]
    y = params["y"]
    score = (x - 2) ** 2 + (y + 3) ** 2
    return {"loss": score, "status": STATUS_OK}

# Convertir les essais Hyperopt en DataFrame
def trials_to_dataframe_hyperopt(trials):
    data = []
    for trial in trials.trials:
        trial_data = trial["misc"]["vals"]
        trial_data = {k: v[0] for k, v in trial_data.items()}  # Extraire les valeurs
        trial_data["score"] = trial["result"]["loss"]
        trial_data["trial_number"] = trial["tid"]
        data.append(trial_data)
    return pd.DataFrame(data)

# Interface Streamlit
st.title("Visualisation et Création d'études Optuna et Hyperopt")

# Section pour créer une nouvelle étude Optuna
st.header("Créer une nouvelle étude Optuna")
new_study_name = st.text_input("Nom de la nouvelle étude", "new_study")
storage_url = st.text_input("URL de stockage Optuna", "sqlite:///example.db")
n_trials_optuna = st.number_input("Nombre d'essais Optuna", min_value=1, max_value=1000, value=50, step=1)

if st.button("Créer et optimiser une étude Optuna"):
    try:
        # Créer et optimiser une nouvelle étude
        study = optuna.create_study(study_name=new_study_name, direction="minimize", storage=storage_url, load_if_exists=True)
        study.optimize(objective, n_trials=n_trials_optuna)
        st.success(f"Étude '{new_study_name}' créée et optimisée avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la création de l'étude : {e}")

# Section pour visualiser une étude Optuna existante
st.header("Visualiser une étude Optuna existante")
study_name = st.text_input("Nom de l'étude Optuna à visualiser", "example_study")

if st.button("Charger et afficher les essais Optuna"):
    try:
        # Charger l'étude
        study = load_study(study_name, storage_url)
        df = trials_to_dataframe(study)

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
                labels={"trial_number": "Numéro d'essai", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("Aucun essai trouvé dans l'étude.")
    except Exception as e:
        st.error(f"Erreur lors du chargement de l'étude : {e}")

# Section pour créer une nouvelle étude Hyperopt
st.header("Créer une nouvelle étude Hyperopt")
n_trials_hyperopt = st.number_input("Nombre d'essais Hyperopt", min_value=1, max_value=1000, value=50, step=1)

if st.button("Créer et optimiser une étude Hyperopt"):
    try:
        # Définir l'espace de recherche
        space = {
            "x": hp.uniform("x", -10, 10),
            "y": hp.uniform("y", -10, 10),
        }

        # Lancer l'optimisation
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
                labels={"trial_number": "Numéro d'essai", "score": "Score"}
            )
            st.plotly_chart(fig)
        else:
            st.warning("Aucun essai trouvé.")
    except Exception as e:
        st.error(f"Erreur lors de l'optimisation : {e}")