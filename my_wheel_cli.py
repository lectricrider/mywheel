    #!/usr/bin/env python3

    """
        This script is provided as-is, with no warranty or support.
        It is provided as a starting point for anyone who wants to
        download their own ride data.
        This script is not affiliated with Future Motion, Inc.
        in any way, and is not supported by them.
        This script is provided under the MIT license.
        The MIT License (MIT)
    """

    import getpass
    import requests
    import json
    import fire
    import io
    import sys

    devnull = open('/dev/null', 'w')

    RIDES_FROM_USER_URL = 'https://app-api.onewheel.com/api/v1/android/rides/fromUser?&userID='
    RIDES_OWN_URL = 'https://app-api.onewheel.com/api/v1/android/rides/own'
    USERS_OWN_URL = 'https://app-api.onewheel.com/api/v1/android/users/own'
    RIDE_OORDINATES_URL = 'https://app-api.onewheel.com/api/v1/android/ridesCoordinates'

    # Useful for debugging
    def to_curl(request):
        """Convert a request to a curl command."""
        if request.body:
            return f'curl -X {request.method} -H "{request.headers}" -d "{request.body}" "{request.url}"'
        else:
            return f'curl -X {request.method} -H "{request.headers}" "{request.url}"'
    
    def do_request(url, username, password, out_file):
        """Do a request."""
        if type(out_file) == str:
            out_file = open(out_file, 'w')
        if not out_file:
            out_file = sys.stdout
        session = requests.Session()
        if username and not password:
            password = getpass.getpass()
        if username and password:
            response = session.get(url, auth=(username, password))
        else:
            response = session.get(url)
        print(to_curl(response.request), file=sys.stderr)
        if response.status_code != 200:
            print(response.text, file=sys.stderr)
            raise ValueError('Failed to get user details.')
        out_file.write(json.dumps(response.json(), indent=4))
        return response.json()

    class Cli():

        def public_rides(self, user_id, out_file=None):
            """Get public riders."""
            do_request(RIDES_FROM_USER_URL + str(user_id), out_file=out_file)

        def own_user(self, username=None, password=None, out_file=None):
            """Get private user info."""
            do_request(USERS_OWN_URL, username=username, password=password, out_file=out_file)

        def ride_coordinates(self, ride_id, username=None, password=None, out_file=None):
            """Get ride coordinates."""
            do_request(RIDES_FROM_USER_URL + str(ride_id), username=username, password=password, out_file=out_file)

        def own_rides(self, username=None, password=None, out_file=None):
            """Get private rides."""
            do_request(RIDES_OWN_URL, username=username, password=password, out_file=out_file)
    
        def ride_coordinates(self, ride_id, username=None, password=None, out_file=None):
            """Get ride coordinates."""
            do_request(f'{RIDE_OORDINATES_URL}/{str(ride_id)}', username=username, password=password, out_file=out_file)

        def all_rides(self, username=None, password=None, out_file=None):
            """Get all of your rides."""
            all_rides = []
            if not password:
                password = getpass.getpass()
            rides = io.StringIO()
            self.own_rides(username=username, password=password, out_file=rides)
            rides = json.loads(rides.getvalue())
            for ride in rides['data']['entries']:
                coordinates = io.StringIO()
                self.ride_coordinates(ride_id=ride['id'], username=username, password=password, out_file=coordinates)
                coordinates = json.loads(coordinates.getvalue())
                all_rides.append({
                    'info': ride,
                    'coordinates': coordinates
                })
            if out_file:
                with open(out_file, 'w') as f:
                    f.write(json.dumps(all_rides, indent=4))
            else:
                print(json.dumps(all_rides, indent=4))

    if __name__ == '__main__':
        fire.Fire(Cli)
