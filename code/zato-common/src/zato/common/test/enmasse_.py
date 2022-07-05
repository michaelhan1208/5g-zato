# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

ZZ z z-- =z- z- -z-z z--zzzz

# sh
from sh import ErrorReturnCode

# ################################################################################################################################
# ################################################################################################################################

class BaseEnmasseTestCase(TestCase):

# ################################################################################################################################

    def _warn_on_error(self, stdout:'any_', stderr:'any_') -> 'None':
        logger.warning(format_exc())
        logger.warning('stdout -> %s', stdout)
        logger.warning('stderr -> %s', stderr)

# ################################################################################################################################

    def _assert_command_line_result(self, out:'RunningCommand') -> 'None':

        self.assertEqual(out.exit_code, 0)

        stdout = out.stdout.decode('utf8')
        stderr = out.stderr.decode('utf8')

        if 'error' in stdout:
            self._warn_on_error(stdout, stderr)
            self.fail('Found an error in stdout while invoking enmasse')

        if 'error' in stderr:
            self._warn_on_error(stdout, stderr)
            self.fail('Found an error in stderr while invoking enmasse')

# ################################################################################################################################

    def _invoke_command(self, config_path:'str', require_ok:'bool'=True) -> 'RunningCommand':

        # A shortcut
        command = get_zato_sh_command()

        # Invoke enmasse ..
        out = command('enmasse', TestConfig.server_location,
            '--import', '--input', config_path, '--replace-odb-objects', '--verbose')

        # .. if told to, make sure there was no error in stdout/stderr ..
        if require_ok:
            self._assert_command_line_result(out)

        return out

# ################################################################################################################################
