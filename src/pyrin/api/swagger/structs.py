# -*- coding: utf-8 -*-
"""
swagger structs module.
"""

import re
import os

from uuid import UUID
from copy import deepcopy
from collections import defaultdict

from flask import current_app
from flasgger import Swagger
from flasgger.marshmallow_apispec import SwaggerView, convert_schemas
from flasgger.constants import OPTIONAL_FIELDS, OPTIONAL_OAS3_FIELDS
from flasgger.utils import extract_definitions, parse_definition_docstring, \
    get_vendor_extension_fields, merge_specs, parse_docstring, is_valid_method_view, \
    has_valid_dispatch_view_docs

import pyrin.database.paging.services as paging_services
import pyrin.configuration.services as config_services
import pyrin.processor.response.status.services as status_services
import pyrin.api.swagger.services as swagger_services

from pyrin.api.router.handlers.protected import ProtectedRoute
from pyrin.core.enumerations import HTTPMethodEnum, ClientErrorResponseCodeEnum
from pyrin.api.swagger.enumerations import ParameterAttributeEnum, ParameterLocationEnum, \
    ParameterTypeEnum, DocstringSectionEnum, ParameterFormatEnum


class ExtendedSwagger(Swagger):
    """
    extended swagger class.

    this class extends `Swagger` class to enable adding common
    schema attributes into registered specs.
    """

    DEFAULT_CONFIG = {
        "headers": [
        ],
        "specs": [
            {
                "endpoint": 'swagger',
                "route": '/swagger.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/swagger/"
    }

    def _get_parameters_section(self, swag):
        """
        gets parameters section from given swag info.

        :param dict swag: swag info.

        :rtype: list[dict]
        """

        return swag.setdefault(DocstringSectionEnum.PARAMETERS, [])

    def _get_responses_section(self, swag):
        """
        gets responses section from given swag info.

        :param dict swag: swag info.

        :rtype: dict
        """

        return swag.setdefault(DocstringSectionEnum.RESPONSES, {})

    def _get_security_section(self, swag):
        """
        gets security section from given swag info.

        :param dict swag: swag info.

        :rtype: list[dict]
        """

        return swag.setdefault(DocstringSectionEnum.SECURITY, [])

    def _get_tags_section(self, swag):
        """
        gets tags section from given swag info.

        :param dict swag: swag info.

        :rtype: list[str]
        """

        return swag.setdefault(DocstringSectionEnum.TAGS, [])

    def _get_parameter(self, name, parameters):
        """
        gets the parameter with given name from provided params.

        it may return None if it does not exist.

        :param str name: parameter name.
        :param list[dict] parameters: list of parameters.

        :rtype: dict
        """

        for param in parameters:
            if param.get(ParameterAttributeEnum.NAME) == name:
                return param

        return None

    def _add_parameter(self, parameters, name, type_, in_, **options):
        """
        adds a new parameter into given parameters.

        if a parameter with the same name is already
        existed, the new parameter will be ignored.

        :param list[dict] parameters: list of parameters.
        :param str name: new parameter name.
        :param str type_: new parameter type.
        :enum type_:
            INTEGER = 'integer'
            NUMBER = 'number'
            BOOLEAN = 'boolean'
            STRING = 'string'
            ARRAY = 'array'
            OBJECT = 'object'

        :param in_: new parameter place.
        :enum in_:
            PATH = 'path'
            QUERY = 'query'
            JSON = 'json'
            BODY = 'body'

        :keyword bool required: specifies that this parameter is required.
                                defaults to False if not provided.

        :keyword str description: new parameter description.
                                  defaults to an empty string if not provided.

        :keyword str format: format to be used for given type.
        :enum format:
            UUID = 'uuid'
            EMAIL = 'email'
            DATE = 'date'
            DATE_TIME = 'date-time'
            PASSWORD = 'password'
            BYTE = 'byte'
            URI = 'uri'
            HOSTNAME = 'hostname'
            IPV4 = 'ipv4'
            IPV6 = 'ipv6'
            DOUBLE = 'double'
            FLOAT = 'float'

        :keyword bool add_first: add the new parameter at the beginning of
                                 available params. defaults to False if not
                                 provided and the new param will be appended
                                 to the end.

        :returns: a value indicating that the new param is added.
        :rtype: bool
        """

        param = self._get_parameter(name, parameters)
        if param is not None:
            return False

        add_first = options.get('add_first', False)
        format_ = options.get('format')
        required = options.get('required', False)
        description = options.get('description')
        new_param = dict()
        new_param[ParameterAttributeEnum.NAME] = name
        new_param[ParameterAttributeEnum.REQUIRED] = required
        new_param[ParameterAttributeEnum.IN] = in_

        if type_ is not None:
            new_param[ParameterAttributeEnum.TYPE] = type_

        if format_ is not None:
            new_param[ParameterAttributeEnum.FORMAT] = format_

        if description is not None:
            new_param[ParameterAttributeEnum.DESCRIPTION] = description

        if add_first is True:
            parameters.insert(0, new_param)
        else:
            parameters.append(new_param)

        return True

    def _get_param_location(self, name, rule, verb):
        """
        gets the location that this parameter must be placed in a request.

        if the parameter is from url params of given rule, it will return `path`.
        if the verb is one of `get`, 'head' or 'options', it will return `query`.
        otherwise it will return `json`.

        :param st name: parameter name.
        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this parameter.
        :param str verb: http method name.

        :rtype: str
        """

        if name in rule.arguments:
            return ParameterLocationEnum.PATH

        if verb.upper() in (HTTPMethodEnum.HEAD,
                            HTTPMethodEnum.GET,
                            HTTPMethodEnum.OPTIONS):
            return ParameterLocationEnum.QUERY

        return ParameterLocationEnum.JSON

    def _fix_metadata(self, rule, verb, swag):
        """
        fixes metadata of given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        self._add_or_fix_required_parameters(rule, verb, swag)
        self._fix_optional_parameters(rule, verb, swag)
        self._add_paging_parameters(rule, verb, swag)
        self._add_locale_parameter(rule, verb, swag)
        self._add_timezone_parameter(rule, verb, swag)
        self._add_security_definitions(rule, verb, swag)
        self._add_authentication_failed_response(rule, verb, swag)
        self._add_permission_denied_response(rule, verb, swag)
        self._add_successful_response(rule, verb, swag)
        self._add_tags(rule, verb, swag)

    def _add_locale_parameter(self, rule, verb, swag):
        """
        adds locale parameter into given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        params = self._get_parameters_section(swag)
        self._add_parameter(params,
                            current_app.request_class.LOCALE_PARAM_NAME,
                            ParameterTypeEnum.STRING,
                            ParameterLocationEnum.QUERY,
                            required=False,
                            description='request locale to be sent. '
                                        'for example en, fa, fr ...')

    def _add_timezone_parameter(self, rule, verb, swag):
        """
        adds timezone parameter into given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        params = self._get_parameters_section(swag)
        self._add_parameter(params,
                            current_app.request_class.TIMEZONE_PARAM_NAME,
                            ParameterTypeEnum.STRING,
                            ParameterLocationEnum.QUERY,
                            required=False,
                            description='request timezone to be sent. '
                                        'for example UTC, Asia/Tehran ...')

    def _add_paging_parameters(self, rule, verb, swag):
        """
        adds paging parameters into given swag info if provided rule is paged.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        if rule.is_paged is True:
            page, page_size = paging_services.get_paging_param_names()
            params = self._get_parameters_section(swag)
            self._add_parameter(params, page,
                                ParameterTypeEnum.INTEGER,
                                ParameterLocationEnum.QUERY,
                                required=False, description='page number to be get.')
            self._add_parameter(params, page_size,
                                ParameterTypeEnum.INTEGER,
                                ParameterLocationEnum.QUERY,
                                required=False, description='page size to be get.')

    def _add_or_fix_required_parameters(self, rule, verb, swag):
        """
        adds or fixes required parameters into given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        params = self._get_parameters_section(swag)
        required_args = rule.required_arguments.union(rule.arguments)
        for name in required_args:
            type_ = None
            format_ = None
            in_ = self._get_param_location(name, rule, verb)
            if in_ == ParameterLocationEnum.PATH:
                argument_type = rule.get_argument_type(name)
                if argument_type is int:
                    type_ = ParameterTypeEnum.INTEGER
                elif argument_type is float:
                    type_ = ParameterTypeEnum.NUMBER
                    format_ = ParameterFormatEnum.FLOAT
                elif argument_type is str:
                    type_ = ParameterTypeEnum.STRING
                elif argument_type is UUID:
                    type_ = ParameterTypeEnum.STRING
                    format_ = ParameterFormatEnum.UUID

            added = self._add_parameter(params, name, type_, in_,
                                        required=True, add_first=True,
                                        format=format_)
            if added is False:
                param = self._get_parameter(name, params)
                if param is not None:
                    param[ParameterAttributeEnum.REQUIRED] = True
                    param.setdefault(ParameterAttributeEnum.IN, in_)
                    if type_ is not None:
                        param.setdefault(ParameterAttributeEnum.TYPE, type_)
                    if format_ is not None:
                        param.setdefault(ParameterAttributeEnum.FORMAT, format_)

    def _fix_optional_parameters(self, rule, verb, swag):
        """
        fixes metadata of optional parameters in given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        required_args = rule.required_arguments.union(rule.arguments)
        params = self._get_parameters_section(swag)
        for item in params:
            name = item.get(ParameterAttributeEnum.NAME)
            if name in required_args:
                continue

            item.setdefault(ParameterAttributeEnum.REQUIRED, False)
            in_ = self._get_param_location(name, rule, verb)
            item.setdefault(ParameterAttributeEnum.IN, in_)

    def _add_security_definitions(self, rule, verb, swag):
        """
        adds security definitions into given swag info if provided rule is protected.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        if isinstance(rule, ProtectedRoute):
            definitions = config_services.get_active('swagger', 'securityDefinitions')
            if definitions is not None and len(definitions) > 0:
                security = self._get_security_section(swag)
                for name in definitions:
                    item = dict()
                    item[name] = []
                    security.append(item)

    def _add_permission_denied_response(self, rule, verb, swag):
        """
        adds permission denied response into given swag info if provided rule is protected.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        if isinstance(rule, ProtectedRoute) and len(rule.permissions) > 0:
            responses = self._get_responses_section(swag)
            permission_denied = dict(description='you do not have the required '
                                                 'permissions to access this resource.')
            responses.setdefault(ClientErrorResponseCodeEnum.FORBIDDEN, permission_denied)

    def _add_authentication_failed_response(self, rule, verb, swag):
        """
        adds authentication failed response into given swag info if provided rule is protected.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        if isinstance(rule, ProtectedRoute):
            responses = self._get_responses_section(swag)
            authentication_failed = dict(description='user has not been authenticated.')
            responses.setdefault(ClientErrorResponseCodeEnum.UNAUTHORIZED, authentication_failed)

    def _add_successful_response(self, rule, verb, swag):
        """
        adds successful response into given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        status_code = rule.status_code
        if status_code is None:
            status_code = status_services.get_status_code(method=verb.upper())

        responses = self._get_responses_section(swag)
        success = dict(description='successful execution of service.')
        responses.setdefault(status_code, success)

    def _add_tags(self, rule, verb, swag):
        """
        adds required tags into given swag info.

        :param pyrin.api.router.handlers.base.RouteBase rule: related rule to this swag info.
        :param str verb: http method name.
        :param dict swag: swag info.
        """

        tags = swagger_services.get_tags(rule, verb.upper())
        if len(tags) > 0:
            tag_section = self._get_tags_section(swag)
            tag_section.extend(tags)

    def _is_flasgger_rule(self, rule):
        """
        gets a value indicating that this rule belongs to flasgger.

        :param pyrin.api.router.handlers.base.RouteBase rule: rule to be checked.

        :rtype: bool
        """

        flasgger_endpoint = config_services.get_active('swagger', 'endpoint')
        return rule.endpoint.startswith(flasgger_endpoint)

    def get_apispecs(self, endpoint='apispec_1'):
        """
        gets api specs for given endpoint.

        we have to duplicate this whole method to be able to hook
        into fetching api specs from docstrings.

        :param str endpoint: endpoint to get its api specs.

        :rtype: dict
        """

        if not self.app.debug and endpoint in self.apispecs:
            return self.apispecs[endpoint]

        spec = None
        for _spec in self.config['specs']:
            if _spec['endpoint'] == endpoint:
                spec = _spec
                break
        if not spec:
            raise RuntimeError('Can`t find specs by endpoint [{endpoint}], '
                               'check your flasgger`s configs.'
                               .format(endpoint=endpoint))

        data = {
            # try to get from config['SWAGGER']['info']
            # then config['SWAGGER']['specs'][x]
            # then config['SWAGGER']
            # then default
            'info': self.config.get('info') or {
                'version': spec.get(
                    'version', self.config.get('version', '0.0.1')
                ),
                'title': spec.get(
                    'title', self.config.get('title', 'A swagger API')
                ),
                'description': spec.get(
                    'description', self.config.get('description',
                                                   'powered by Flasgger')
                ),
                'termsOfService': spec.get(
                    'termsOfService', self.config.get('termsOfService',
                                                      '/tos')
                ),
            },
            'paths': self.config.get('paths') or defaultdict(dict),
            'definitions': self.config.get('definitions') or defaultdict(dict)
        }

        openapi_version = self.config.get('openapi')
        if openapi_version:
            data['openapi'] = openapi_version
        else:
            data['swagger'] = self.config.get('swagger') or self.config.get(
                'swagger_version', '2.0'
            )

        # Support extension properties in the top level config
        top_level_extension_options = get_vendor_extension_fields(self.config)
        if top_level_extension_options:
            data.update(top_level_extension_options)

        # if True schema ids will be prefixed by function_method_{id}
        # for backwards compatibility with <= 0.5.14
        prefix_ids = self.config.get('prefix_ids')

        if self.config.get('host'):
            data['host'] = self.config.get('host')
        if self.config.get('basePath'):
            data['basePath'] = self.config.get('basePath')
        if self.config.get('schemes'):
            data['schemes'] = self.config.get('schemes')
        if self.config.get('securityDefinitions'):
            data['securityDefinitions'] = self.config.get(
                'securityDefinitions'
            )

        def is_openapi3():
            """
            returns True if `openapi_version` is 3.
            """

            return openapi_version and openapi_version.split('.')[0] == '3'

        if is_openapi3():
            # enable oas3 fields when openapi_version is 3.*.*
            optional_oas3_fields = self.config.get(
                'optional_oas3_fields') or OPTIONAL_OAS3_FIELDS
            for key in optional_oas3_fields:
                if self.config.get(key):
                    data[key] = self.config.get(key)

        # set defaults from template
        if self.template is not None:
            data.update(self.template)

        paths = data['paths']
        definitions = data['definitions']
        ignore_verbs = set(
            self.config.get('ignore_verbs', ('HEAD', 'OPTIONS'))
        )

        # technically only responses is non-optional
        optional_fields = self.config.get('optional_fields') or OPTIONAL_FIELDS

        for name, def_model in self.get_def_models(
                spec.get('definition_filter')).items():
            description, swag = parse_definition_docstring(
                def_model, self.sanitizer)
            if name and swag:
                if description:
                    swag.update({'description': description})
                definitions[name].update(swag)

        specs = self.get_specs(
            self.get_url_mappings(spec.get('rule_filter')), ignore_verbs,
            optional_fields, self.sanitizer,
            doc_dir=self.config.get('doc_dir'))

        http_methods = ['get', 'post', 'put', 'delete']
        for rule, verbs in specs:
            operations = dict()
            for verb, swag in verbs:
                update_dict = swag.get('definitions', {})
                if type(update_dict) == list and type(update_dict[0]) == dict:
                    # pop, assert single element
                    update_dict, = update_dict
                definitions.update(update_dict)
                defs = []  # swag.get('definitions', [])
                defs += extract_definitions(
                    defs, endpoint=rule.endpoint, verb=verb,
                    prefix_ids=prefix_ids
                )

                params = swag.get('parameters', [])
                if verb in swag.keys():
                    verb_swag = swag.get(verb)
                    if len(params) == 0 and verb.lower() in http_methods:
                        params = verb_swag.get('parameters', [])

                defs += extract_definitions(params,
                                            endpoint=rule.endpoint,
                                            verb=verb,
                                            prefix_ids=prefix_ids)

                request_body = swag.get('requestBody')
                if request_body:
                    content = request_body.get("content", {})
                    extract_definitions(
                        list(content.values()),
                        endpoint=rule.endpoint,
                        verb=verb,
                        prefix_ids=prefix_ids
                    )

                callbacks = swag.get('callbacks', {})
                if callbacks:
                    callbacks = {
                        str(key): value
                        for key, value in callbacks.items()
                    }
                    extract_definitions(
                        list(callbacks.values()),
                        endpoint=rule.endpoint,
                        verb=verb,
                        prefix_ids=prefix_ids
                    )

                responses = None
                if 'responses' in swag:
                    responses = swag.get('responses', {})
                    responses = {
                        str(key): value
                        for key, value in responses.items()
                    }
                    if responses is not None:
                        defs = defs + extract_definitions(
                            responses.values(),
                            endpoint=rule.endpoint,
                            verb=verb,
                            prefix_ids=prefix_ids
                        )
                    for definition in defs:
                        if 'id' not in definition:
                            definitions.update(definition)
                            continue
                        def_id = definition.pop('id')
                        if def_id is not None:
                            definitions[def_id].update(definition)

                operation = {}
                if swag.get('summary'):
                    operation['summary'] = swag.get('summary')
                if swag.get('description'):
                    operation['description'] = swag.get('description')
                if request_body:
                    operation['requestBody'] = request_body
                if callbacks:
                    operation['callbacks'] = callbacks
                if responses:
                    operation['responses'] = responses
                # parameters - swagger ui dislikes empty parameter lists
                if len(params) > 0:
                    operation['parameters'] = params
                # other optionals
                for key in optional_fields:
                    if key in swag:
                        value = swag.get(key)
                        if key in ('produces', 'consumes'):
                            if not isinstance(value, (list, tuple)):
                                value = [value]

                        operation[key] = value
                operations[verb] = operation

            if len(operations):
                try:
                    # Add reverse proxy prefix to route
                    prefix = self.template['swaggerUiPrefix']
                except (KeyError, TypeError):
                    prefix = ''
                srule = '{0}{1}'.format(prefix, rule)

                try:
                    # handle basePath
                    base_path = self.template['basePath']

                    if base_path:
                        if base_path.endswith('/'):
                            base_path = base_path[:-1]
                        if base_path:
                            # suppress base_path from srule if needed.
                            # Otherwise we will get definitions twice...
                            if srule.startswith(base_path):
                                srule = srule[len(base_path):]
                except (KeyError, TypeError):
                    pass

                # old regex '(<(.*?\:)?(.*?)>)'
                for arg in re.findall('(<([^<>]*:)?([^<>]*)>)', srule):
                    srule = srule.replace(arg[0], '{%s}' % arg[2])

                for key, val in operations.items():
                    if srule not in paths:
                        paths[srule] = {}
                    if key in paths[srule]:
                        paths[srule][key].update(val)
                    else:
                        paths[srule][key] = val
        self.apispecs[endpoint] = data
        return data

    def get_specs(self, rules, ignore_verbs, optional_fields, sanitizer, doc_dir=None):
        """
        gets api specs for given url rules.

        :param list[pyrin.api.router.handlers.base.RouteBase] rules: list of url rules.
        :param list[str] ignore_verbs: list of ignored http method names.
        :param list[str] optional_fields: list of optional fields in docstrings.
        :param function sanitizer: a callable to be used as string sanitizer.
        :param str doc_dir: directory path of docs.

        :rtype: list[tuple]
        """

        specs = []
        for rule in rules:
            if self._is_flasgger_rule(rule):
                continue

            endpoint = current_app.view_functions[rule.endpoint]
            methods = dict()
            is_mv = is_valid_method_view(endpoint)

            for verb in rule.methods.difference(ignore_verbs):
                if not is_mv and has_valid_dispatch_view_docs(endpoint):
                    endpoint.methods = endpoint.methods or ['GET']
                    if verb in endpoint.methods:
                        methods[verb.lower()] = endpoint
                elif getattr(endpoint, 'methods', None) is not None:
                    if verb in endpoint.methods:
                        verb = verb.lower()
                        if hasattr(endpoint.view_class, verb):
                            methods[verb] = getattr(endpoint.view_class, verb)
                else:
                    methods[verb.lower()] = endpoint

            verbs = []
            for verb, method in methods.items():

                klass = method.__dict__.get('view_class', None)
                if not is_mv and klass and hasattr(klass, 'verb'):
                    method = getattr(klass, 'verb', None)
                elif klass and hasattr(klass, 'dispatch_request'):
                    method = getattr(klass, 'dispatch_request', None)
                if method is None:  # for MethodView
                    method = getattr(klass, verb, None)

                if method is None:
                    if is_mv:  # #76 Empty MethodViews
                        continue
                    raise RuntimeError(
                        'Cannot detect view_func for rule {0}'.format(rule)
                    )

                swag = {}

                if getattr(method, 'specs_dict', None):
                    definition = {}
                    merge_specs(
                        swag,
                        convert_schemas(deepcopy(method.specs_dict), definition)
                    )
                    swag['definitions'] = definition

                view_class = getattr(endpoint, 'view_class', None)
                if view_class and issubclass(view_class, SwaggerView):
                    apispec_swag = {}
                    apispec_attrs = optional_fields + [
                        'parameters', 'definitions', 'responses',
                        'summary', 'description'
                    ]
                    for attr in apispec_attrs:
                        value = getattr(view_class, attr)
                        if value:
                            apispec_swag[attr] = value

                    apispec_definitions = apispec_swag.get('definitions', {})
                    swag.update(
                        convert_schemas(apispec_swag, apispec_definitions)
                    )
                    swag['definitions'] = apispec_definitions

                if doc_dir:
                    if view_class:
                        file_path = os.path.join(
                            doc_dir, endpoint.__name__, method.__name__ + '.yml')
                    else:
                        file_path = os.path.join(
                            doc_dir, endpoint.__name__ + '.yml')
                    if os.path.isfile(file_path):
                        func = method.__func__ \
                            if hasattr(method, '__func__') else method
                        setattr(func, 'swag_type', 'yml')
                        setattr(func, 'swag_path', file_path)

                doc_summary, doc_description, doc_swag = parse_docstring(
                    method, sanitizer, endpoint=rule.endpoint, verb=verb)

                if doc_swag is None:
                    doc_swag = {}

                merge_specs(swag, doc_swag)

                if doc_summary:
                    swag['summary'] = doc_summary

                if doc_description:
                    swag['description'] = doc_description

                self._fix_metadata(rule, verb, swag)
                verbs.append((verb, swag))

            if verbs:
                specs.append((rule, verbs))

        return specs
