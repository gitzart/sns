import re

import cerberus

from project.utils import to_camel_case


class ErrorHandler(cerberus.errors.BasicErrorHandler):
    def __call__(self, errors=None):
        if errors is not None:
            self.clear()
            self.extend(errors)
        return self.json_ready_pretty_tree

    @property
    def json_ready_pretty_tree(self):
        pretty = {}
        for k, v in self.tree.items():
            pretty[to_camel_case(k)] = v[0]
        return pretty


class Validator(cerberus.Validator):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_handler', ErrorHandler)
        super().__init__(*args, **kwargs)

    def _validate_allspace(self, allspace, field, value):
        """When False, doesn't allow all space value (' ') or empty value ('').

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        skip_rules = False

        if not allspace and isinstance(value, str):
            if value.isspace():
                skip_rules = True
                self._error(field, 'all space value not allowed')
            elif len(value) == 0:
                skip_rules = True
                self._error(field, 'empty values not allowed')

        if skip_rules:
            self._drop_remaining_rules(
                'allowed', 'forbidden', 'items', 'maxlength', 'minlength',
                'regex', 'validator'
            )

    def _validator_email(self, field, value):
        pattern = re.compile(
            '^[\w.!#$%&’*+/=?^_`{|}~-]+@((?!_)[\w-])+(?:\.((?!_)[\w-])+)*$'
        )
        if not pattern.match(value):
            self._error(
                field, f"value does not match regex '{pattern.pattern}'")
        else:
            components = value.split('@')[-1].split('.')
            for c in components:
                if c.startswith('-') or c.endswith('-'):
                    self._error(field, 'contains misplaced character (-)')
                    break

    def _validator_username(self, field, value):
        pattern = re.compile('^[A-Za-z0-9.]{5,}$')
        if not pattern.match(value):
            self._error(
                field, f"value does not match regex '{pattern.pattern}'")
        elif value.startswith('.') or value.endswith('.'):
            self._error(field, 'contains misplaced character (.)')
