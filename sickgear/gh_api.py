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

from . import helpers

# noinspection PyUnreachableCode
if False:
    from typing import Dict, Optional


class GitHub(object):
    """
    Simple api wrapper for the Github API v3. Currently only supports the small thing that SB
    needs it for - list of commits.
    """

    def __init__(self, github_repo_user, github_repo, branch):

        self.github_repo_user = github_repo_user
        self.github_repo = github_repo
        self.branch = branch

    @staticmethod
    def _access_API(path, params=None):
        """
        Access the API at the path given and with the optional params given.

        path: A list of the path elements to use (eg. ['repos', 'midgetspy', 'Sick-Beard', 'commits'])
        params: Optional dict of name/value pairs for extra params to send. (eg. {'per_page': 10})

        Returns a deserialized json object of the result. Doesn't do any error checking (hope it works).
        """

        url = 'https://api.github.com/' + '/'.join(path)

        if params and type(params) is dict:
            url += '?' + '&'.join([str(x) + '=' + str(params[x]) for x in params])

        parsedJSON = helpers.get_url(url, parse_json=True)
        if not parsedJSON:
            return []

        return parsedJSON

    def commits(self):
        """
        Get a list of the 100 most recent commits from the specified user/repo/branch, starting from HEAD.

        user: The github username of the person whose repo you're querying
        repo: The repo name to query
        branch: Optional, the branch name to show commits from

        Returns a deserialized json object containing the commit info. See http://developer.github.com/v3/repos/commits/
        """
        access_API = self._access_API(['repos', self.github_repo_user, self.github_repo, 'commits'],
                                      params={'per_page': 100, 'sha': self.branch})
        return access_API

    def compare(self, base, head, per_page=1):
        """
        Uses the API to get a list of compares between base and head.

        user: The github username of the person whose repo you're querying
        repo: The repo name to query
        base: Start compare from branch
        head: Current commit sha or branch name to compare
        per_page: number of items per page

        Returns a deserialized json object containing the compare info. See http://developer.github.com/v3/repos/commits
        """
        access_API = self._access_API(
            ['repos', self.github_repo_user, self.github_repo, 'compare', base + '...' + head],
            params={'per_page': per_page})
        return access_API

    def branches(self):
        access_API = self._access_API(
            ['repos', self.github_repo_user, self.github_repo, 'branches'],
            params={'per_page': 100})
        return access_API

    def pull_requests(self):
        access_API = self._access_API(
            ['repos', self.github_repo_user, self.github_repo, 'pulls'],
            params={'per_page': 100})  # type: Optional[Dict]
        pulls = []
        for x in access_API:
            try:
                pull = PullRequest(x['head']['ref'], x['number'])
                pulls.append((repr(pull), pull.fetch_name()))
            except (BaseException, Exception):
                continue
        return pulls


class PullRequest(object):
    def __init__(self, ref, number):
        self.ref = ref
        self.number = number

    def __repr__(self):
        return '%s: %s' % (self.number, self.ref)

    def fetch_name(self):
        return 'pull/%s/head:pull/%s/%s' % (self.number, self.number, self.ref)
