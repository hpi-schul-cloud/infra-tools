import yaml,os
a_file = 'dbcm_config.yaml'
if not os.path.isabs(a_file):
        script_path = os.path.dirname(os.path.realpath(__file__))
        a_file_abs = os.path.join(script_path, a_file)
with open(a_file_abs, 'r') as file:
    prime_service = yaml.safe_load(file)

x = prime_service['instances']
y = prime_service['version_metrics']['services']
print (x)
print (y)