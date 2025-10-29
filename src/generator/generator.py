class BaseGenerator:
    """
    Classe de base pour tous les générateurs.

    Ajoutée automatiquement comme classe de base lors de la décoration.

    Exemple :
    ```
        @GeneratorRegistry.register("cmake", "Generate CMake CMakeLists.txt")
        class GeneratorCMake:
            pass
     ```
    """
    _generator_name :str= None
    _short_desc :str= None

    @classmethod
    def name(cls) -> str:
        return cls._generator_name
    
    @classmethod
    def short_desc(cls) -> str:
        return cls._short_desc
    
    @classmethod
    def create(cls, *args, **kwargs):
        """Instancie le générateur"""
        return cls(*args, **kwargs)

    @classmethod
    def add_cli_argument_to_parser(cls, argparse):
        """Doit être implémenté dans la sous-classe."""
        raise NotImplementedError(f"{cls.__name__} doit implémenter add_cli_argument_to_parser()")
    
    @classmethod
    def info(self):
        """Retourne une description basique du générateur."""
        return f"Générateur: {self.name} ({self.__class__.__name__})"
    
    def __str__(self):
        return f"{getattr(self, 'name')}"


class GeneratorRegistry:
    """
    GeneratorRegistry est une classe permettant d'enregistrer des générateurs 
    afin de pouvoir être appeler lors d'une commande de génération ou de build par exemple.

    Les generateurs sont automatiquement enregistré lorsqu'ils sont décorées avec @GeneratorRegistry.register:

    Exemple:
    ```
    @GeneratorRegistry.register("cmake", "Generate CMake CMakeLists.txt") # Le générateur `GeneratorCMake` est enregistrer sous le nom `cmake`
        class GeneratorCMake:
            pass
    ```
    """
    def __init__(self):
        self._registry = {}

    def register(self, name: str, short_desc:str):
        """
        Décorateur pour enregistrer une classe de générateur.

        Ce décorateur ajoute automatiquement la classe dans le registre des générateurs.
        Si la classe n'hérite pas déjà de BaseGenerator, elle est automatiquement étendue.

        Args:
            name (str): Nom unique du générateur.
            short_desc (str): Description courte du générateur, utile pour l'introspection et le CLI.

        Returns:
            Callable: Le décorateur qui prendra la classe et l'enregistrera.
        """
        def decorator(cls):
            if name in self._registry:
                raise RuntimeError(f"Le générateur '{name}' est déjà enregistré !")
            
            # Si la classe n'hérite pas déjà de BaseGenerator → on la "wrap"
            if not issubclass(cls, BaseGenerator):
                cls = type(cls.__name__, (BaseGenerator, cls), dict(cls.__dict__))

             # On ajoute un attribut utile pour introspection
            cls._generator_name = name
            cls._short_desc = short_desc
            self._registry[name] = cls

            return cls
        return decorator
    
    def get(self, name: str):
        """
        Récupère la classe associée à un générateur par son nom.

        Args:
            name (str): Nom unique du générateur à rechercher.

        Returns:
            Generateur|None: La classe du générateur si trouvée, sinon None.
        """
        return self._registry.get(name)

    def create(self, name: str, *args, **kwargs):
        """
        Instancie un générateur par son nom et retourne l'objet généré.

        Cette méthode utilise la méthode `create()` de la classe du générateur,
        qui doit être définie comme `@classmethod` dans la classe du générateur.

        Args:
            name (str): Nom unique du générateur à instancier.
            *args: Arguments positionnels à passer au constructeur du générateur.
            **kwargs: Arguments nommés à passer au constructeur du générateur.

        Returns:
            BaseGenerator: Une instance du générateur correspondant.

        Raises:
            KeyError: Si aucun générateur avec le nom fourni n'est trouvé.
        """
        cls = self.get(name)
        if cls is None:
            raise KeyError(f"Générateur '{name}' introuvable.")
        return cls.create()

    def __contains__(self, name):
        """
        Vérifie si un générateur avec le nom donné est enregistré.

        Args:
            name (str): Nom du générateur à vérifier.

        Returns:
            bool: True si le générateur existe dans le registre, False sinon.
        """
        return name in self._registry

    def __iter__(self):
        """
        Permet d’itérer sur les paires (nom, classe) des générateurs enregistrés.

        Returns:
            Iterator[Tuple[str, générateurs]]: Itérateur sur les couples (nom, classe).
        """
        return iter(self._registry.items())

    def keys(self):
        """
        Retourne les noms des générateurs enregistrés.

        Returns:
            KeysView[str]: Vue sur les clés du registre.
        """
        return self._registry.keys()

    def values(self):
        """
        Retourne les classes des générateurs enregistrés.

        Returns:
            ValuesView[générateurs]: Vue sur les valeurs du registre (les classes de générateurs).
        """
        return self._registry.values()

    def items(self):
        """
        Retourne les paires (nom, classes des générateurs) des générateurs enregistrés.

        Returns:
            ItemsView[Tuple[str, générateurs]]: Vue sur les items du registre.
        """
        return self._registry.items()

GeneratorRegistry = GeneratorRegistry()