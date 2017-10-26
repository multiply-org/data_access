import sys
from cate.util.cli import run_main, SubCommandCommand

__author__ = 'Tonio Fincke (Brockmann Consult GmbH)'

#: Name of command line executable
CLI_NAME = 'multiply'
CLI_DESCRIPTION = 'The MULTIPLY Data Access command line interface'

__version__ = '0.1'

HELP_TEXT = 'Get a list of urls to locally available data sets that are within the given region of interest (roi), ' \
            'occur later than the start time and earlier than the stop time, and are of one of the requested data ' \
            'types. Parameters may either be passed as part of a config file in YAML format or explicitly passed ' \
            'as individual parameters. If a parameter is contained in the config file and passed as dedicated ' \
            'parameter, the value from the latter will be used.'
CONFIG_HELP_TEXT = 'A config file in YAML format. This file holds information on the other parameters.'
ROI_HELP_TEXT = 'The spatial extent of the region of interest, given as wkt string. EO products that intersect this ' \
                'zone will be included. If not given, it is assumed that the whole globe is the region of interest.'
START_TIME_HELP_TEXT = 'The earliest time for which EO data is requested. Given in ISO format. Must not be later ' \
                       'than end_time. Optional'
END_TIME_HELP_TEXT = 'The latest time for which EO data is requested. Given in ISO format, must not be earlier than ' \
                     'start_time. Optional.'
DATA_TYPES_HELP_TEXT = 'List of string values. The types of EO data shall actually be retrieved. If not given, ' \
                       'no data will be retrieved.'
WORKING_DIR_HELP_TEXT = 'Directory to which the list with the urls shall be downloaded. If not given, the list will ' \
                        'be downloaded to the default working directory.'
DOWNLOAD_DIR_HELP_TEXT = 'Directory to which data shall be downloaded. If not given, no data will be downloaded and ' \
                         'only locally available data will be considered.'

class GetDataUrlsCommand(SubCommandCommand):

    @classmethod
    def name(cls):
        return 'get_data_urls'

    @classmethod
    def parser_kwargs(cls):

        return dict(help=HELP_TEXT,
                    description=HELP_TEXT)

    @classmethod
    def configure_parser_and_subparsers(cls, parser, subparsers):
        parser.add_argument('--config', '-c', help=CONFIG_HELP_TEXT)
        parser.add_argument('--roi', '-r', help=ROI_HELP_TEXT)
        parser.add_argument('--start_time', '-st', help=START_TIME_HELP_TEXT)
        parser.add_argument('--end_time', '-et', help=END_TIME_HELP_TEXT)
        parser.add_argument('--data_types', '-dt', help=DATA_TYPES_HELP_TEXT)
        parser.add_argument('--working_dir', '-wd', help=WORKING_DIR_HELP_TEXT)
        parser.add_argument('--download_dir', '-dd', help=DOWNLOAD_DIR_HELP_TEXT)
        # parser.set_defaults(sub_command_function=cls._execute_list)


# list of commands supported by the CLI. Entries are classes derived from :py:class:'Command' class-
COMMAND_REGISTRY = [GetDataUrlsCommand]

def main(args=None) -> int:
    # noinspection PyTypeChecker
    return run_main(CLI_NAME,
                    CLI_DESCRIPTION,
                    __version__,
                    COMMAND_REGISTRY,
                    license_text='license text',
                    docs_url='url to docs',
                    error_message_trimmer=None,
                    args=args)

if __name__ == '__main__':
    sys.exit(main())
