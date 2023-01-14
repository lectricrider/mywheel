#!/usr/bin/env python3

import io
import json
import getpass
import requests
import sys
import argparse

RIDES_FROM_USER_URL = 'https://app-api.onewheel.com/api/v1/android/rides/fromUser?&userID='
RIDES_OWN_URL = 'https://app-api.onewheel.com/api/v1/android/rides/own'
USERS_OWN_URL = 'https://app-api.onewheel.com/api/v1/android/users/own'
RIDE_OORDINATES_URL = 'https://app-api.onewheel.com/api/v1/android/ridesCoordinates'

def do_request(url, username, password, out_file=sys.stdout):
    """Do a request."""
    if type(out_file) == str:
        out_file = open(out_file, 'w')
    session = requests.Session()
    if username and not password:
        password = getpass.getpass()
    if username and password:
        response = session.get(url, auth=(username, password))
    else:
        response = session.get(url)
    if response.status_code != 200:
        print(response.text, file=sys.stderr)
        raise ValueError('Failed to get user details.')
    if out_file:
        out_file.write(json.dumps(response.json(), indent=4))
    return response.json()

def ride_manifest(username=None, password=None, out_file=sys.stdout):
    """Get private rides."""
    return do_request(RIDES_OWN_URL, username=username, password=password, out_file=out_file)

def ride_coordinates(ride_id, username=None, password=None, out_file=sys.stdout):
    """Get coordinates for a ride."""
    return do_request(f'{RIDE_OORDINATES_URL}/{ride_id}', username=username, password=password, out_file=out_file)

def all_rides(username, password, out_file=sys.stdout):
    """Get all of your rides."""
    print(f'Getting all rides for {username}...')
    rides = io.StringIO()
    rides = ride_manifest(username=username, password=password, out_file=None)
    all_rides = []
    print(f'Found {len(rides["data"]["entries"])} rides.')
    for ride in rides['data']['entries']:
        print(f'Getting coordinates for ride {ride["id"]}.')
        coordinates = io.StringIO()
        coordinates = ride_coordinates(ride_id=ride['id'], username=username, password=password, out_file=None)
        all_rides.append({
            'info': ride,
            'coordinates': coordinates
        })
    if out_file:
        print(f'Writing {len(all_rides)} rides to {out_file}.')
        with open(out_file, 'w') as f:
            f.write(json.dumps(all_rides, indent=4))
    print('Done.')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-u', '--username', help='Username or email.')
    argparser.add_argument('-p', '--password', help='Password.')
    argparser.add_argument('-o', '--out', help='Output file.', default='my_rides.json')
    args = argparser.parse_args()
    if not args.username:
        args.username = input('Username/Email: ')
    if not args.password:
        args.password = getpass.getpass()
    all_rides(username=args.username, password=args.password, out_file=args.out)
    
