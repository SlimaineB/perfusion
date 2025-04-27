import numpy as np

class MatrixOperationScenario:
    def run(self, **kwargs):
        operation_type = kwargs.get('operation_type')
        matrix_size = int(kwargs.get('matrix_size'))

        matrice_A = np.random.rand(matrix_size, matrix_size)
        matrice_B = np.random.rand(matrix_size, matrix_size)

        if operation_type == "add":
            resultat = np.add(matrice_A, matrice_B)
        elif operation_type == "multiply":
            resultat = np.dot(matrice_A, matrice_B)
        else:
            raise ValueError("Invalid operation type. Use 'add' or 'multiply'.")
        return resultat.size