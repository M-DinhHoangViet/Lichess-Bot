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
            CONFIG = yaml.safe_load(yml_input)
        except Exception as e:
            print(f'There appears to be a syntax problem with your {config_path}', file=sys.stderr)
            raise e

    if 'LICHESS_BOT_TOKEN' in os.environ:
        CONFIG['token'] = os.environ['LICHESS_BOT_TOKEN']

    # [section, type, error message]
    sections = [
        ['token', str, 'Section `token` must be a string wrapped in quotes.'],
        ['engine', dict, 'Section `engine` must be a dictionary with indented keys followed by colons.'],
        ['challenge', dict, 'Section `challenge` must be a dictionary with indented keys followed by colons.'],
        ['matchmaking', dict, 'Section `matchmaking` must be a dictionary with indented keys followed by colons.'],
        ['messages', dict, 'Section `messages` must be a dictionary with indented keys followed by colons.'],
        ['books', dict, 'Section `books` must be a dictionary with indented keys followed by colons.']]
    for section in sections:
        if section[0] not in CONFIG:
            raise RuntimeError(f'Your {config_path} does not have required section `{section[0]}`.')

        if not isinstance(CONFIG[section[0]], section[1]):
            raise TypeError(section[2])

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
        if subsection[0] not in CONFIG['engine']:
            raise RuntimeError(f'Your {config_path} does not have required `engine` subsection `{subsection[0]}`.')

        if not isinstance(CONFIG['engine'][subsection[0]], subsection[1]):
            raise TypeError(f' `engine`subsection {subsection[2]}')

    syzygy_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['paths', list, '"paths" must be a list.'],
        ['max_pieces', int, '"max_pieces" must be an integer.'],
        ['instant_play', bool, '"instant_play" must be a bool.']]
    for subsection in syzygy_sections:
        if subsection[0] not in CONFIG['engine']['syzygy']:
            raise RuntimeError(f'Your {config_path} does not have required '
                               f'`engine` `syzygy` subsection `{subsection[0]}`.')

        if not isinstance(CONFIG['engine']['syzygy'][subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `syzygy` subsection {subsection[2]}')

    gaviota_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['paths', list, '"paths" must be a list.'],
        ['max_pieces', int, '"max_pieces" must be an integer.']]
    for subsection in gaviota_sections:
        if subsection[0] not in CONFIG['engine']['gaviota']:
            raise RuntimeError(f'Your {config_path} does not have required '
                               f'`engine` `gaviota` subsection `{subsection[0]}`.')

        if not isinstance(CONFIG['engine']['gaviota'][subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `gaviota` subsection {subsection[2]}')

    variants_sections = [
        ['enabled', bool, '"enabled" must be a bool.'],
        ['dir', str, '"dir" must be a string wrapped in quotes.'],
        ['name', str, '"name" must be a string wrapped in quotes.'],
        ['ponder', bool, '"ponder" must be a bool.'],
        ['uci_options', dict, '"uci_options" must be a dictionary with indented keys followed by colons.']]
    for subsection in variants_sections:
        if subsection[0] not in CONFIG['engine']['variants']:
            raise RuntimeError(f'Your {config_path} does not have required '
                               f'`engine` `variants` subsection `{subsection[0]}`.')

        if not isinstance(CONFIG['engine']['variants'][subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `variants` subsection {subsection[2]}')

    online_moves_sections = [
        ['opening_explorer', dict, '"opening_explorer" must be a dictionary with indented keys followed by colons.'],
        ['chessdb', dict, '"chessdb" must be a dictionary with indented keys followed by colons.'],
        ['lichess_cloud', dict, '"lichess_cloud" must be a dictionary with indented keys followed by colons.'],
        ['online_egtb', dict, '"online_egtb" must be a dictionary with indented keys followed by colons.']]
    for subsection in online_moves_sections:
        if subsection[0] not in CONFIG['engine']['online_moves']:
            raise RuntimeError(f'Your {config_path} does not have required '
                               f'`engine` `online_moves` subsection `{subsection[0]}`.')

        if not isinstance(CONFIG['engine']['online_moves'][subsection[0]], subsection[1]):
            raise TypeError(f'`engine` `online_moves` subsection {subsection[2]}')

    matchmaking_types_sections = [
        ['tc', str, '"tc" must be a string in initial_minutes+increment_seconds format.'],
        ['rated', bool, '"rated" must be a bool.'],
        ['variant', str, '"variant" must be a variant name from "https://lichess.org/variant".'],
        ['multiplier', int, '"multiplier" must be an integer.'],
        ['weight', int, '"weight" must be an integer.'],
        ['min_rating_diff', int, '"min_rating_diff" must be an integer.'],
        ['max_rating_diff', int, '"max_rating_diff" must be an integer.']]
    for matchmaking_type, matchmaking_options in CONFIG['matchmaking']['types'].items():
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

    if 'whitelist' in CONFIG:
        if not isinstance(CONFIG['whitelist'], list):
            raise TypeError('If uncommented, "whitelist" must be a list of usernames.')

        CONFIG['whitelist'] = [username.lower() for username in CONFIG['whitelist']]

    if 'blacklist' in CONFIG:
        if not isinstance(CONFIG['blacklist'], list):
            raise TypeError('If uncommented, "blacklist" must be a list of usernames.')

        CONFIG['blacklist'] = [username.lower() for username in CONFIG['blacklist']]

    if not os.path.isdir(CONFIG['engine']['dir']):
        raise RuntimeError(f'Your engine directory "{CONFIG["engine"]["dir"]}" is not a directory.')

    CONFIG['engine']['path'] = os.path.join(CONFIG['engine']['dir'], CONFIG['engine']['name'])

    if not os.path.isfile(CONFIG['engine']['path']):
        raise RuntimeError(f'The engine "{CONFIG["engine"]["path"]}" file does not exist.')

    if not os.access(CONFIG['engine']['path'], os.X_OK):
        raise RuntimeError(f'The engine "{CONFIG["engine"]["path"]}" doesnt have execute (x) permission. '
                           f'Try: chmod +x {CONFIG["engine"]["path"]}')

    if CONFIG['engine']['variants']['enabled']:
        if not os.path.isdir(CONFIG['engine']['variants']['dir']):
            raise RuntimeError(f'Your variants engine directory "{CONFIG["engine"]["variants"]["dir"]}" '
                               'is not a directory.')

        CONFIG['engine']['variants']['path'] = os.path.join(
            CONFIG['engine']['variants']['dir'],
            CONFIG['engine']['variants']['name'])

        if not os.path.isfile(CONFIG['engine']['variants']['path']):
            raise RuntimeError(f'The variants engine "{CONFIG["engine"]["variants"]["path"]}" file does not exist.')

        if not os.access(CONFIG['engine']['variants']['path'], os.X_OK):
            raise RuntimeError(f'The variants engine "{CONFIG["engine"]["variants"]["path"]}" doesnt have execute '
                               f'(x) permission. Try: chmod +x {CONFIG["engine"]["variants"]["path"]}')

    if CONFIG['engine']['syzygy']['enabled']:
        for path in CONFIG['engine']['syzygy']['paths']:
            if not os.path.isdir(path):
                raise RuntimeError(f'Your syzygy directory "{path}" is not a directory.')

    if CONFIG['engine']['gaviota']['enabled']:
        for path in CONFIG['engine']['gaviota']['paths']:
            if not os.path.isdir(path):
                raise RuntimeError(f'Your gaviota directory "{path}" is not a directory.')

    if CONFIG['engine']['opening_books']['enabled']:
        for key, book_list in CONFIG['engine']['opening_books']['books'].items():
            if not isinstance(book_list, list):
                raise TypeError(f'The `engine: opening_books: books: {key}` section must be a '
                                'list of book names or commented.')

            for book in book_list:
                if book not in CONFIG['books']:
                    raise RuntimeError(f'The book "{book}" is not defined in the books section.')
                if not os.path.isfile(CONFIG['books'][book]):
                    raise RuntimeError(f'The book "{book}" at "{CONFIG["books"][book]}" does not exist.')

            CONFIG['engine']['opening_books']['books'][key] = {book: CONFIG['books'][book] for book in book_list}

    try:
        output = subprocess.check_output(['git', 'show', '-s', '--date=format:%Y%m%d',
                                         '--format=%cd', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_date = output.decode('utf-8').strip()
        output = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_SHA = output.decode('utf-8').strip()[:7]
        CONFIG['version'] = f'{commit_date}-{commit_SHA}'
    except (FileNotFoundError, subprocess.CalledProcessError):
        CONFIG['version'] = __version__

    return CONFIG
