from optparse import OptionParser
from collections import namedtuple
from kitir import *

log = logging.getLogger('conversable.converse')

conversable_dir = this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(conversable_dir, 'data')
sample_data_name = 'sample.json'
sample_data_source = os.path.join(data_dir, sample_data_name)

ConversePair = namedtuple('ConversePair', 'a b')
ConverseMap = namedtuple('ConverseMap', 'phrases words characters')


class TranslateDirectionEnum:
    a_to_b = 'ab'
    b_to_a = 'ba'


class ConverseGroup(object):
    def __init__(self, **kwargs) -> None:

        self.phrases = kwargs.get('phrases', [])
        self.words = kwargs.get('words', [])
        self.characters = kwargs.get('characters', [])

        if 'json' in kwargs:
            self.load_group_json(kwargs['json'])
        if 'dict' in kwargs:
            self.update_group(kwargs['dict'])
        if 'data' in kwargs:
            self.update_group(kwargs['data'])

    def load_group_json(self, path_to_group_json):
        data = utils.read_json(path_to_group_json)
        self.update_group(data)

    def update_group(self, data):
        _new_phrases = data.get('phrases', [])
        _new_words = data.get('words', [])
        _new_characters = data.get('characters', [])

        log.debug('updating group with new pairs: phrases={} words={} characters={}'.format(
            len(_new_phrases), len(_new_words), len(_new_characters)))

        self.phrases.extend(_new_phrases)
        self.words.extend(_new_words)
        self.characters.extend(_new_characters)

        log.debug('updating complete, current count: phrases={} words={} characters={}'.format(
            len(_new_phrases), len(_new_words), len(_new_characters)))

    def create_map(self, direction):
        phrases = self._create_map_for_collection(direction, self.phrases)
        words = self._create_map_for_collection(direction, self.words)
        characters = self._create_map_for_collection(direction, self.characters)
        return ConverseMap(phrases, words, characters)

    @staticmethod
    def _create_map_for_collection(direction, collection):
        result_map = {}
        for pair in collection:
            if direction == TranslateDirectionEnum.a_to_b:
                key, value = pair
            else:
                value, key = pair
            result_map[key] = value
        return result_map


class Translator(object):

    def __init__(self, group, direction=TranslateDirectionEnum.a_to_b) -> None:
        assert isinstance(group, ConverseGroup)
        assert direction in (TranslateDirectionEnum.a_to_b, TranslateDirectionEnum.b_to_a)
        self.direction = direction
        self.group = group
        self.map = group.create_map(direction)

    def get_best_translation_for_segment(self, segment):
        """
        finds the best available option for the current text segment.

        go through the collections in order phrases > words > characters
        if any key in the collection matches the segment, then use that.
        :param segment:
        :return:
        """

        def sort_by_key_len(kv):
            return len(kv[0])

        def segment_matches_key(s, k):
            return bool(s[:len(k)].lower() == k)

        for key, value in sorted(self.map.phrases.items(), key=sort_by_key_len, reverse=True):
            if segment_matches_key(segment, key):
                return key, value

        for key, value in sorted(self.map.words.items(), key=sort_by_key_len, reverse=True):
            if segment_matches_key(segment, key):
                return key, value

        for key, value in sorted(self.map.characters.items(), key=sort_by_key_len, reverse=True):
            if segment_matches_key(segment, key):
                return key, value

        return None  # no matches

    def translate(self, text):
        """
        parses the text, and if it finds any segments to translate will change those segments.
        :param text:
        :return:
        """
        translation = ''  # the final translation (or result, as also non translated text will be here)
        current_index = 0  # keep track of where we are parsing the text

        while current_index < len(text):
            # as long as we still have text to parse, lets look for any segments from the current index to the end
            result = self.get_best_translation_for_segment(text[current_index:])

            if result is None:
                # if we do not have a translation for the segment just use the current text
                new_text = text[current_index]
                current_index += 1
            else:
                # if we do have a translation then lets use it
                key, value = result
                new_text = value

                # check if we need to capitalize the first letter
                if text[current_index].isupper():
                    new_text = new_text[0].upper() + new_text[1:]

                # adjust the text index base on the length of the segment we found (and translated)
                current_index += len(key)

            # add new text to translation (results)
            translation += new_text

        return translation


def translate_text(converse_file, text_to_translate, **kwargs):
    group = ConverseGroup(json=converse_file)
    t = Translator(group, **kwargs)
    return t.translate(text_to_translate)


def translate_file(converse_file, text_to_translate=None, input_file=None, output_file=None, **kwargs):
    assert text_to_translate is not None and input_file is not None, 'only one input method'
    group = ConverseGroup(json=converse_file)
    t = Translator(group, **kwargs)
    if text_to_translate is None:
        text_to_translate = utils.read_file(input_file, as_str=True)
    result = t.translate(text_to_translate)
    if output_file is not None:
        utils.write_file(output_file, result)


def sample_translate(text):
    """
    Using sample language for translation
    >>> sample_translate('how do you do captain?')
    "'ow diya do cap'n?"

    >>> sample_translate("this is a good example wouldn't you say?")
    "dis is a good example wouldn'd you say?"

    >>> sample_translate("Here, this is my favorite.")
    "'ere, dis is ma favoride."

    :param text: some English text.
    :return: some accented text
    """
    group = ConverseGroup(json=sample_data_source)
    t = Translator(group)
    return t.translate(text)


def main(args):
    parser = OptionParser()
    # logging
    parser.add_option('--log-level', '--ll', dest='log_level', help='Log Level (0=info, 1=debug, 2=trace)')
    parser.add_option('--log-file', '--lf', dest='log_file', help='Log file',
                      default=init_working_directory + '/conversable.log')
    # data
    parser.add_option('--converse-file', '-c', dest='converse_file',
                      help='Converse File (.json) default: data/sample.json')
    parser.add_option('--input-file', '-i', dest='input_file',
                      help='read from input file (.txt) instead of args')
    parser.add_option('--output-file', '-o', dest='output_file',
                      help='write to output file (.txt) instead of STDOUT')
    parser.add_option('--direction', '-d', dest='direction',
                      help='translate direction (ab or ba) default: ab', default='ab')
    options, args = parser.parse_args(args)

    utils.logging_setup(log_level=options.log_level, log_file=options.log_file)

    converse_file = options.converse_file
    if not converse_file:
        converse_file = sample_data_source

    if args:
        input_text = ' '.join(args)
    else:
        input_text = None

    if input_text is None and not options.input_file:
        parser.error('no input method provided')

    if input_text is not None and options.input_file:
        parser.error('only use one input method')

    if input_text is not None:
        return translate_text(
            converse_file=converse_file,
            text_to_translate=input_text,
            direction=options.direction
        )
    else:
        return translate_file(
            converse_file=converse_file,
            input_file=options.input_file,
            output_file=options.output_file,
            direction=options.direction
        )


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
