import pytest
from kitir import *
from conversable import converse

conversable_dir = this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(conversable_dir, 'data')

utils.logging_setup()

sample_text = [
    # [
    #     "Captain, I'm glad you got my message. I been thinking on this mission. They took the prince, they criminals. They kidnap and they trying to rob our ships. Maybe they also liars. Maybe they trick us. Maybe they make up the story. Maybe no kingdom in east, maybe never was.",
    #     "Cap'n, I'ma glad you god ma message. I been dinkin on dis mission. Dey dook da prince, dey criminals. Dey kidnap and dey drying do rob our ships. Maybe dey also liars. Maybe dey drick us. Maybe dey make up da sdory. Maybe no kingdom in easd, maybe never was."
    # ],
    [
        "how do you do captain?",
        "'ow diya do cap'n?"
    ],
    [
        "this is a good example wouldn't you say?",
        "dis is a good example wouldn'd you say?"
    ],
    [
        "Here, this is my favorite.",
        "'ere, dis is ma favoride."
    ],
    # [
    #     "Here is the report captain. Everything is written down for you, down to the last screw. I have made a notation for each tool and supplies what they are for, and you can also find the tools and supplies referenced under each device or ship part. All in all sir, we are in good stock, but since we expect a long journy and i suspect unexpected surprises. Then I recomend we double the standard supply ammounts for everything to make sure we have enough on board, and that we should tripple the type-C screws, those are used for hull repairs, and that would be the last thing we want to run out of sir.",
    #     ""
    # ]
]


class TestSample:
    data_name = 'sample.json'
    data_source = os.path.join(data_dir, data_name)

    # sample_data = utils.read_json(data_source)
    sample_group = converse.ConverseGroup(json=data_source)

    @pytest.mark.parametrize(
        argnames=['phrase_a', 'phrase_b'],
        argvalues=sample_group.phrases)
    def test_phrases_ab(self, phrase_a, phrase_b):
        translator = converse.Translator(self.sample_group, converse.TranslateDirectionEnum.a_to_b)
        result = translator.translate(phrase_a)
        assert result == phrase_b

    @pytest.mark.parametrize(
        argnames=['word_a', 'word_b'],
        argvalues=sample_group.words)
    def test_words_ab(self, word_a, word_b):
        translator = converse.Translator(self.sample_group, converse.TranslateDirectionEnum.a_to_b)
        result = translator.translate(word_a)
        assert result == word_b

    @pytest.mark.parametrize(
        argnames=['character_a', 'character_b'],
        argvalues=sample_group.characters)
    def test_characters_ab(self, character_a, character_b):
        translator = converse.Translator(self.sample_group, converse.TranslateDirectionEnum.a_to_b)
        result = translator.translate(character_a)
        assert result == character_b

    @pytest.mark.parametrize(
        argnames=['text_a', 'text_b'],
        argvalues=sample_text)
    def test_sample_text(self, text_a, text_b):
        translator = converse.Translator(self.sample_group, converse.TranslateDirectionEnum.a_to_b)
        result = translator.translate(text_a)
        assert result == text_b
