from abc import ABC, abstractmethod

from kiss_parser import KissParser
from platform_target import PlatformTarget
from project.project import Project

class BaseBuilder(ABC):
    """
    Classe de base pour tous les builder.

    Ajoutée automatiquement comme classe de base lors de la décoration.

    Exemple :
    ```
        @BuilderRegistry.register("cmake", "Build CMake CMakeLists.txt")
        class BuilderCMake:
            pass
     ```
    """
    _name :str= None
    _short_desc :str= None

    @abstractmethod
    def build(self, args : KissParser, project: Project):
        pass

    @classmethod
    def name(cls) -> str:
        return cls._name
    
    @classmethod
    def short_desc(cls) -> str:
        return cls._short_desc
    
    @classmethod
    def create(cls, *args, **kwargs):
        """Instancie le builder"""
        return cls(*args, **kwargs)

    @classmethod
    def add_cli_argument_to_parser(cls, argparse):
        """Doit être implémenté dans la sous-classe."""
        raise NotImplementedError(f"{cls.__name__} doit implémenter add_cli_argument_to_parser()")
    
    @classmethod
    def info(self):
        """Retourne une description basique du builder."""
        return f"Builder: {self.name} ({self.__class__.__name__})"
    
    def __str__(self):
        return f"{getattr(self, 'name')}"
    


class BuilderRegistry:
    """
    BuilderRegistry est une classe permettant d'enregistrer des builder 
    afin de pouvoir être appeler lors d'une commande de builder ou de build par exemple.

    Les Builders sont automatiquement enregistré lorsqu'ils sont décorées avec @BuilderRegistry.register:

    Exemple:
    ```
    @GBuilderRegistry.register("cmake", "Build CMake CMakeLists.txt") # Le builder `BuilderCMake` est enregistrer sous le nom `cmake`
        class BuilderCMake:
            pass
    ```
    """
    def __init__(self):
        self._registry = {}

    def register(self, name: str, short_desc:str):
        """
        Décorateur pour enregistrer une classe de builder.

        Ce décorateur ajoute automatiquement la classe dans le registre des builder.
        Si la classe n'hérite pas déjà de BaseBuilder, elle est automatiquement étendue.

        Args:
            name (str): Nom unique du builder.
            short_desc (str): Description courte du builder, utile pour l'introspection et le CLI.

        Returns:
            Callable: Le décorateur qui prendra la classe et l'enregistrera.
        """
        def decorator(cls):
            if name in self._registry:
                raise RuntimeError(f"Le builder '{name}' est déjà enregistré !")
            
            # Si la classe n'hérite pas déjà de BaseBuilder → on la "wrap"
            if not issubclass(cls, BaseBuilder):
                cls = type(cls.__name__, (BaseBuilder, cls), dict(cls.__dict__))

             # On ajoute un attribut utile pour introspection
            cls._name = name
            cls._short_desc = short_desc
            self._registry[name] = cls

            return cls
        return decorator
    
    def get(self, name: str):
        """
        Récupère la classe associée à un builder par son nom.

        Args:
            name (str): Nom unique du builder à rechercher.

        Returns:
            Builder|None: La classe du builder si trouvée, sinon None.
        """
        return self._registry.get(name)

    def create(self, name: str, *args, **kwargs):
        """
        Instancie un builder par son nom et retourne l'objet généré.

        Cette méthode utilise la méthode `create()` de la classe du builder,
        qui doit être définie comme `@classmethod` dans la classe du builder.

        Args:
            name (str): Nom unique du builder à instancier.
            *args: Arguments positionnels à passer au constructeur du builder.
            **kwargs: Arguments nommés à passer au constructeur du builder.

        Returns:
            BaseGenerator: Une instance du builder correspondant.

        Raises:
            KeyError: Si aucun builder avec le nom fourni n'est trouvé.
        """
        cls = self.get(name)
        if cls is None:
            raise KeyError(f"builder '{name}' introuvable.")
        return cls.create(*args, **kwargs)

    def __contains__(self, name):
        """
        Vérifie si un builder avec le nom donné est enregistré.

        Args:
            name (str): Nom du builder à vérifier.

        Returns:
            bool: True si le builder existe dans le registre, False sinon.
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

BuilderRegistry = BuilderRegistry()