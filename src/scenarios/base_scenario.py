class BaseScenario:
    def __init__(self):
        """
        Initialisation commune pour tous les scénarios.
        """
        pass

    def run(self, params):
        """
        Méthode à implémenter dans les classes enfants.
        Cette méthode doit exécuter le scénario avec les paramètres donnés.
        """
        raise NotImplementedError("La méthode 'run' doit être implémentée dans les classes enfants.")