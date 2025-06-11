import json
import subprocess
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        default='build/docker/images_configuration.json',
                        help='Config file path')
    parser.add_argument('--test', action='store_true', help='Build test images')
    args = parser.parse_args()

    try:
        cfg = json.load(open(args.config))
    except Exception as e:
        print(f"Failed to load config: {e}", file=sys.stderr)
        sys.exit(1)

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[2]

    svc_keys = [k for k in cfg if (k.startswith('test_') if args.test else not k.startswith('test_'))]

    for svc in svc_keys:
        conf = cfg[svc]
        dockerfile_rel = conf['dockerfile']
        dockerfile_path = repo_root / dockerfile_rel
        image = f"misis-{svc}"
        print(f"Building {image} from {dockerfile_path}...")
        subprocess.check_call([
            'docker', 'build',
            '-f', str(dockerfile_path),
            '-t', image,
            str(repo_root)
        ])

    if not args.test:
        print("Deploying production services...")
        compose_file = repo_root / 'build' / 'docker' / 'docker_compose.yml'
        subprocess.check_call(['docker-compose', '-f', str(compose_file), 'up', '-d'])


if __name__ == '__main__':
    main()
