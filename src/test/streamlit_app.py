import streamlit as st
import plotly.express as px
import pandas as pd
import optuna

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

# Interface Streamlit
st.title("Visualisation et Création d'études Optuna")

# Section pour créer une nouvelle étude
st.header("Créer une nouvelle étude")
new_study_name = st.text_input("Nom de la nouvelle étude", "new_study")
storage_url = st.text_input("URL de stockage Optuna", "sqlite:///example.db")
n_trials = st.number_input("Nombre d'essais", min_value=1, max_value=1000, value=50, step=1)

if st.button("Créer et optimiser une étude"):
    try:
        # Créer et optimiser une nouvelle étude
        study = optuna.create_study(study_name=new_study_name, direction="minimize", storage=storage_url, load_if_exists=True)
        study.optimize(objective, n_trials=n_trials)
        st.success(f"Étude '{new_study_name}' créée et optimisée avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la création de l'étude : {e}")

# Section pour visualiser une étude existante
st.header("Visualiser une étude existante")
study_name = st.text_input("Nom de l'étude à visualiser", "example_study")

if st.button("Charger et afficher les essais"):
    try:
        # Charger l'étude
        study = load_study(study_name, storage_url)
        df = trials_to_dataframe(study)

        # Afficher le DataFrame
        st.write("Données des essais :")
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