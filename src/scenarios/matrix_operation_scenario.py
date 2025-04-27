import numpy as np
from .base_scenario import BaseScenario

class MatrixOperationScenario(BaseScenario):
    def __init__(self):
        super().__init__()
        # Initialisation spécifique au scénario MatrixOperation

    def run(self, **params):
        """
        Implémentation de la méthode run pour le scénario MatrixOperation.
        """
        # Logique spécifique pour exécuter le scénario avec les paramètres donnés
        print("Running MatrixOperationScenario with params:", params)
        operation_type = params.get('operation_type')
        matrix_size = int(params.get('matrix_size'))

        matrice_A = np.random.rand(matrix_size, matrix_size)
        matrice_B = np.random.rand(matrix_size, matrix_size)

        if operation_type == "add":
            resultat = np.add(matrice_A, matrice_B)
        elif operation_type == "multiply":
            resultat = np.dot(matrice_A, matrice_B)
        else:
            raise ValueError("Invalid operation type. Use 'add' or 'multiply'.")
        return resultat.size