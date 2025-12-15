from abc import ABC, abstractmethod

from kiss_parser import KissParser
from platform_target import PlatformTarget
from project.project import Project

class BaseRunner(ABC):
    """
    Classe de base pour tous les runner.

    Ajoutée automatiquement comme classe de base lors de la décoration.

    Exemple :
    ```
        @RunnerRegistry.register("cmake", "Run project built with cmake")
        class RunnerCMake:
            pass
     ```
    """
    _name :str= None
    _short_desc :str= None

    @abstractmethod
    def run(self, args : KissParser, project: Project):
        pass

    @classmethod
    def name(cls) -> str:
        return cls._name
    
    @classmethod
    def short_desc(cls) -> str:
        return cls._short_desc
    
    @classmethod
    def create(cls, *args, **kwargs):
        """Instancie le runner"""
        return cls(*args, **kwargs)

    @classmethod
    def add_cli_argument_to_parser(cls, argparse):
        """Doit être implémenté dans la sous-classe."""
        raise NotImplementedError(f"{cls.__name__} doit implémenter add_cli_argument_to_parser()")
    
    @classmethod
    def info(self):
        """Retourne une description basique du runner."""
        return f"Runner: {self.name} ({self.__class__.__name__})"
    
    def __str__(self):
        return f"{getattr(self, 'name')}"
    


class RunnerRegistry:
    """
    RunnerRegistry est une classe permettant d'enregistrer des runner 
    afin de pouvoir être appeler lors d'une commande de runner ou de build par exemple.

    Les Runners sont automatiquement enregistré lorsqu'ils sont décorées avec @RunnerRegistry.register:

    Exemple:
    ```
    @RunnerRegistry.register("cmake", "Run project built with cmake") # Le runner `RunnerCMake` est enregistrer sous le nom `cmake`
        class GeneratorCMake:
            pass
    ```
    """
    def __init__(self):
        self._registry = {}

    def register(self, name: str, short_desc:str):
        """
        Décorateur pour enregistrer une classe de runner.

        Ce décorateur ajoute automatiquement la classe dans le registre des runner.
        Si la classe n'hérite pas déjà de BaseRunner, elle est automatiquement étendue.

        Args:
            name (str): Nom unique du runner.
            short_desc (str): Description courte du runner, utile pour l'introspection et le CLI.

        Returns:
            Callable: Le décorateur qui prendra la classe et l'enregistrera.
        """
        def decorator(cls):
            if name in self._registry:
                raise RuntimeError(f"Le runner '{name}' est déjà enregistré !")
            
            # Si la classe n'hérite pas déjà de BaseRunner → on la "wrap"
            if not issubclass(cls, BaseRunner):
                cls = type(cls.__name__, (BaseRunner, cls), dict(cls.__dict__))

             # On ajoute un attribut utile pour introspection
            cls._name = name
            cls._short_desc = short_desc
            self._registry[name] = cls

            return cls
        return decorator
    
    def get(self, name: str):
        """
        Récupère la classe associée à un runner par son nom.

        Args:
            name (str): Nom unique du runner à rechercher.

        Returns:
            Runner|None: La classe du runner si trouvée, sinon None.
        """
        return self._registry.get(name)

    def create(self, name: str, *args, **kwargs):
        """
        Instancie un runner par son nom et retourne l'objet généré.

        Cette méthode utilise la méthode `create()` de la classe du runner,
        qui doit être définie comme `@classmethod` dans la classe du runner.

        Args:
            name (str): Nom unique du runner à instancier.
            *args: Arguments positionnels à passer au constructeur du runner.
            **kwargs: Arguments nommés à passer au constructeur du runner.

        Returns:
            BaseGenerator: Une instance du runner correspondant.

        Raises:
            KeyError: Si aucun runner avec le nom fourni n'est trouvé.
        """
        cls = self.get(name)
        if cls is None:
            raise KeyError(f"runner '{name}' introuvable.")
        return cls.create(*args, **kwargs)

    def __contains__(self, name):
        """
        Vérifie si un runner avec le nom donné est enregistré.

        Args:
            name (str): Nom du runner à vérifier.

        Returns:
            bool: True si le runner existe dans le registre, False sinon.
        """
        return name in self._registry

    def __iter__(self):
        """
        Permet d’itérer sur les paires (nom, classe) des builders enregistrés.

        Returns:
            Iterator[Tuple[str, builders]]: Itérateur sur les couples (nom, classe).
        """
        return iter(self._registry.items())

    def keys(self):
        """
        Retourne les noms des builders enregistrés.

        Returns:
            KeysView[str]: Vue sur les clés du registre.
        """
        return self._registry.keys()

    def values(self):
        """
        Retourne les classes des builders enregistrés.

        Returns:
            ValuesView[builders]: Vue sur les valeurs du registre (les classes de builders).
        """
        return self._registry.values()

    def items(self):
        """
        Retourne les paires (nom, classes des builders) des builders enregistrés.

        Returns:
            ItemsView[Tuple[str, builders]]: Vue sur les items du registre.
        """
        return self._registry.items()

RunnerRegistry = RunnerRegistry()