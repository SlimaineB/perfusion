# matrix_comparator.py
import os
import numpy as np
from scenario.perfusion_comparator import PerfusionComparator

MATRIX_SIZE = 1000  # Taille de la matrice

class MatrixComparator(PerfusionComparator ):

    def __init__(self):
        """
        Initializes the Matrix comparator.
        """
        super().__init__()
        # Fixer une graine pour la reproductibilité
        np.random.seed(42)
        self.matrix_size = MATRIX_SIZE
        print("Matrix Comparator initialized.")


    def deployment(self, trial=None):
        """
        Handles the deployment process for the Matrix comparator.
        """
        print("Deploying Matrix Comparator...")
        nombre_threads = trial.suggest_int("threads", 1, 20)  # Nombre de threads entre 1 et 20
        self.set_threads(nombre_threads)
        return nombre_threads


    def run(self):
        """
        Executes the Matrix comparator logic.
        """
        print("Running Matrix Comparator...")


        # Créer des matrices aléatoires
        taille_matrice =  self.matrix_size  # Taille des matrices
        matrice_A = np.random.rand(taille_matrice, taille_matrice)
        matrice_B = np.random.rand(taille_matrice, taille_matrice)

        # Multiplication matricielle
        resultat = np.dot(matrice_A, matrice_B)

        return resultat

    # Fonction pour définir le nombre de threads
    def set_threads(self, nombre_threads):
        os.environ["OMP_NUM_THREADS"] = str(nombre_threads)
        os.environ["MKL_NUM_THREADS"] = str(nombre_threads)


# Example usage
if __name__ == "__main__":
    comparator = MatrixComparator()
    comparator.deployment()
    comparator.run()