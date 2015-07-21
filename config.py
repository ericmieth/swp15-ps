import argparse
import configparser
import os  # needed to open file

config = configparser.ConfigParser()
config_file = "config.ini"  # default name and path to config-file

# begin: default values
conf_cont = dict()
conf_cont["webserver"] = {
	"host": "localhost",
	"port": "5000",
	"secret_key": os.urandom(24)
}
conf_cont["ODFMI"] = {"url": "http://od.fmi.uni-leipzig.de:8892/sparql"}
conf_cont["user_db"] = {"path": "./db/ps.sqlite"}
# end: default values

# begin: argument-parsing
parser = argparse.ArgumentParser(
			description="start webserver with given arguments")
parser.add_argument(
	"--host",
	metavar="address",
	default="",
	help="hostname to listen on"
)
parser.add_argument(
	"-p", "--port",
	type=int,
	help="port to listen on"
)
parser.add_argument(
	"-db", "--database",
	help="path to SQLite-database"
)
parser.add_argument(
	"--debug",
	action="store_true",
	help="enables debugging-mode (Werkzeug)"
)
parser.add_argument(
	"-c", "--config",
	default="config.ini",
	help="choose here to validate or create the config"
)
parser.add_argument(
	"-C", "--create",
	action="store_true",
	help="create a config file containing the default values"
)
args = parser.parse_args()
# end: argument-parsing

config_file = args.config

# create config
if args.create:
	config.read_dict(conf_cont)
	with open(config_file, 'w') as file:
		config.write(file)

# read config
with open(config_file) as config_f:
	config.read_file(config_f)
for key in config:
	for subkey in config[key]:
		conf_cont[key][subkey] = config[key][subkey]

# set values
conf_cont["webserver"]["port"] = int(conf_cont["webserver"]["port"])

if args.host:
	conf_cont["webserver"]["host"] = args.host
if args.port:
	conf_cont["webserver"]["port"] = args.port
if args.database:
	conf_cont["user_db"]["path"] = args.database
conf_cont["debug"] = args.debug
c = conf_cont
