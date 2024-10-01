import fire
import yaml
import re


def read_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file)


def promote_version(file_path, from_version, to_version, promote, service_name_prefix):
    data = read_yaml(file_path)

    for upstream in data['upstreams']:
        if upstream['name'] == f'{service_name_prefix}-canary':
            total_weight = sum(target['weight'] for target in upstream['targets'])
            for target in upstream['targets']:
                if target['target'] == f'{service_name_prefix}-{from_version}':
                    target['weight'] = max(0, target['weight'] - promote)
                elif target['target'] == f'{service_name_prefix}-{to_version}':
                    target['weight'] = min(100, target['weight'] + promote)
            # Normalize weights to ensure they sum up to 100
            total_weight = sum(target['weight'] for target in upstream['targets'])
            for target in upstream['targets']:
                target['weight'] = int((target['weight'] / total_weight) * 100)

    write_yaml(file_path, data)
    print(f"Promoted {to_version} by {promote}% from {from_version}")


def revert_version(file_path):
    print("Revert functionality is not available without state management.")


def set_canary_version(file_path, from_version, to_version, reset_percent, service_name_prefix):
    data = read_yaml(file_path)

    for upstream in data['upstreams']:
        if upstream['name'] == f'{service_name_prefix}-canary':
            for target in upstream['targets']:
                if target['target'] == f'{service_name_prefix}-{from_version}':
                    target['weight'] = max(0, 100 - reset_percent)
                elif target['target'] == f'{service_name_prefix}-{to_version}':
                    target['weight'] = min(100, reset_percent)
                else:
                    target['weight'] = 0

    write_yaml(file_path, data)
    print(f"Set {to_version} as the canary version with {reset_percent}% weight, reducing {from_version} to {100 - reset_percent}%.")


def is_valid_version(version):
    return re.match(r'^v\d+$', version) is not None


class CanaryDeploymentCLI:
    def promote(self, file_path, from_version, to_version, promote, service_name_prefix):
        """Promote weight from one version to another by a specified percentage."""
        if not is_valid_version(from_version) or not is_valid_version(to_version):
            print("Invalid version specified. Use versions in the format 'v<number>'.")
            return
        if promote < 0 or promote > 100:
            print("Invalid promote value. It should be between 0 and 100.")
            return
        promote_version(file_path, from_version, to_version, promote, service_name_prefix)

    def revert(self, file_path):
        """Revert functionality is not available without state management."""
        revert_version(file_path)

    def set_canary(self, file_path, from_version, to_version, reset_percent, service_name_prefix):
        """Set a specific version as the canary with a specified percentage weight, resetting others."""
        if not is_valid_version(from_version) or not is_valid_version(to_version):
            print("Invalid version specified. Use versions in the format 'v<number>'.")
            return
        if reset_percent < 0 or reset_percent > 100:
            print("Invalid reset percentage. It should be between 0 and 100.")
            return
        set_canary_version(file_path, from_version, to_version, reset_percent, service_name_prefix)


if __name__ == '__main__':
    fire.Fire(CanaryDeploymentCLI)