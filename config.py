import os
import os.path
import subprocess
import sys
import logging
import logging.handlers

import yaml


logger = logging.getLogger(__name__)

with open('versioning.yml', encoding='utf-8') as version_file:
    versioning_info = yaml.safe_load(version_file)

__version__ = versioning_info['Lichess_Bot_version']

terminated = False
restart = True

def load_config(config_path: str) -> dict:
    with open(config_path, encoding='utf-8') as yml_input:
        try:
            config = yaml.safe_load(yml_input)
        except Exception as e:
            print(f'There appears to be a syntax problem with your {config_path}', file=sys.stderr)
            raise e

    if 'LICHESS_BOT_TOKEN' in os.environ:
        config['token'] = os.environ['LICHESS_BOT_TOKEN']
    _check_sections(config)
    _check_engine_sections(config['engine'])
    _check_syzygy_sections(config['engine']['syzygy'])
    _check_gaviota_sections(config['engine']['gaviota'])
    _check_variants_sections(config['engine']['variants'])
    _check_online_moves_sections(config['engine']['online_moves'])
    _check_matchmaking_types_sections(config['matchmaking']['types'])
    _check_egtb(config['engine'])
    _init_lists(config)
    _init_engines(config['engine'])
    _init_opening_books(config)
    config['version'] = _get_version()

    return config


def _check_sections(config: dict) -> None:
    # [section, type, error message]
    sections = [
        ['token', str, 'Section `token` must be a string wrapped in quotes.'],
        ['engine', dict, 'Section `engine` must be a dictionary with indented keys followed by colons.'],
        ['challenge', dict, 'Section `challenge` must be a dictionary with indented keys followed by colons.'],
        ['matchmaking', dict, 'Section `matchmaking` must be a dictionary with indented keys followed by colons.'],
        ['messages', dict, 'Section `messages` must be a dictionary with indented keys followed by colons.'],
        ['books', dict, 'Section `books` must be a dictionary with indented keys followed by colons.']]
    for section in sections:
        if section[0] not in config:
            raise RuntimeError(f'Your config does not have required section `{section[0]}`.')

        if not isinstance(config[section[0]], section[1]):
            raise TypeError(section[2])

def _check_engine_sections(engine_section: dict) -> None:
    engine_sections = [
        ['dir', str, '"dir" must be a string wrapped in quotes.'],
        ['name', str, '"name" must be a string wrapped in quotes.'],
        ['ponder', bool, '"ponder" must be a bool.'],
        ['syzygy', dict, '"syzygy" must be a dictionary with indented keys followed by colons.'],
        ['gaviota', dict, '"gaviota" must be a dictionary with indented keys followed by colons.'],
        ['uci_options', dict, '"uci_options" must be a dictionary with indented keys followed by colons.'],
        ['variants', dict, '"variants" must be a dictionary with indented keys followed by colons.'],
        ['opening_books', dict, '"opening_books" must be a dictionary with indented keys followed by colons.'],
        ['online_moves', dict, '"online_moves" must be a dictionary with indented keys followed by colons.'],
        ['offer_draw', dict, '"offer_draw" must be a dictionary with indented keys followed by colons.'],
        ['resign', dict, '"resign" must be a dictionary with indented keys followed by colons.']]
    for subsection in engine_sections:
        if subsection[0] not in engine_section:
            raise RuntimeError(f'Your config does not have required `engine` subsection `{subsection[0]}`.')

        if not isinstance(engine_section[subsection[0]], subsection[1]):
            raise TypeError(f' `engine`subsection {subsection[2]}')


def _check_syzygy_sections(syzygy_section: dict) -> None:
    syzygy_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['paths', list, '"paths" must be a list.'],
        ['max_pieces', int, '"max_pieces" must be an integer.'],
        ['instant_play', bool, '"instant_play" must be a bool.']]
    for subsection in syzygy_sections:
        if subsection[0] not in syzygy_section:
            raise RuntimeError(f'Your config does not have required `engine` `syzygy` subsection `{subsection[0]}`.')

        if not isinstance(syzygy_section[subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `syzygy` subsection {subsection[2]}')


def _check_gaviota_sections(gaviota_section: dict) -> None:
    gaviota_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['paths', list, '"paths" must be a list.'],
        ['max_pieces', int, '"max_pieces" must be an integer.']]
    for subsection in gaviota_sections:
        if subsection[0] not in gaviota_section:
            raise RuntimeError(f'Your config does not have required `engine` `gaviota` subsection `{subsection[0]}`.')

        if not isinstance(gaviota_section[subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `gaviota` subsection {subsection[2]}')

def _check_variants_sections(variants_section: dict) -> None:
    variants_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['dir', str, '"dir" must be a string wrapped in quotes.'],
        ['name', str, '"name" must be a string wrapped in quotes.'],
        ['ponder', bool, '"ponder" must be a bool.'],
        ['uci_options', dict, '"uci_options" must be a dictionary with indented keys followed by colons.']]
    for subsection in variants_sections:
        if subsection[0] not in variants_section:
            raise RuntimeError(f'Your config does not have required `engine` `variants` subsection `{subsection[0]}`.')

        if not isinstance(variants_section[subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `variants` subsection {subsection[2]}')


def _check_online_moves_sections(online_moves_section: dict) -> None:
    online_moves_sections = [
        ['opening_explorer', dict, '"opening_explorer" must be a dictionary with indented keys followed by colons.'],
        ['chessdb', dict, '"chessdb" must be a dictionary with indented keys followed by colons.'],
        ['lichess_cloud', dict, '"lichess_cloud" must be a dictionary with indented keys followed by colons.'],
        ['online_egtb', dict, '"online_egtb" must be a dictionary with indented keys followed by colons.']]
    for subsection in online_moves_sections:
        if subsection[0] not in online_moves_section:
            raise RuntimeError(
                f'Your config does not have required `engine` `online_moves` subsection `{subsection[0]}`.')

        if not isinstance(online_moves_section[subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `online_moves` subsection {subsection[2]}')

def _check_matchmaking_types_sections(matchmaking_types_section: dict) -> None:
    matchmaking_types_sections = [
        ['tc', str, '"tc" must be a string in initial_minutes+increment_seconds format.'],
        ['rated', bool, '"rated" must be a bool.'],
        ['variant', str, '"variant" must be a variant name from "https://lichess.org/variant".'],
        ['multiplier', int, '"multiplier" must be an integer.'],
        ['weight', int, '"weight" must be an integer.'],
        ['min_rating_diff', int, '"min_rating_diff" must be an integer.'],
        ['max_rating_diff', int, '"max_rating_diff" must be an integer.']]
    for matchmaking_type, matchmaking_options in matchmaking_types_section.items():
        if not isinstance(matchmaking_options, dict):
            raise TypeError(f'`matchmaking` `types` subsection "{matchmaking_type}" must be a dictionary with '
                            'indented keys followed by colons.')

        if 'tc' not in matchmaking_options:
            raise RuntimeError(f'Your matchmaking type "{matchmaking_type}" does not have required `tc` field.')

        for key, value in matchmaking_options.items():
            for subsection in matchmaking_types_sections:
                if key == subsection[0]:
                    if not isinstance(value, subsection[1]):
                        raise TypeError(f'`matchmaking` `types` `{matchmaking_type}` field {subsection[2]}')

                    break
            else:
                raise RuntimeError(f'Unknown field "{key}" in matchmaking type "{matchmaking_type}".')

    
def _init_lists(config: dict) -> None:
    if 'whitelist' in config:
        if not isinstance(config['whitelist'], list):
            raise TypeError('If uncommented, "whitelist" must be a list of usernames.')

        config['whitelist'] = [username.lower() for username in config['whitelist']]

    if 'blacklist' in config:
        if not isinstance(config['blacklist'], list):
            raise TypeError('If uncommented, "blacklist" must be a list of usernames.')

        config['blacklist'] = [username.lower() for username in config['blacklist']]


def _init_engines(engine_section: dict) -> None:
    if not os.path.isdir(engine_section['dir']):
        raise RuntimeError(f'Your engine directory "{engine_section["dir"]}" is not a directory.')

    engine_section['path'] = os.path.join(engine_section['dir'], engine_section['name'])

    if not os.path.isfile(engine_section['path']):
        raise RuntimeError(f'The engine "{engine_section["path"]}" file does not exist.')

    if not os.access(engine_section['path'], os.X_OK):
        raise RuntimeError(f'The engine "{engine_section["path"]}" doesnt have execute (x) permission. '
                           f'Try: chmod +x {engine_section["path"]}')

    if engine_section['variants']['enabled']:
        if not os.path.isdir(engine_section['variants']['dir']):
            raise RuntimeError(f'Your variants engine directory "{engine_section["variants"]["dir"]}" '
                               'is not a directory.')

        engine_section['variants']['path'] = os.path.join(
            engine_section['variants']['dir'],
            engine_section['variants']['name'])

        if not os.path.isfile(engine_section['variants']['path']):
            raise RuntimeError(f'The variants engine "{engine_section["variants"]["path"]}" file does not exist.')

        if not os.access(engine_section['variants']['path'], os.X_OK):
            raise RuntimeError(f'The variants engine "{engine_section["variants"]["path"]}" doesnt have execute '
                               f'(x) permission. Try: chmod +x {engine_section["variants"]["path"]}')


def _check_egtb(engine_section: dict) -> None:
    if engine_section['syzygy']['enabled']:
        for path in engine_section['syzygy']['paths']:
            if not os.path.isdir(path):
                raise RuntimeError(f'Your syzygy directory "{path}" is not a directory.')

    if engine_section['gaviota']['enabled']:
        for path in engine_section['gaviota']['paths']:
            if not os.path.isdir(path):
                raise RuntimeError(f'Your gaviota directory "{path}" is not a directory.')


def _init_opening_books(config: dict) -> None:
    if config['engine']['opening_books']['enabled']:
        for key, book_list in config['engine']['opening_books']['books'].items():
            if not isinstance(book_list, list):
                raise TypeError(f'The `engine: opening_books: books: {key}` section must be a '
                                'list of book names or commented.')

            for book in book_list:
                if book not in config['books']:
                    raise RuntimeError(f'The book "{book}" is not defined in the books section.')
                if not os.path.isfile(config['books'][book]):
                    raise RuntimeError(f'The book "{book}" at "{config["books"][book]}" does not exist.')

            config['engine']['opening_books']['books'][key] = {book: config['books'][book] for book in book_list}

def _get_version() -> str:
    try:
        output = subprocess.check_output(['git', 'show', '-s', '--date=format:%Y%m%d',
                                         '--format=%cd', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_date = output.decode('utf-8').strip()
        output = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_SHA = output.decode('utf-8').strip()[:7]
        return f'{commit_date}-{commit_SHA}'
    except (FileNotFoundError, subprocess.CalledProcessError):
        return __version__
