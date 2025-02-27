# Author: Nico Berlee http://nico.berlee.nl/
#
# This file is part of SickGear.
#
# SickGear is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SickGear is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SickGear.  If not, see <http://www.gnu.org/licenses/>.

import re
import telnetlib

from .generic import BaseNotifier
import sickgear
from exceptions_helper import ex

from _23 import etree, urlencode
# noinspection PyUnresolvedReferences
from six.moves import urllib


class NMJNotifier(BaseNotifier):

    def notify_settings(self, host):
        """
        Retrieves the settings from a NMJ/Popcorn hour

        host: The hostname/IP of the Popcorn Hour server

        Returns: True if the settings were retrieved successfully, False otherwise
        """

        # establish a terminal session to the PC
        result, terminal = False, None
        try:
            terminal = telnetlib.Telnet(host)
        except (BaseException, Exception):
            self._log_warning(u'Unable to get a telnet session to %s' % host)

        if result:
            # tell the terminal to output the necessary info to the screen so we can search it later
            self._log_debug(u'Connected to %s via telnet' % host)
            terminal.read_until('sh-3.00# ')
            terminal.write('cat /tmp/source\n')
            terminal.write('cat /tmp/netshare\n')
            terminal.write('exit\n')
            tnoutput = terminal.read_all()

            match = re.search(r'(.+\.db)\r\n?(.+)(?=sh-3.00# cat /tmp/netshare)', tnoutput)
            # if we found the database in the terminal output then save that database to the config
            if not match:
                self._log_warning(u'Could not get current NMJ database on %s, NMJ is probably not running!' % host)
            else:
                database = match.group(1)
                device = match.group(2)
                self._log_debug(u'Found NMJ database %s on device %s' % (database, device))
                sickgear.NMJ_DATABASE = database
                # if the device is a remote host then try to parse the mounting URL and save it to the config
                if device.startswith('NETWORK_SHARE/'):
                    match = re.search('.*(?=\r\n?%s)' % (re.escape(device[14:])), tnoutput)

                    if not match:
                        self._log_warning('Detected a network share on the Popcorn Hour, '
                                          'but could not get the mounting url')
                    else:
                        mount = match.group().replace('127.0.0.1', host)
                        self._log_debug(u'Found mounting url on the Popcorn Hour in configuration: %s' % mount)
                        sickgear.NMJ_MOUNT = mount
                        result = True

        if result:
            return '{"message": "Got settings from %(host)s", "database": "%(database)s", "mount": "%(mount)s"}' % {
                "host": host, "database": sickgear.NMJ_DATABASE, "mount": sickgear.NMJ_MOUNT}
        return '{"message": "Failed! Make sure your Popcorn is on and NMJ is running. ' \
               '(see Error Log -> Debug for detailed info)", "database": "", "mount": ""}'

    def _send(self, host=None, database=None, mount=None):
        """
        Sends a NMJ update command to the specified machine

        host: The hostname/IP to send the request to (no port)
        database: The database to send the request to
        mount: The mount URL to use (optional)

        Returns: True if the request succeeded, False otherwise
        """
        host = self._choose(host, sickgear.NMJ_HOST)
        database = self._choose(database, sickgear.NMJ_DATABASE)
        mount = self._choose(mount, sickgear.NMJ_MOUNT)

        self._log_debug(u'Sending scan command for NMJ ')

        # if a mount URL is provided then attempt to open a handle to that URL
        if mount:
            try:
                req = urllib.request.Request(mount)
                self._log_debug(u'Try to mount network drive via url: %s' % mount)
                http_response_obj = urllib.request.urlopen(req)  # PY2 http_response_obj has no `with` context manager
                http_response_obj.close()
            except IOError as e:
                if hasattr(e, 'reason'):
                    self._log_warning(u'Could not contact Popcorn Hour on host %s: %s' % (host, e.reason))
                elif hasattr(e, 'code'):
                    self._log_warning(u'Problem with Popcorn Hour on host %s: %s' % (host, e.code))
                return False
            except (BaseException, Exception) as e:
                self._log_error(u'Unknown exception: ' + ex(e))
                return False

        # build up the request URL and parameters
        params = dict(arg0='scanner_start', arg1=database, arg2='background', arg3='')
        params = urlencode(params)
        update_url = 'http://%(host)s:8008/metadata_database?%(params)s' % {'host': host, 'params': params}

        # send the request to the server
        try:
            req = urllib.request.Request(update_url)
            self._log_debug(u'Sending scan update command via url: %s' % update_url)
            http_response_obj = urllib.request.urlopen(req)
            response = http_response_obj.read()
            http_response_obj.close()
        except IOError as e:
            if hasattr(e, 'reason'):
                self._log_warning(u'Could not contact Popcorn Hour on host %s: %s' % (host, e.reason))
            elif hasattr(e, 'code'):
                self._log_warning(u'Problem with Popcorn Hour on host %s: %s' % (host, e.code))
            return False
        except (BaseException, Exception) as e:
            self._log_error(u'Unknown exception: ' + ex(e))
            return False

        # try to parse the resulting XML
        try:
            et = etree.fromstring(response)
            result = et.findtext('returnValue')
        except SyntaxError as e:
            self._log_error(u'Unable to parse XML returned from the Popcorn Hour: %s' % ex(e))
            return False

        # if the result was a number then consider that an error
        if 0 < int(result):
            self._log_error(u'Popcorn Hour returned an errorcode: %s' % result)
            return False

        self._log(u'NMJ started background scan')
        return True

    def _notify(self, host=None, database=None, mount=None, **kwargs):

        result = self._send(host, database, mount)

        return self._choose((('Success, started %s', 'Failed to start %s')[not result] % 'the scan update'), result)

    def test_notify(self, host, database, mount):
        self._testing = True
        return self._notify(host, database, mount)

    # notify_snatch() Not implemented: Start the scanner when snatched does not make sense
    # notify_git_update() Not implemented, no reason to start scanner

    def notify_download(self, *args, **kwargs):
        self._notify()

    def notify_subtitle_download(self, *args, **kwargs):
        self._notify()


notifier = NMJNotifier
