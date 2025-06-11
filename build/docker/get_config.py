import json
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Get config values for a service')
    parser.add_argument('config_file', help='Path to images configuration file')
    parser.add_argument('service', help='Service name')
    parser.add_argument('field', help='Field to retrieve (e.g., LIBS)')
    args = parser.parse_args()

    try:
        cfg = json.load(open(args.config_file))
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    val = cfg.get(args.service, {}).get(args.field)
    if isinstance(val, list):
        print(' '.join(val))
    elif isinstance(val, dict):
        for k, v in val.items():
            print(f"{k}={v}")
    elif val is not None:
        print(val)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
