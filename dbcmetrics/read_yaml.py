import yaml

with open('config.yaml', 'r') as file:
    prime_service = yaml.safe_load(file)

print(prime_service['prime_numbers'][0])
print(prime_service['rest']['url'])