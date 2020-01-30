# -*- coding: utf-8 -*-
"""
packaging base module.
"""

from pyrin.core.context import CoreObject
from pyrin.settings.static import DEFAULT_COMPONENT_KEY


class Package(CoreObject):
    """
    base package class.
    all application python packages should be subclassed from this.
    except some base packages like `application`, `core` and `utils` that
    should not implement Package class.
    """

    # the name of the package.
    # example: `pyrin.api`.
    # should get it from `__name__` for each package.
    NAME = None

    # list of all packages that this package is dependent
    # on them and should be loaded after all of them.
    # example: ['pyrin.logging', 'pyrin.config']
    # notice that all dependencies on `pyrin.application`
    # and `pyrin.packaging` should not be added to this list
    # because those two packages will be loaded at the beginning
    # and are always available before any other package gets loaded.
    DEPENDS = []

    # component name should be unique for each package unless it's intended
    # to replace an already available one. it should be fully qualified name
    # omitting the root application package name (for example `pyrin`), pointing to
    # a real file inside the package (omitting `.py` extension).
    # for example: `api.component` or `security.session.component` or 'my_package.my_component'
    # packages that need to extend (replace) an already available package, must
    # be subclassed from parent package and should not set this attribute.
    COMPONENT_NAME = None

    # component custom key should be unique for each instance unless it's intended
    # to replace an already available one.
    # custom key usage is when we want to expose different implementations
    # based on request context.
    COMPONENT_CUSTOM_KEY = DEFAULT_COMPONENT_KEY

    # all configuration stores that should be loaded by this package.
    CONFIG_STORE_NAMES = []

    def load_configs(self, config_services):
        """
        loads all required configs of this package.

        :param Module config_services: configuration services dependency.
                                       to be able to overcome circular dependency problem,
                                       we should inject configuration services dependency
                                       into this method. because all other packages are
                                       referenced `packaging.context` module in them, so we
                                       can't import `pyrin.configuration.services` in this
                                       module. this is more beautiful in comparison to
                                       importing it inside this method.
        """

        if len(self.CONFIG_STORE_NAMES) > 0:
            config_services.load_configurations(*self.CONFIG_STORE_NAMES,
                                                ignore_on_existed=True)

        self._load_configs(config_services)

    def _load_configs(self, config_services):
        """
        loads all required configs of this package.
        this method is intended for overriding by
        subclasses to do custom configurations.

        :param Module config_services: configuration services dependency.
                                       to be able to overcome circular dependency problem,
                                       we should inject configuration services dependency
                                       into this method. because all other packages are
                                       referenced `packaging.context` module in them, so we
                                       can't import `pyrin.configuration.services` in this
                                       module. this is more beautiful in comparison to
                                       importing it inside this method.
        """
        pass
